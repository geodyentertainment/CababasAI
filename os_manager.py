from os import environ
from os import path
from os import mkdir
from json import loads
from json import dumps

## Uncomment if necessary
# from dotenv import load_dotenv
# load_dotenv()

WHITELISTED_GUILDS:dict[str, int] = {
    'TEST' : 1249087176592068659
}

# Environment variables
class environment:
    OPENAI_API:str = environ.get('OPENAI_CABABAS_API_KEY', 'unknown') # The API key to access OpenAI's API
    OPENAI_PROJ:str = environ.get('OPENAI_CABABAS_PROJECT', 'unknown') # The project ID
    OPENAI_ORG:str = environ.get('OPENAI_CABABAS_ORGANIZATION', 'unknown') # The organization ID
    OPENAI_MOD:str = environ.get('OPENAI_CABABAS_MODEL', 'unknown') # The model ID

    DISCORD_TOK:str = environ.get('DISCORD_CABABAS_TOKEN', 'unknown') # The discord bot token

class resources:
    ## Constants
    FOLDER_PATH:str = 'resources'
    HISTORIES_PATH:str = f'{FOLDER_PATH}/histories'
    SETTINGS_PATH:str = f'{FOLDER_PATH}/Settings.json'
    SYSTEM_PATH:str = f'{FOLDER_PATH}/System'
    FINE_TUNE_PATH:str = f'{FOLDER_PATH}/FineTuning.jsonl'

    class settings:
        DEFAULT:dict[str, dict[str, any]] = {
            'discord' : {
                'whitelisted_channels' : {},
                'managers' : {
                    'Geody' : 775117392644407296,
                    'Wallibe' : 1164735044200435734
                }
            }
        }

        @staticmethod
        async def update_settings() -> None:
            self = resources.settings
            # Check if settings file exists
            if not path.exists(resources.SETTINGS_PATH):
                with open(resources.SETTINGS_PATH, 'x',encoding='utf-8') as settings_file:
                    settings_file.write(dumps(obj=self.DEFAULT,indent=True)) # Create file if it doesnt exist
                return # Stop the function
            
            # Update settings based on the default settings if file exists
            with open(resources.SETTINGS_PATH, 'r',encoding='utf-8') as settings_file:
                saved = loads(settings_file.read())

            with open(resources.SETTINGS_PATH, 'w',encoding='utf-8') as settings_file:
                if not isinstance(saved, dict): # File was invalid...
                    settings_file.write(dumps(obj=self.DEFAULT,indent=True))
                    return
                updated = self.DEFAULT.copy()
                updated.update(saved)

                settings_file.write(dumps(obj=updated,indent=True))

        @staticmethod
        async def get_settings() -> dict[str, any]:
            self = resources.settings
            await self.update_settings() # Make sure settings are updated

            with open(resources.SETTINGS_PATH, 'r',encoding='utf-8') as settings_file: # Open file
                return loads(settings_file.read()) # Read file, load, and return value
            
        @staticmethod
        async def is_manager(user_id:int) -> bool:
            saved:dict[str, any] = await resources.settings.get_settings()
            managers:dict[str, int] = saved["discord"]["managers"]

            return user_id in managers.values() # Check if the user ID is found in the managers file

    class history:
        DEFAULT:list[dict[str, str]] = []

        @staticmethod
        async def update_histories() -> None:
            self = resources.history

            # Create history folder if it doesn't exist
            if not path.exists(resources.HISTORIES_PATH):
                mkdir(resources.HISTORIES_PATH)

            # Iterate through each whitelisted guild ID
            for guild_id in WHITELISTED_GUILDS.values():
                file_path:str = self.id_to_history_path(guild_id) # Get the path to the save file
                if not path.exists(file_path): # Check if the file exists
                    with open(file_path, 'x',encoding='utf-8') as history_file: # Create new file if it doesn't exist
                        history_file.write(dumps(obj=self.DEFAULT,indent=True))

        @staticmethod
        def id_to_history_path(guild_id:int) -> str:
            return f'{resources.HISTORIES_PATH}/history-{str(guild_id)}.json'
            
        @staticmethod
        async def get_history(guild_id:int) -> list[dict[str, str]]:
            self = resources.history
            await self.update_histories() # Make sure histories are updated

            file_path:str = self.id_to_history_path(guild_id)

            if not path.exists(file_path): # In case the ID was invalid, meaning no file exists
                return self.DEFAULT # If so, return default empty history

            with open(self.id_to_history_path(guild_id), 'r',encoding='utf-8') as settings_file: # Open file
                return loads(settings_file.read()) # Read file, load, and return value
            
    class finetuning:
        @staticmethod
        async def update_fine_tune() -> None:
            self = resources
            # Check if fine tuning file exists
            if not path.exists(self.FINE_TUNE_PATH):
                open(self.FINE_TUNE_PATH, 'x',encoding='utf-8').close() # Create file if it doesnt exist

    class system:
        @staticmethod
        async def update_system() -> None:
            self = resources
            # Check if system file exists
            if not path.exists(self.SYSTEM_PATH):
                open(self.SYSTEM_PATH, 'x',encoding='utf-8').close() # Create file if it doesnt exist

        @staticmethod
        async def get_system() -> str:
            self = resources
            await self.system.update_system() # Make sure file is updated
            with open(self.SYSTEM_PATH, 'r', encoding='utf-8') as system_file:
                return system_file.read()

    # Check and create missing resource files (including the directory itself)
    @staticmethod
    async def update_files() -> None:
        self = resources
        # Update folder
        if not path.exists(self.FOLDER_PATH):
            mkdir(self.FOLDER_PATH)

        # Update settings
        await self.settings.update_settings()

        # Update history
        await self.history.update_histories()

        # Update the fine tuning file
        await self.finetuning.update_fine_tune()

        # Update the system file
        await self.system.update_system()