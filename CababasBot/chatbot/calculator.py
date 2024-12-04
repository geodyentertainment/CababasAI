import tiktoken

from CababasBot import env_secrets
from CababasBot.config_manager import Settings
from CababasBot.logger import PrefixedLogger

TYPE_INPUT = 'input'
TYPE_OUTPUT = 'output'

def input_to_tokens(prompt: str) -> int:
    model_name = env_secrets.OPENAI_MOD

    encoding = tiktoken.encoding_for_model(model_name=model_name)

    tokens = encoding.encode(prompt)
    return len(tokens)

async def calculate_cost(count_type:str, token_count:int, logger:PrefixedLogger|None=None , config:dict|None=None) -> float:
    mult = -1.0
    if count_type == TYPE_INPUT:
        mult = await Settings.get_key_data(Settings.SEC_AI, Settings.KEY_PROMPT_COST, logger, config)
    else:
        mult =await  Settings.get_key_data(Settings.SEC_AI, Settings.KEY_COMP_COST, logger, config)
    return token_count*mult