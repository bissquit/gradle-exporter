import pytest
import aiohttp
import json
import yarl
import io
from multidict import CIMultiDictProxy, CIMultiDict
from handler import \
    get_data, \
    validate_json, \
    generate_metrics, \
    HandleFileData


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


# emulates incorrect directory path
class MockOSReadFile:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise OSError


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


def test_generate_metrics():
    fake_url_str = 'http://fake.url/ingest-queue'
    json_data = {
        "pending": 0,
        "requested": 0
    }
    result = generate_metrics(json_data=json_data,
                              url=fake_url_str)
    assert result == f'gradle_ingest_queue_pending{{url="{fake_url_str}"}} 0\ngradle_ingest_queue_requested{{url="{fake_url_str}"}} 0\n'

    json_data = json.loads('{}')
    result = generate_metrics(json_data=json_data,
                              url=fake_url_str)
    assert result == ''


def test_normalize_url():
    invalid_urls_list = [
        'http:/google.com',
        'httpa://google.com',
        'htt:/google.com',
        'http//google.com',
        'ttp://google.com',
        'http://google',
        'http://google.com:44a',
        'google.com'
    ]

    for url in invalid_urls_list:
        result = HandleFileData('').normalize_url(url=url)
        assert result is False

    valid_urls_list = [
        'http://google.com',
        'https://google.com',
        'http://google.com:443',
        'http://google.com/path',
        'http://google.com:443/path?'
    ]

    for url in valid_urls_list:
        result = HandleFileData('').normalize_url(url=url)
        assert result is True


@pytest.mark.asyncio
def test_read_file(mocker):
    fake_path_str = '/fake/path'

    file_data_str = 'http://google.ru \nhttps://ya.ru\n'
    # creates file-like obj in memory with appropriate methods like read() and write()
    file = io.StringIO(file_data_str)
    mocker.patch("builtins.open", return_value=file)
    client = HandleFileData('').read_file(fake_path_str)
    assert client == ['http://google.ru \n', 'https://ya.ru\n']

    file_data_str = '\n\n'
    file = io.StringIO(file_data_str)
    mocker.patch("builtins.open", return_value=file)
    client = HandleFileData('').read_file(fake_path_str)
    assert client == ['\n', '\n']

    file_data_str = ''
    file = io.StringIO(file_data_str)
    mocker.patch("builtins.open", return_value=file)
    client = HandleFileData('').read_file(fake_path_str)
    assert client == []

    resp = MockOSReadFile(fake_path_str)
    mocker.patch("builtins.open", return_value=resp)
    client = HandleFileData('').read_file(fake_path_str)
    assert client == []


def test_normalize_urls_list():
    file_data_str = [
        'htt://google.ru \n',
        'https://ya.ru\n',
        '\n',
        ' \n',
        '  \n',
        '\n ',
        '\n  ',
        '\n\n',
        '\n\n ',
        '\n\n  ',
        '   ',
        'google.ru',
        '  http://site.tld '
    ]
    result = HandleFileData('').normalize_urls_list(strs_list=file_data_str)
    assert result == ['https://ya.ru', 'http://site.tld']
