## Environment variables (secrets)

from os import environ

## Uncomment if necessary
# from dotenv import load_dotenv
# load_dotenv()

OPENAI_API:str = environ.get('OPENAI_CABABAS_API_KEY') # The API key to access OpenAI's API
OPENAI_PROJ:str = environ.get('OPENAI_CABABAS_PROJECT') # The project ID
OPENAI_ORG:str = environ.get('OPENAI_CABABAS_ORGANIZATION') # The organization ID
OPENAI_MOD:str = environ.get('OPENAI_CABABAS_MODEL') # The model ID

DISCORD_TOK:str = environ.get('DISCORD_CABABAS_TOKEN') # The discord bot token