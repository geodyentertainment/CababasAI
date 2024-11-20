import json
from json import JSONDecodeError
from os import mkdir
from os import path
from CababasBot.logger import get_traceback
from CababasBot.logger import PrefixedLogger

CONFIG_PATH = 'config'
default_logger = PrefixedLogger('CONFIG_MANAGER')

def create_folder(name: str, logger: PrefixedLogger | None = default_logger) -> tuple[bool, FileExistsError|Exception | None]:
    folder = f'{CONFIG_PATH}/{name}'
    try:
        mkdir(folder)
    except FileExistsError as e:
        return False, e
    except Exception as e:
        logger.error(f'Error creating directory "{name}":\n{get_traceback(e)}')
        return False, e
    return True, None


def create_file(name: str, content: str | None = '[]', logger: PrefixedLogger | None = default_logger) -> tuple[
    bool, FileExistsError|Exception | None]:
    file_path = f'{CONFIG_PATH}/{name}'
    try:
        with open(file=file_path, mode='x', encoding='utf-8') as file:
            file.write(content)
    except FileExistsError as e:
        return False, e
    except Exception as e:
        logger.error(f'Error creating file "{name}":\n{get_traceback(e)}')
        return False, e
    return True, None


def write_file(name: str, content: str | None = '[]', logger: PrefixedLogger | None = default_logger) -> tuple[
    bool, Exception | None]:
    try:
        file_path = f'{CONFIG_PATH}/{name}'
        with open(file=file_path, mode='w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        logger.error(f'Error creating file "{name}":\n{get_traceback(e)}')
        return False, e
    return True, None


def read_file(name: str, default_content: str | None = '[]', logger: PrefixedLogger | None = default_logger) -> str:
    file_path = f'{CONFIG_PATH}/{name}'
    try:
        if path.exists(file_path):
            with open(file=file_path, mode='r', encoding='utf-8') as file:
                return file.read()
    except Exception as e:
        logger.error(f'Error creating file "{name}": {str(e)}\n{get_traceback(e)}')
        return default_content


class Settings:
    SEC_DISCORD = 'discord'
    KEY_ENABLED = 'enabled'
    KEY_MANAGERS = 'managers'
    KEY_COMMANDS_WHITELIST = 'commands_whitelisted_guilds'
    KEY_AI_WHITELIST = 'ai_whitelisted_guilds'

    SEC_AI = 'ai'
    KEY_HISTORY_MEM = 'history_memory'
    KEY_TEMP = 'temperature'
    KEY_TOP_P = 'top_p'
    KEY_LOGIT_BIAS = 'logit_bias'
    KEY_SEED = 'seed'
    KEY_MAX_PROMPT_TOK = 'get_max_prompt_tokens'
    KEY_MAX_COMP_TOK = 'max_completion_tokens'
    KEY_FREQ_PENALTY = 'frequency_penalty'
    KEY_PRES_PENALTY = 'presence_penalty'

    SAVE_NAME = 'settings.json'
    SAVE_DEFAULT: dict[str, dict[str, any]] = {
        SEC_DISCORD: {
            KEY_ENABLED: True,
            KEY_MANAGERS: {
                'Geody': 775117392644407296,
                'Wallibe': 1164735044200435734
            },
            KEY_COMMANDS_WHITELIST: {},
            KEY_AI_WHITELIST: {},
        },
        SEC_AI: {
            KEY_ENABLED: False,
            KEY_HISTORY_MEM: 11,
            KEY_TEMP: 0.79,
            KEY_TOP_P: 1,
            KEY_LOGIT_BIAS: {'1734': -100},
            KEY_SEED: 572875094,
            KEY_MAX_PROMPT_TOK: 40,
            KEY_MAX_COMP_TOK: 20,
            KEY_FREQ_PENALTY: 0,
            KEY_PRES_PENALTY: 0
        }
    }

    @staticmethod
    def get_data(logger: PrefixedLogger | None = default_logger) -> dict:
        try:
            create_file(Settings.SAVE_NAME, json.dumps(Settings.SAVE_DEFAULT, indent=True), logger)

            def on_invalid():
                write_file(Settings.SAVE_NAME, json.dumps(Settings.SAVE_DEFAULT, indent=True), logger)
                return Settings.SAVE_DEFAULT

            try:
                save_data = json.loads(read_file(Settings.SAVE_NAME, logger=logger))
            except JSONDecodeError:
                return on_invalid()

            if not isinstance(save_data, dict):  # File was invalid...
                return on_invalid()

            updated = save_data.copy()
            updated.update(Settings.SAVE_DEFAULT)

            for section in updated:
                if section in save_data:
                    updated[section].update(save_data[section])

            if not save_data == updated:
                write_file(Settings.SAVE_NAME, json.dumps(updated, indent=True), logger)

            return updated
        except TypeError as e:
            logger.error(f'TypeError getting settings data:\n{get_traceback(e)}')
            return Settings.SAVE_DEFAULT

    @staticmethod
    def set_data(data:dict, logger:PrefixedLogger|None=default_logger) -> tuple[bool,Exception|None]:
        try:
            write_file(Settings.SAVE_NAME, json.dumps(Settings.SAVE_DEFAULT, indent=True), logger)
        except Exception as e:
            return False, e
        return True, None


    @staticmethod
    def get_key_data(section_name: str, key: str, logger: PrefixedLogger | None = default_logger, settings_data: dict | None=None) -> bool | int | dict | None:
        save_data = settings_data if settings_data is not None else Settings.get_data(logger)
        key_data = None

        if section_name in save_data:
            section = save_data[section_name]
        elif section_name in Settings.SAVE_DEFAULT:
            section = Settings.SAVE_DEFAULT[section_name]
            logger.error(f'Section "{section_name}" found in save default instead of save file while getting key value..')
        else:
            logger.error(f'Could not find section "{section_name}"')
            return None

        if not isinstance(section, dict):
            logger.error(f'Section "{section_name}" is not dict while getting key value.')
            return None

        if key in section:
            key_data = section[key]
        else:
            logger.error(f'Could not find key "{key}" in section "{section_name}" while getting key value.')

        return key_data

    @staticmethod
    def set_key_data(section_name: str, key: str, value:bool|int|str|dict, logger: PrefixedLogger | None = default_logger, settings_data: dict | None=None) -> tuple[bool, FileNotFoundError|TypeError|None]:
        new_save = settings_data.copy() if settings_data is not None else Settings.get_data(logger)

        if section_name not in new_save:
            logger.error(f'Could not find section "{section_name}" while setting key value.')
            return False, FileNotFoundError(f'Could not find section "{section_name}" while setting key value.')

        if not isinstance(new_save[section_name], dict):
            logger.error(f'Section "{section_name}" is not dict while setting key value.')
            return False, TypeError(f'Section "{section_name}" is not dict while setting key value.')

        if key not in new_save[section_name]:
            logger.error(f'Could not find key "{key}" in section "{section_name}" while setting key value.')
            return False, FileNotFoundError(f'Could not find key "{key}" in section "{section_name}" while setting key value.')

        if not isinstance(new_save[section_name][key], type(value)):
            logger.error(f'Key "{key}" in section "{section_name}" ({type(new_save[section_name][key])}) does not match type {type(value)} of the new value {value}.')
            return False, TypeError(f'Key "{key}" in section "{section_name}" ({type(new_save[section_name][key])}) does not match type {type(value)} of the new value {value}.')

        new_save[section_name][key] = value
        return Settings.set_data(new_save, logger)
try:
    mkdir(CONFIG_PATH)
except FileExistsError:
    pass