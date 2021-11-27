import logging
import argparse
import datetime
from bot import Bot

logging.basicConfig(
    format='%(asctime)s: %(funcName)s: %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def parseArgs():
    parser = argparse.ArgumentParser(
        description='login callback and save settings demo')
    parser.add_argument('-s', '--settings',
                        dest='settings_file_path', type=str, required=True)
    parser.add_argument('-c', '--credentials',
                        dest='credentials_file_path', type=str, required=True)
    parser.add_argument('-debug', '--debug', action='store_true')
    return parser.parse_args()


def main():
    args = parseArgs()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    bot = Bot(args.credentials_file_path, args.settings_file_path)

    # Show when login expires
    cookie_expiry = bot().cookie_jar.auth_expires
    logger.info('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(
        cookie_expiry).strftime('%Y-%m-%d at %H:%M:%S')))


if __name__ == '__main__':
    main()
