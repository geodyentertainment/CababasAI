import os
import time
import json
import random
from Faces import FACES
from openai import OpenAI
from PrintColors import TColors
# from dotenv import load_dotenv

# load_dotenv()

MODEL = os.environ.get('OPENAI_CABABAS_MODEL')
API_KEY = os.environ.get('OPENAI_CABABAS_API_KEY')
PROJECT_ID = os.environ.get('OPENAI_CABABAS_PROJECT_ID')
ORGANIZATION_ID = os.environ.get('OPENAI_WYU2_ORGANIZATION_ID')
PRESET_PATH = "Resources/Preset.txt"
HISTORY_PATH = "Resources/History.json"
FINETUNING_PATH = "Resources/FineTuning.jsonl"

FINE_TUNING = False

RATE_LIMIT = 5
RECOMMENDED_COST = 0.0025
MAX_CONTENT_SIZE = 200
LAST_REQ = time.time()

history = []

enabled = False

AI_Client = OpenAI(
    api_key=API_KEY,
    project=PROJECT_ID,
    organization=ORGANIZATION_ID
)

def process_response_ai(name:str, content:str):
    return process_response_ai_flag(name, content, False)

def process_response_ai_flag(name:str, content:str, ignore_flag:bool) -> tuple[str, float]:
    current_time = time.time()

    global LAST_REQ
    global RATE_LIMIT
    global AI_Client
    global enabled
    global history
    global MAX_CONTENT_SIZE

    if not enabled and not ignore_flag:
        print(f'{TColors.RED}AI is disabled.{TColors.RESET}')
        return "sowy wallibe says no ai rn ):", 0.0
    
    if current_time-LAST_REQ < RATE_LIMIT:
        print(f'{TColors.RED}User was rate limited.{TColors.RESET}')
        return random.choice(FACES), 0.0
    
    if len(content) >= MAX_CONTENT_SIZE:
        print(f'{TColors.RED}Content exeeds max content cap.{TColors.RESET}')
        return "i not reading allat " + random.choice(FACES), 0.0

    messages = []

    # Add all previous history to messages
    if not FINE_TUNING:
        for m in history:
            messages.append(m)

    with open(PRESET_PATH, "r") as PRESET_FILE:

        preset_content = PRESET_FILE.read().replace("\n", " ")
        messages.append({"role":"system","content": preset_content+" You are talking to "+name})    

    while (len(messages) > 30):
        messages.pop(0)

    # Add prompt to history
    formatted_prompt = {"role":"user","content":content}
    messages.append(formatted_prompt)

    # Generate a response using ChatGPT
    chat_completion = AI_Client.chat.completions.create(
        messages=messages,
        model=MODEL,
        max_tokens=40,
        seed=572875094,
        temperature=1.1,
        logit_bias={"1734": -100}
    )
    response:str = chat_completion.choices[0].message.content

    finish_reason = chat_completion.choices[0].finish_reason

    cost:float = (prompt_token_pricing(chat_completion.usage.prompt_tokens) + completion_token_pricing(chat_completion.usage.completion_tokens))

    # print(f'{TColors.B_FINISH_REASON}> Seed {chat_completion.}{TColors.RESET}')
    print(f'{TColors.B_FINISH_REASON}> Prompt tokens: {chat_completion.usage.prompt_tokens}{TColors.RESET}')
    print(f'{TColors.B_FINISH_REASON}> Completion tokens: {chat_completion.usage.completion_tokens}{TColors.RESET}')
    print(f'{TColors.B_FINISH_REASON}> Cost of generation: {TColors.RED}${cost}{TColors.RESET}')
    print(f'{TColors.B_FINISH_REASON}> Finish reason: {finish_reason}{TColors.RESET}')

    if (finish_reason == 'content_filter'): # Make sure content filter wasn't triggered
        return "That is not allowed :(", cost

    elif (finish_reason == 'length'):
        response = response + " ... *yawn*"

    # Add response to history
    if FINE_TUNING:
        save_to_finetuning(to_finetuning_line(preset_content, content, response))
        response += " (fine tuning)"
    else:
        while (len(history) > 2000):
            history.pop(0)
            
        history.append(formatted_prompt)
        history.append({"role":"assistant","content": response})

        saveHistory()

    LAST_REQ = current_time
    return response, cost

def saveHistory() -> None:
    global history

    with open(HISTORY_PATH, "w") as SAVE_FILE:
        SAVE_FILE.write(json.dumps(history))

def loadHistory() -> None:
    global history

    with open(HISTORY_PATH, "r", encoding='utf-8') as HISTORY_FILE:
        history = json.loads(HISTORY_FILE.read())
        print(f'{TColors.B_SUCCESS}Loaded: {history}{TColors.RESET}')

def get_fine_tuning_history():
    FINETUNING_HISTORY_PATH = open(FINETUNING_HISTORY_PATH, "r")
    return json.loads(FINETUNING_HISTORY_PATH.read())

def to_finetuning_line(sys:str, prompt:str, response:str) -> str:
    try:
        n_sys = sys.replace("\n", " ").replace('"', '\\"')
        n_prompt = prompt.replace("\n", " ").replace('"', '\\"')
        n_response = response.replace("\n", " ").replace('"', '\\"')

        line = (f'{{"messages":[{{"role":"system","content":"{n_sys}"}},{{"role":"user","content":"{n_prompt}"}},{{"role":"assistant","content":"{n_response}"}}]}}')
        return line
    except Exception as e:
        print(f'{TColors.RED}Could not create fine tuning model line:{str(e)}{TColors.RESET}')
        return str(e)

def save_to_finetuning(line:str) -> None:
    with open(FINETUNING_PATH, "a",encoding='utf-8') as finetuning_file:
        try:
            finetuning_file.write("\n"+line)
        except Exception as e:
            print(f'{TColors.RED}Could not append to fine tuning file: {str(e)}{TColors.RESET}')

def clearHistory() -> None:
    global history

    history.clear()
    
def prompt_token_pricing(t) -> float:
    return (t/1000000.0)*3

def completion_token_pricing(t) -> float:
    return (t/1000000.0)*6