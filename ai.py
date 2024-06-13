import openai
from discord import User
from openai import OpenAI
from random import choice

import console
import os_manager
from os_manager import resources
from os_manager import environment
import token_calculator
import faces

ROLE_USER = 'user'
ROLE_SYSTEM = 'system'

ai_settings = resources.settings.ai_settings

client = OpenAI(
    api_key=environment.OPENAI_API,
    organization=environment.OPENAI_ORG,
    project=environment.OPENAI_PROJ
)

# Get a response based on the prompt. Returns the output message, and a flag determining if the process was a success.
async def get_response(prompt:str, user:User, guild_id:int) -> tuple[str, bool]:
    console.log(f'Checking response flags: ')
    
    input_tokens = await token_calculator.prompt_to_tokens(prompt)
    if input_tokens > await resources.settings.ai_settings.get_max_prompt_tokens():
        return f'i not weading alat {choice(faces.SAD)}', False
    
    prompts = await create_prompt_history(prompt, user, guild_id)

    chat_completion = await create_chat_completion(prompts, user)
    
    finish_reason = chat_completion.choices[0].finish_reason
    response:str = chat_completion.choices[0].message.content
    used_tokens = chat_completion.usage
    
async def create_message(role:str, content:str) -> dict[str, str]:
    return {'role':role,'content':content}
    
async def create_prompt_history(prompt:str, user:User, guild_id:int) -> list[dict[str, str]]:
    history:list[dict[str, str]] = resources.ai_history.get_history(guild_id)
    result:list[dict[str, str]]  = {}
    for i in range(0, resources.settings.ai_settings.get_history_memory()-1):
        if len(history) >= i:
            result.insert(0, reversed(history)[i])
        else:
            break
    result.append(create_message(ROLE_USER,prompt))
    
async def create_chat_completion(prompts:list[dict[str, str]], user:User):
    return client.completions.create(
        model=environment.OPENAI_MOD,
        user=str(user.id),
        prompt=prompts,
        temperature=ai_settings.get_temperature(),
        top_p=ai_settings.get_top_p(),
        logit_bias=ai_settings.get_logit_bias(),
        seed=ai_settings.get_seed(),
        max_tokens=ai_settings.get_max_completion_tokens(),
        frequency_penalty=ai_settings.get_frequency_penalty(),
        presence_penalty=ai_settings.get_presence_penalty()
    )