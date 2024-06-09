import os
import time
import json
import random
from Faces import FACES
from openai import OpenAI
from PrintColors import TColors
# from dotenv import load_dotenv

# load_dotenv()

MODEL = "ft:gpt-3.5-turbo-0125:wyu2:cameluo-cababas:9YCcnkvC"
# MODEL = "gpt-3.5-turbo"
API_KEY = os.environ.get('OPENAI_CABABAS_API_KEY')
PROJECT_ID = os.environ.get('OPENAI_CABABAS_PROJECT_ID')
ORGANIZATION_ID = os.environ.get('OPENAI_WYU2_ORGANIZATION_ID')
PRESET_PATH = "Resources/Preset.txt"
HISTORY_PATH = "Resources/History.json"

RATE_LIMIT = 5
RECOMMENDED_COST = 0.0025
MAX_CONTENT_SIZE = 200
LAST_REQ = time.time()

enabled = False

AI_Client = OpenAI(
    api_key=API_KEY,
    project=PROJECT_ID,
    organization=ORGANIZATION_ID
)

def process_response_ai(content:str):
    return process_response_ai_flag(content, False)

def process_response_ai_flag(content:str, ignore_flag:bool):
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

    PRESET_FILE = open(PRESET_PATH, "r")
    messages = []

    # Add all previous history to messages
    for m in history:
        messages.append(m)
    messages.append({"role":"system","content":PRESET_FILE.read()})
    PRESET_FILE.close()
    
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
        seed=0,
        temperature=0.5,
        logit_bias={"1734": -100}
    )
    response = chat_completion.choices[0].message.content

    finish_reason = chat_completion.choices[0].finish_reason

    cost:float = (prompt_token_pricing(chat_completion.usage.prompt_tokens) + completion_token_pricing(chat_completion.usage.completion_tokens))

    print(f'{TColors.B_FINISH_REASON}> Prompt tokens: {chat_completion.usage.prompt_tokens}{TColors.RESET}')
    print(f'{TColors.B_FINISH_REASON}> Completion tokens: {chat_completion.usage.completion_tokens}{TColors.RESET}')
    print(f'{TColors.B_FINISH_REASON}> Cost of generation: {TColors.RED}${cost}{TColors.RESET}')
    print(f'{TColors.B_FINISH_REASON}> Finish reason: {finish_reason}{TColors.RESET}')

    if (finish_reason == 'content_filter'): # Make sure content filter wasn't triggered
        return "That is not allowed :(", cost

    elif (finish_reason == 'length'):
        response = response + " ... *yawn*"

    # Add response to history
    while (len(history) > 2000):
        history.pop(0)
        
    history.append(formatted_prompt)
    history.append({"role":"assistant","content": response})

    saveHistory()

    LAST_REQ = current_time
    return response, cost

def saveHistory():
    global history

    SAVE_FILE = open(HISTORY_PATH, "w")
    SAVE_FILE.write(json.dumps(history))
    SAVE_FILE.close()

def loadHistory():
    global history

    HISTORY_FILE = open(HISTORY_PATH, "r")
    history = json.loads(HISTORY_FILE.read())
    print(f'{TColors.B_SUCCESS}Loaded: {history}{TColors.RESET}')
    HISTORY_FILE.close()

def clearHistory():
    global history

    history.clear()
    
def prompt_token_pricing(t):
    return (t/1000000.0)*3

def completion_token_pricing(t):
    return (t/1000000.0)*6