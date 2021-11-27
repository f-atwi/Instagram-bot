import json
import codecs
import logging
import logging
from pathlib import Path
from instagram_private_api import (
    Client, ClientError, ClientLoginError,
    ClientCookieExpiredError, ClientLoginRequiredError)

logging.basicConfig(
    format='%(asctime)s: %(funcName)s: %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Bot:
    def __init__(self, credentials_file_path: Path, settings_file_path: Path):
        self.api = Bot._login(
            Path(credentials_file_path+'.json'), Path(settings_file_path))
    def __call__(self):
        return self.api
    def _to_json(python_object):
        if isinstance(python_object, bytes):
            return {'__class__': 'bytes',
                    '__value__': codecs.encode(python_object, 'base64').decode()}
        raise TypeError(repr(python_object) + ' is not JSON serializable')

    def _from_json(json_object):
        if '__class__' in json_object and json_object['__class__'] == 'bytes':
            return codecs.decode(json_object['__value__'].encode(), 'base64')
        return json_object

    def _onlogin_callback(api, new_settings_file):
        cache_settings = api.settings
        with open(new_settings_file, 'w') as outfile:
            json.dump(cache_settings, outfile, default=Bot._to_json)
            logging.info(f'SAVED: {new_settings_file}')

    def _load_credentials(credentials_file_path: Path) -> dict:
        if not Path.is_file(credentials_file_path):
            logger.error(f'Unable to find file: {credentials_file_path}')
            # exit()
        else:
            with open(credentials_file_path) as file_data:
                return json.load(file_data)

    def _load_settings(settings_file_path: Path):
        if not Path.is_file(settings_file_path):
            # settings file does not exist
            logger.warning(f'Unable to find file: {settings_file_path}')
            # login new
            return None
        else:
            with open(settings_file_path) as file_data:
                cached_settings = json.load(
                    file_data, object_hook=Bot._from_json)
            logger.info(
                f'Reusing settings: {settings_file_path}')
            return cached_settings

    def _login(credentials_file_path: Path, settings_file_path: Path):
        credentials = Bot._load_credentials(credentials_file_path)
        try:
            cached_settings = Bot._load_settings(settings_file_path)
            if not cached_settings:
                # login new
                return Client(
                    credentials['username'], credentials['password'],
                    on_login=lambda x: Bot._onlogin_callback(x, settings_file_path))
            else:
                device_id = cached_settings.get('device_id')
                # reuse auth settings
                return Client(
                    credentials['username'], credentials['password'],
                    settings=cached_settings)

        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
            logger.warning(
                f'ClientCookieExpiredError/ClientLoginRequiredError: {e}')
            # Login expired
            # Do relogin but use default ua, keys and such
            return Client(
                credentials['username'], credentials['password'],
                device_id=device_id,
                on_login=lambda x: Bot._onlogin_callback(x, settings_file_path))

        except ClientLoginError as e:
            logger.error(f'ClientLoginError {e}')
            # exit(9)
        except ClientError as e:
            logger.error(
                f'ClientError {e.msg} (Code: {e.code}, Response: {e.error_response})')
            # exit(9)
        except Exception as e:
            logger.error(f'Unexpected Exception: {e}')
            # exit(99)


def main():
    bot = Bot("credentials", "settings")
    pass


if __name__ == "__main__":
    main()
