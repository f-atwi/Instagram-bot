import json
import codecs
import datetime
import logging
import os.path
import logging
import argparse
from instagram_private_api import (
    Client, ClientError, ClientLoginError,
    ClientCookieExpiredError, ClientLoginRequiredError,
    __version__ as client_version)


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        print('SAVED: {0!s}'.format(new_settings_file))


def parseArgs():
    parser = argparse.ArgumentParser(description='login callback and save settings demo')
    parser.add_argument('-settings', '--settings', dest='settings_file_path', type=str, required=True)
    parser.add_argument('-c', '--credentials', dest='credentials_file_path', type=str, required=True)
    parser.add_argument('-debug', '--debug', action='store_true')
    return parser.parse_args()


def loginUsingSetting(args):
    credentials_file = args.credentials_file_path
    if not os.path.isfile(credentials_file):
        logger.error('Unable to find file: {0!s}'.format(credentials_file))
        exit()
    else:
        with open(credentials_file) as file_data:
            credentials = json.load(file_data)
        try:
            settings_file = args.settings_file_path
            if not os.path.isfile(settings_file):
                # settings file does not exist
                logger.warning('Unable to find file: {0!s}'.format(settings_file))

                # login new
                return Client(
                    credentials['username'], credentials['password'],
                    on_login=lambda x: onlogin_callback(x, args.settings_file_path))
            else:
                with open(settings_file) as file_data:
                    cached_settings = json.load(file_data, object_hook=from_json)
                logger.info('Reusing settings: {0!s}'.format(settings_file))

                device_id = cached_settings.get('device_id')
                # reuse auth settings
                return Client(
                    credentials['username'], credentials['password'],
                    settings=cached_settings)

        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
            logger.warning('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

            # Login expired
            # Do relogin but use default ua, keys and such
            return Client(
                credentials['username'], credentials['password'],
                device_id=device_id,
                on_login=lambda x: onlogin_callback(x, args.settings_file_path))

        except ClientLoginError as e:
            logger.error('ClientLoginError {0!s}'.format(e))
            exit(9)
        except ClientError as e:
            logger.error('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
            exit(9)
        except Exception as e:
            logger.error('Unexpected Exception: {0!s}'.format(e))
            exit(99)


def main():
    args = parseArgs()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    logger.info('Client version: {0}'.format(client_version))
    device_id = None
    api = loginUsingSetting(args)
    

    # Show when login expires
    cookie_expiry = api.cookie_jar.auth_expires
    logger.info('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%d at %H:%M:%S')))


logger = logging
logger_format = '%(asctime)s: %(funcName)s: %(levelname)s: %(message)s'
logger.basicConfig(format=logger_format, level=logging.INFO)



if __name__ == '__main__':
    main()

