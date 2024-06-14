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
    AI_PATH:str = f'{FOLDER_PATH}/ai'
    RNG_PATH:str = f'{FOLDER_PATH}/rng'
    SETTINGS_PATH:str = f'{FOLDER_PATH}/Settings.json'

    AI_HISTORIES_PATH:str = f'{AI_PATH}/histories'
    AI_SYSTEM_PATH:str = f'{AI_PATH}/System'
    AI_FINE_TUNE_PATH:str = f'{AI_PATH}/FineTuning.jsonl'

    RNG_RANKS_PATH:str = f'{RNG_PATH}/Ranks.json'

    class settings:
        DEFAULT:dict[str, dict[str, any]] = {
            'discord' : {
                'managers' : {
                    'Geody' : 775117392644407296,
                    'Wallibe' : 1164735044200435734
                }
            },
            'ai_settings' : {
                'enabled' : False,
                'encoding_model' : 'gpt-3.5-turbo',
                'history_memory' : 10,
                'temperature' : 1,
                'top_p' : 1,
                'logit_bias' : {'1734': -100},
                'seed' : 572875094,
                'get_max_prompt_tokens' : 100,
                'max_completion_tokens' : 20,
                'frequency_penalty' : 0,
                'presence_penalty' : 0
            }
        }
                
        class discord:
            @staticmethod
            async def is_manager(user_id:int) -> bool:
                saved:dict[str, any] = await resources.settings.get_settings()
                managers:dict[str, int] = saved["discord"]["managers"]

                return user_id in managers.values() # Check if the user ID is found in the managers file
            
        class ai_settings:
            @staticmethod
            async def get_ai_settings() -> dict[str, any]:
                saved:dict[str, any] = dict(await resources.settings.get_settings())  
                return saved['ai_settings']             
            
            async def is_enabled() -> bool:
                self = resources.settings.ai_settings
                return dict(await self.get_ai_settings())['enabled']
            
            async def set_enabled(flag:bool) -> None:
                current_settings = await resources.settings.get_settings()
                current_settings['ai_settings']['enabled'] = flag
                await resources.settings.set_settings(current_settings)
                
            async def get_encoding_model() -> str:
                self = resources.settings.ai_settings
                return dict(await self.get_ai_settings())['encoding_model']
            
            async def get_temperature() -> float:
                self = resources.settings.ai_settings
                return dict(await self.get_ai_settings())['temperature']
            
            async def get_top_p() -> float:
                self = resources.settings.ai_settings
                return dict(await self.get_ai_settings())['top_p']
            
            async def get_logit_bias() -> dict[str, int]:
                self = resources.settings.ai_settings
                return dict(await self.get_ai_settings())['logit_bias']
            
            async def get_seed() -> int:
                self = resources.settings.ai_settings
                return dict(await self.get_ai_settings())['seed']
            
            async def get_max_prompt_tokens() -> int:
                self = resources.settings.ai_settings
                return dict(await self.get_ai_settings())['get_max_prompt_tokens']
            
            async def get_max_completion_tokens() -> int:
                self = resources.settings.ai_settings
                return dict(await self.get_ai_settings())['max_completion_tokens']
            
            async def get_frequency_penalty() -> float:
                self = resources.settings.ai_settings
                return dict(await self.get_ai_settings())['frequency_penalty']
            
            async def get_presence_penalty() -> float:
                self = resources.settings.ai_settings
                return dict(await self.get_ai_settings())['presence_penalty']
            
            async def get_history_memory() -> int:
                self = resources.settings.ai_settings
                return dict(await self.get_ai_settings())['history_memory']
                
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
        async def set_settings(new_settings:dict[str, any]) -> None:
            self = resources.settings
            await self.update_settings() # Make sure settings are updated
            
            updated = self.DEFAULT.copy()
            updated.update(new_settings)
            
            with open(resources.SETTINGS_PATH, 'w',encoding='utf-8') as settings_file: # Open file
                settings_file.write(updated)

    class ai_history:
        DEFAULT:list[dict[str, str]] = []

        @staticmethod
        async def update_histories() -> None:
            self = resources.ai_history

            # Create history folder if it doesn't exist
            if not path.exists(resources.AI_HISTORIES_PATH):
                mkdir(resources.AI_HISTORIES_PATH)

            # Iterate through each whitelisted guild ID
            for guild_id in WHITELISTED_GUILDS.values():
                file_path:str = self.id_to_history_path(guild_id) # Get the path to the save file
                if not path.exists(file_path): # Check if the file exists
                    with open(file_path, 'x',encoding='utf-8') as history_file: # Create new file if it doesn't exist
                        history_file.write(dumps(obj=self.DEFAULT,indent=True))

        @staticmethod
        def id_to_history_path(guild_id:int) -> str:
            return f'{resources.AI_HISTORIES_PATH}/history-{str(guild_id)}.json'
            
        @staticmethod
        async def get_history(guild_id:int) -> list[dict[str, str]]:
            self = resources.ai_history
            await self.update_histories() # Make sure histories are updated

            file_path:str = self.id_to_history_path(guild_id)

            if not path.exists(file_path): # In case the ID was invalid, meaning no file exists
                return self.DEFAULT.copy() # If so, return default empty history

            with open(self.id_to_history_path(guild_id), 'r',encoding='utf-8') as history_file: # Open file
                return loads(history_file.read()) # Read file, load, and return value
            
    class ai_finetuning:
        @staticmethod
        async def update_fine_tune() -> None:
            self = resources
            # Check if fine tuning file exists
            if not path.exists(self.AI_FINE_TUNE_PATH):
                open(self.AI_FINE_TUNE_PATH, 'x',encoding='utf-8').close() # Create file if it doesnt exist

    class ai_system:
        @staticmethod
        async def update_system() -> None:
            self = resources
            # Check if system file exists
            if not path.exists(self.AI_SYSTEM_PATH):
                open(self.AI_SYSTEM_PATH, 'x',encoding='utf-8').close() # Create file if it doesnt exist

        @staticmethod
        async def get_system() -> str:
            self = resources
            await self.ai_system.update_system() # Make sure file is updated
            with open(self.AI_SYSTEM_PATH, 'r', encoding='utf-8') as system_file:
                return system_file.read()
            
    class rng_ranks:
        DEFAULT:dict[str, str] = {}

        @staticmethod
        async def update_ranks() -> None:
            self = resources
            # Check if system file exists
            if not path.exists(self.RNG_RANKS_PATH):
                with open(self.RNG_RANKS_PATH, 'x',encoding='utf-8') as file: # Create file if it doesnt exist
                    file.write(dumps(self.rng_ranks.DEFAULT,indent=True))

        @staticmethod
        async def get_ranks() -> dict[str, str]:
            self = resources
            await self.rng_ranks.update_ranks() # Make sure ranks are updated
            with open(self.RNG_RANKS_PATH, 'r',encoding='utf-8') as file: # Open file
                return loads(file.read()) # Read file, load, and return value

        @staticmethod
        async def get_rank(user_id:int) -> str | None:
            ranks = await resources.rng_ranks.get_ranks()

            if str(user_id) in ranks:
                return ranks[str(user_id)]
            
            return None
        
        @staticmethod
        async def set_rank(user_id:int, rank:str) -> None:
            self = resources.rng_ranks
            await self.update_ranks() # Make sure ranks are updated
            with open(resources.RNG_RANKS_PATH, 'r',encoding='utf-8') as file: # Open file
                ranks = loads(file.read()) # Read file, load, and return value
            
            ranks[str(user_id)] = rank

            with open(resources.RNG_RANKS_PATH, 'w',encoding='utf-8') as file: # Open file
                file.write(dumps(ranks,indent=True))
            


    # Check and create missing resource files (including the directory itself)
    @staticmethod
    async def update_files() -> None:
        self = resources
        # Update folders
        if not path.exists(self.FOLDER_PATH):
            mkdir(self.FOLDER_PATH)

        if not path.exists(self.AI_PATH):
            mkdir(self.AI_PATH)

        if not path.exists(self.RNG_PATH):
            mkdir(self.RNG_PATH)

        # Update settings
        await self.settings.update_settings()

        # Update ai history
        await self.ai_history.update_histories()

        # Update the ai fine tuning file
        await self.ai_finetuning.update_fine_tune()

        # Update the ai system file
        await self.ai_system.update_system()

        # Update the RNG ranks file
        await self.rng_ranks.update_ranks()