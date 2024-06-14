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
async def generate_response(prompt:str, user:User, guild_id:int) -> tuple[str, bool]:
    console.line()
    console.task(f'Checking AI flags...')
    if not await resources.settings.ai_settings.is_enabled():
        console.error(f'AI flag is set to false.')
        return f'sowwy wallibe say no ai rn {choice(faces.SAD)}', True
    console.task_completed(f'AI flag is set to true.')
    
    console.task(f'Checking prompt tokens...')
    input_tokens = await token_calculator.prompt_to_tokens(prompt)
    if input_tokens > await resources.settings.ai_settings.get_max_prompt_tokens():
        console.error(f'Prompt token amount exceed the cap of {await resources.settings.ai_settings.get_max_prompt_tokens()}')
        return f'i not weading alat {choice(faces.CONFUSED)}', True
    console.task_completed(f'Prompt token amount does not exceed the token cap.')
    
    console.task(f'Creating useable history...')
    prompts = await create_prompt_history(prompt, user, guild_id)
    console.task_completed(f'History created.           ')

    console.task(f'Generating chat completion...')
    chat_completion = await create_chat_completion(prompts)
    
    console.task_completed(f'Chat completion successfully created.')
    finish_reason:str = chat_completion.choices[0].finish_reason
    response:str = chat_completion.choices[0].message.content
    used_tokens = chat_completion.usage
    
    input_cost = token_calculator.input_tokens_to_cost(used_tokens.prompt_tokens)
    output_cost = token_calculator.output_tokens_to_cost(used_tokens.completion_tokens)
    total_cost = input_cost + output_cost
    
    console.log(f'Response: {response}')
    console.log(f'Finish reason: {finish_reason}')
    console.log(f'Prompt tokens: {used_tokens.prompt_tokens} ({console.Colors.L_CHARGE}${token_calculator.to_string(input_cost)})')
    console.log(f'Completion tokens: {used_tokens.prompt_tokens} ({console.Colors.L_CHARGE}${token_calculator.to_string(output_cost)})')
    console.log(f'Total tokens: {used_tokens.total_tokens} ({console.Colors.L_CHARGE}${token_calculator.to_string(total_cost)})')
    console.line()
    
    return response, True
    
async def create_message(role:str, content:str) -> dict[str, str]:
    return {'role':role,'content':content}
    
async def create_prompt_history(prompt:str, user:User, guild_id:int) -> list[dict[str, str]]:
    history:list[dict[str, str]] = await resources.ai_history.get_history(guild_id)
    result:list[dict[str, str]]  = []
    for i in range(0, int(await resources.settings.ai_settings.get_history_memory())-1):
        if len(history) >= i+1:
            result.insert(0, list(reversed(history))[i])
        else:
            break
    result.append(dict(await create_message(ROLE_USER,prompt)))
    return result
    
async def create_chat_completion(prompts:list[dict[str, str]]):
    return client.chat.completions.create(
        model=environment.OPENAI_MOD,
        messages=prompts,
        temperature = await ai_settings.get_temperature(),
        top_p = await ai_settings.get_top_p(),
        logit_bias = await ai_settings.get_logit_bias(),
        seed = await ai_settings.get_seed(),
        max_tokens = await ai_settings.get_max_completion_tokens(),
        frequency_penalty = await ai_settings.get_frequency_penalty(),
        presence_penalty = await ai_settings.get_presence_penalty()
    )