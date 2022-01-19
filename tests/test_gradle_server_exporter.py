import pytest
import aiohttp
import json
import yarl
from multidict import CIMultiDictProxy, CIMultiDict
from gradle_server_exporter import \
    get_data, \
    validate_json, \
    parse_args, \
    generate_metrics


class MockResponse:
    def __init__(self, text, status, error_code=None, headers=None):
        self._text = text
        self.status = status
        self.error_code = error_code
        self.headers = headers

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        # MultiDictProxy - HTTP Headers and URL query string require specific data structure: multidict.
        # It behaves mostly like a dict but may have several values for the same key.
        #
        # CIMultiDictProxy - Case insensitive version of MultiDictProxy
        # https://docs.aiohttp.org/en/v0.14.4/multidict.html
        headers = CIMultiDictProxy(CIMultiDict())
        # RequestInfo - a data class with request URL and headers from ClientRequest object,
        # available as ClientResponse.request_info attribute.
        # https://docs.aiohttp.org/en/stable/client_reference.html#requestinfo
        #
        # yarl.URL Represents URL as:
        # [scheme:]//[user[:password]@]host[:port][/path][?query][#fragment]
        # https://yarl.readthedocs.io/en/stable/api.html#yarl.URL
        request_info = aiohttp.RequestInfo(yarl.URL(),
                                           'GET',
                                           headers=headers)
        # based on https://docs.aiohttp.org/en/stable/client_reference.html#hierarchy-of-exceptions
        if self.error_code == 1:
            raise aiohttp.ClientResponseError(request_info, ())
        elif self.error_code == 2:
            raise aiohttp.ClientConnectionError
        elif self.error_code == 3:
            raise aiohttp.ClientPayloadError
        elif self.error_code == 4:
            raise aiohttp.InvalidURL(url='http://fake_url')
        return self

    async def text(self):
        return self._text

    async def json(self):
        return json.loads(self._text)


@pytest.mark.asyncio
async def test_get_data(mocker):
    json_data = {
      "pending": 0,
      "requested": 0,
      "ageMins": 0,
      "requestWaitTimeSecs": 0,
      "incomingRate1m": 0.07325439431321024,
      "incomingRate5m": 0.04505484144595491,
      "incomingRate15m": 0.020544298197747727,
      "processingRate1m": 0.07448036802367386,
      "processingRate5m": 0.04546168132054522,
      "processingRate15m": 0.02061971630595855
    }
    mock_resp = MockResponse(text=json.dumps(json_data),
                             status=200)
    mocker.patch('aiohttp.ClientSession.get', return_value=mock_resp)
    resp = await get_data(url="http://localhost")
    assert resp == json_data

    mock_resp = MockResponse(text=json.dumps({}),
                             status=503)
    mocker.patch('aiohttp.ClientSession.get', return_value=mock_resp)
    resp = await get_data(url="http://localhost")
    assert resp == {}

    # emulate client errors
    for error in range(1, 5):
        print(error)
        mock_resp = MockResponse(text=json.dumps({}),
                                 status=None,
                                 error_code=error)
        mocker.patch('aiohttp.ClientSession.get', return_value=mock_resp)
        resp = await get_data(url="http://localhost")
        assert resp == {}


# dummy test for None result function
def test_validate_json():
    # client = GradleWebClient()
    result = validate_json('{}')
    assert result is None


def test_parse_args():
    print(parse_args())
    pass


def test_generate_metrics():
    print(generate_metrics(json.loads('{}')))
    pass
