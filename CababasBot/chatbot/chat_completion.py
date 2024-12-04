import asyncio

from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from CababasBot import env_secrets
from CababasBot.config_manager import Settings, AI
from CababasBot.logger import PrefixedLogger

client = OpenAI(
    api_key=env_secrets.OPENAI_API,
    organization=env_secrets.OPENAI_ORG,
    project=env_secrets.OPENAI_PROJ
)

async def generate_completion(history:list[dict[str,str]],config:dict|None=None,logger:PrefixedLogger|None=None) -> ChatCompletion:
    settings_config = config if config is not None else await Settings.get_data(logger)
    return client.chat.completions.create(
        model=env_secrets.OPENAI_MOD,
        messages=history,
        temperature=await Settings.get_key_data(Settings.SEC_AI, Settings.KEY_TEMP, logger, settings_config),
        top_p=await Settings.get_key_data(Settings.SEC_AI, Settings.KEY_TOP_P, logger, settings_config),
        logit_bias=await Settings.get_key_data(Settings.SEC_AI, Settings.KEY_LOGIT_BIAS, logger, settings_config),
        seed=await Settings.get_key_data(Settings.SEC_AI, Settings.KEY_SEED, logger, settings_config),
        max_tokens=await Settings.get_key_data(Settings.SEC_AI, Settings.KEY_MAX_COMP_TOK, logger, settings_config),
        frequency_penalty=await Settings.get_key_data(Settings.SEC_AI, Settings.KEY_FREQ_PENALTY, logger, settings_config),
        presence_penalty=await Settings.get_key_data(Settings.SEC_AI, Settings.KEY_PRES_PENALTY, logger, settings_config),
        stream=False
    )
