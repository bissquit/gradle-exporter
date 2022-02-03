import os
import sys
from aiohttp import web
import asyncio
import logging
import argparse
from handler import \
    HandleFileData, \
    get_data, \
    generate_metrics

logging.basicConfig(level=os.getenv("LOG_LEVEL", logging.INFO), format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_args():
    # You may either use command line argument or env variables
    parser = argparse.ArgumentParser(prog='gradle_server_exporter',
                                     description='Prometheus exporter for Gradle Enterprise Server ')
    parser.add_argument('-f', '--file',
                        default=os.getenv("APP_FILE_PATH", ''),
                        type=str,
                        help='Absolute path to file. Each line is url link (default: Empty string)')
    parser.add_argument('-p', '--port',
                        default=os.getenv("APP_PORT", 8080),
                        type=int,
                        help='Port to be listened (default: 8080)')
    parser.add_argument('-t', '--time',
                        default=os.getenv("APP_CHECK_INTERVAL", 60),
                        type=int,
                        help='Default time range in seconds to check metrics (default: 60)')
    return parser.parse_args()


async def start_background_tasks(app):
    app['gradle_metrics_checker'] = asyncio.create_task(metrics_checker(app))


async def cleanup_background_tasks(app):
    app['gradle_metrics_checker'].cancel()
    await app['gradle_metrics_checker']


async def metrics_checker(app):
    if not app['urls_list']:
        logging.critical('Empty urls list is accepted. Nothing to check. Exiting...')
        sys.exit(1)

    while True:
        app['metrics_str'] = ''
        for url in app['urls_list']:
            json_data = await get_data(url=url)
            app['metrics_str'] += generate_metrics(json_data=json_data,
                                                   url=url)
        await asyncio.sleep(app['args'].time)


# https://docs.aiohttp.org/en/stable/web_quickstart.html#handler
# A request handler must be a coroutine that accepts
# a Request instance as its only parameter...
async def return_metrics(request):
    # ... and returns a Response instance
    return web.Response(text=request.app['metrics_str'])


def main():
    args = parse_args()
    app = web.Application()
    # For storing global-like variables, feel free to save them in an Application instance
    app['metrics_str'] = 'Initialization'
    app['args'] = args
    app['urls_list'] = HandleFileData(args.file).return_urls_list()
    app.add_routes([web.get('/metrics', return_metrics)])
    # https://docs.aiohttp.org/en/stable/web_advanced.html#background-tasks
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    web.run_app(app, port=args.port)


if __name__ == "__main__":
    main()
