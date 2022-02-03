import os
import json
import aiohttp
import validators
import logging

logging.basicConfig(level=os.getenv("LOG_LEVEL", logging.INFO), format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def get_data(url):
    # json.loads() requires str beginning with a JSON document
    json_body = json.loads('{}')

    async with aiohttp.ClientSession() as client:
        try:
            async with client.get(url) as r:
                status = r.status
                logger.info(f'Requesting Gradle url {url}')
                logger.debug(f'Full response: {r}')
                if status == 200:
                    json_body = await r.json()
                else:
                    logger.error(f'Cannot request Gradle url {url}! Response status: {status}')
        except aiohttp.ClientError as error:
            logger.error(f'Connection error to url {url}: {error}')

    return json_body


def validate_json(json_data):
    """
    :param json_data: any json
    :return:

    Example of expected json format received from Gradle server:
    {
      "pending" : 0,
      "requested" : 0,
      "ageMins" : 0,
      "requestWaitTimeSecs" : 0,
      "incomingRate1m" : 0.03221981766544038,
      "incomingRate5m" : 0.02219163413405735,
      "incomingRate15m" : 0.021373141599789678,
      "processingRate1m" : 0.03399783025186821,
      "processingRate5m" : 0.022374841163558885,
      "processingRate15m" : 0.021459615070953553
    }

    Params validation may be added in the future
    """
    if json_data == '{}':
        logger.error('Empty json response from server! No metrics will be produced')
    return None


def generate_metrics(json_data, url):
    metrics_str = ''
    for k, v in json_data.items():
        metrics_str += f'gradle_ingest_queue_{k}{{url="{url}"}} {v}\n'
    return metrics_str


class HandleFileData:
    def __init__(self, path):
        self.path = path

    def return_urls_list(self):
        strs_list = self.read_file(path=self.path)
        urls_list = self.normalize_urls_list(strs_list=strs_list)
        return urls_list

    def normalize_urls_list(self, strs_list):
        invalid_urls_counter = 0
        urls_list = []

        for line in strs_list:
            line_striped = line.strip()
            if line_striped == '':
                pass
            # ignore line in the list if it doesn't look like a valid url
            elif self.normalize_url(url=line_striped) is False:
                invalid_urls_counter += 1
            else:
                urls_list.append(line_striped)

        if invalid_urls_counter > 0:
            logger.warning(f'{invalid_urls_counter} url(s) has been removed due to invalid format. Check file {self.path}')
            logger.info('Read more about url format at https://validators.readthedocs.io/en/latest/#module-validators.url')

        return urls_list

    @staticmethod
    def read_file(path):
        try:
            logger.info(f'Reading file {path}')
            with open(path) as file:
                # Return all lines in the file, as a list where each line is an item
                strs_list = file.readlines()
        except OSError as error:
            logger.critical(f'Could not read file {path}: {error}')
            strs_list = []
        return strs_list

    @staticmethod
    def normalize_url(url):
        result = True
        if not validators.url(url):
            logger.warning(f'String {url} is not a valid url. Skipping...')
            result = False
        return result
