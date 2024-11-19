import json
from json import JSONDecodeError
from os import mkdir
from os import path
from CababasBot.logger import get_traceback
from CababasBot.logger import Logger


CONFIG_PATH = 'config'


def create_folder(name:str,logger:Logger|None=None) -> tuple[bool, Exception|None]:
   folder = f'{CONFIG_PATH}/{name}'
   try:
       mkdir(folder)
   except FileExistsError:
       msg = f'Directory {folder} already found. Did not create.'
       if logger is Logger:
           logger.task_completed(msg)
       else:
           print(msg)
   except Exception as e:
       msg = f'Error creating file "{name}":\n{get_traceback(e)}'
       if logger is Logger:
           logger.error(msg)
       else:
           print(msg)
       return False, e
   return True, None


def create_file(name:str,content:str|None='[]',logger:Logger|None=None) -> tuple[bool, Exception|None]:
   file_path = f'{CONFIG_PATH}/{name}'
   try:
       with open(file=file_path, mode='x', encoding='utf-8') as file:
               file.write(content)
   except FileExistsError as e:
       msg = f'File {file_path} already found. Did not create.'
       if logger is Logger:
           logger.task_completed(msg)
       else:
           print(msg)
       return True, e
   except Exception as e:
       msg = f'Error creating file "{name}":\n{get_traceback(e)}'
       if logger is Logger:
           logger.error(msg)
       else:
           print(msg)
       return False, e
   return True, None


def write_file(name:str,content:str|None='[]',logger:Logger|None=None) -> tuple[bool, Exception|None]:
   try:
       file_path = f'{CONFIG_PATH}/{name}'
       with open(file=file_path, mode='w', encoding='utf-8') as file:
               file.write(content)
   except Exception as e:
       msg = f'Error creating file "{name}":\n{get_traceback(e)}'
       if logger is Logger:
           logger.error(msg)
       else:
           print(msg)
       return False, e
   return True, None


def read_file(name:str,default_content:str|None='[]',logger:Logger|None=None) -> str:
   file_path = f'{CONFIG_PATH}/{name}'
   try:
       if path.exists(file_path):
           with open(file=file_path, mode='r', encoding='utf-8') as file:
               return file.read()
   except Exception as e:
       msg = f'Error creating file "{name}": {str(e)}\n{get_traceback(e)}'
       if logger is Logger:
           logger.error(msg)
       else:
           print(msg)
       return default_content


class Settings:
   NAME = 'settings.json'
   DEFAULT:dict[str, dict[str, any]] = {
       'discord': {
           'enabled': True,
           'managers': {
               'Geody': 775117392644407296,
               'Wallibe': 1164735044200435734
           },
           'commands_whitelisted_guilds':{},
           'ai_whitelisted_guilds':{},
       },
       'ai_settings': {
           'enabled': False,
           'history_memory': 11,
           'temperature': 0.79,
           'top_p': 1,
           'logit_bias': {'1734': -100},
           'seed': 572875094,
           'get_max_prompt_tokens': 40,
           'max_completion_tokens': 20,
           'frequency_penalty': 0,
           'presence_penalty': 0
       }
   }


   @staticmethod
   def get_data(logger:Logger|None=None) -> dict:
       try:
           create_file(Settings.NAME, json.dumps(Settings.DEFAULT, indent=True), logger)

           def on_invalid():
               print("Invalid settings file. Rewriting...")
               write_file(Settings.NAME, json.dumps(Settings.DEFAULT, indent=True), logger)
               return Settings.DEFAULT


           try:
               save_data = json.loads(read_file(Settings.NAME, logger=logger))
           except JSONDecodeError:
               return on_invalid()


           if not isinstance(save_data, dict):  # File was invalid...
               return on_invalid()


           updated = save_data.copy()
           updated.update(Settings.DEFAULT)

           for section in updated:
               updated[section].update(save_data[section])

           if not save_data == updated:
               write_file(Settings.NAME, json.dumps(updated, indent=True), logger)

           return updated
       except TypeError as e:
           msg = f'TypeError getting settings data:\n{get_traceback(e)}'
           if logger is Logger:
               logger.error(msg)
           else:
               print(msg)
           return Settings.DEFAULT


   class Section:
       def __init__(self,name:str):
           self.name=name

try:
   mkdir(CONFIG_PATH)
except FileExistsError:
   print(f'Config file already found.')


print(f'\n\n{str(Settings.get_data())}')