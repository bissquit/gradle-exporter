import pytest
import json
from gradle_server_exporter import \
    get_data, \
    validate_json, \
    parse_args, \
    generate_metrics


class MockResponse:
    def __init__(self, text, status, headers=None):
        self._text = text
        self.status = status
        self.headers = headers

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
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
    # client = GradleWebClient()
    mock_resp = MockResponse(json.dumps(json_data), 200)
    mocker.patch('aiohttp.ClientSession.get', return_value=mock_resp)
    resp = await get_data(url="http://localhost")
    assert resp == json_data

    json_data = {}
    # client = GradleWebClient()
    mock_resp = MockResponse(json.dumps(json_data), 503)
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
