import json
from json import JSONDecodeError
from os import mkdir
from os import path
from CababasBot.logger import get_traceback
from CababasBot.logger import PrefixedLogger

CONFIG_PATH = 'config'
default_logger = PrefixedLogger('CONFIG_MANAGER')

def create_folder(name: str, logger: PrefixedLogger | None = default_logger) -> tuple[bool, Exception | None]:
    folder = f'{CONFIG_PATH}/{name}'
    try:
        mkdir(folder)
    except FileExistsError:
        logger.task_completed(f'Directory {folder} already found. Did not create.')
    except Exception as e:
        logger.error(f'Error creating directory "{name}":\n{get_traceback(e)}')
        return False, e
    return True, None


def create_file(name: str, content: str | None = '[]', logger: PrefixedLogger | None = default_logger) -> tuple[
    bool, Exception | None]:
    file_path = f'{CONFIG_PATH}/{name}'
    try:
        with open(file=file_path, mode='x', encoding='utf-8') as file:
            file.write(content)
    except FileExistsError as e:
        logger.task_completed(f'File {file_path} already found. Did not create.')
        return True, e
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
    def get_section(name: str, logger: PrefixedLogger | None = default_logger, settings_data: dict | None=None) -> dict:
        data = settings_data if settings_data is not None else Settings.get_data(logger)
        section_data = {}

        if name in data:
            section_data = data[name]
        elif name in Settings.SAVE_DEFAULT:
            section_data = Settings.SAVE_DEFAULT[name]
            logger.error(f'Section "{name}" not found in save file. Using default section.')
        else:
            logger.error(f'Section "{name}" not found in settings.')

        if isinstance(section_data, dict):
            return section_data

        return {}

    @staticmethod
    def get_key_data(section_name: str, key: str, logger: PrefixedLogger | None = default_logger, settings_data: dict | None=None) -> bool | int | dict | None:
        section = Settings.get_section(section_name, logger, settings_data)
        key_data = None

        if key in section:
            key_data = section[key]
        else:
            logger.error(f'Could not find key "{key}" in section "{section_name}"')

        return key_data


try:
    mkdir(CONFIG_PATH)
except FileExistsError:
    pass