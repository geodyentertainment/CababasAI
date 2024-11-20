from os import environ
from dotenv import load_dotenv

load_dotenv()

OPENAI_API:str = environ.get('OPENAI_CABABAS_API_KEY', 'unknown')
OPENAI_PROJ:str = environ.get('OPENAI_CABABAS_PROJECT', 'unknown')
OPENAI_ORG:str = environ.get('OPENAI_CABABAS_ORGANIZATION', 'unknown')
OPENAI_MOD:str = environ.get('OPENAI_CABABAS_MODEL', 'unknown')
DISCORD_TOK:str = environ.get('DISCORD_CABABAS_TOKEN', 'unknown')
DISCORD_TOK_TEST:str = environ.get('DISCORD_CABABAS_TOKEN_TEST', 'unknown')
ERROR_CHANNEL_ID:int = environ.get('ERROR_CHANNEL_ID',0)