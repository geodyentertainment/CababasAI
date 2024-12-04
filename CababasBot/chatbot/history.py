from CababasBot.config_manager import AI, Settings
from CababasBot.logger import PrefixedLogger

ROLE_USER = 'user'
ROLE_ASSIST = 'assistant'
ROLE_SYSTEM = 'system'

K_PROMPTER = 'prompter'
K_ROLE = 'role'
K_CONTENT = 'content'

async def prompt_to_history(history_id:int|None, prompt:str, role:str, user:str|None, logger:PrefixedLogger|None=None, settings_data:dict|None=None) -> list[dict[str,str]]:
    history = (await AI.get_history(history_id, logger)) if history_id is not None else []

    memory = await Settings.get_key_data(Settings.SEC_AI, Settings.KEY_HISTORY_MEM, logger, settings_data)
    if memory is not int:
        memory = 10

    if len(history) > memory:
        history = history[memory:]

    history.append(create_message(user, role, prompt))
    history.append(create_message(None, ROLE_SYSTEM,await AI.get_system(logger)))
    return history

async def append_passed_history(history_id:int, passed_history:list[dict[str,str]], response:str, logger:PrefixedLogger|None=None):
    for i in range(len(passed_history)):
        if len(passed_history) <= i:
            break
        message = passed_history[i]
        if message.get(K_ROLE) == ROLE_SYSTEM:
            passed_history.pop(i)

    passed_history.append(create_message(None, ROLE_ASSIST,response))
    await AI.write_history(history_id, passed_history, logger)

def create_message(user:str|None, role:str, prompt:str, ) -> dict[str, str]:
    if user is None:
        return {
            K_ROLE: role,
            K_CONTENT: prompt
        }
    return {
        K_PROMPTER:user,
        K_ROLE:role,
        K_CONTENT:prompt
    }