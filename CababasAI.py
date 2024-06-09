import os
import time
import json
import random
from Faces import FACES
from openai import OpenAI
from PrintColors import TColors

MODEL = "ft:gpt-3.5-turbo-0125:wyu2:cameluo-cababas:9YCcnkvC"
# MODEL = "gpt-3.5-turbo"
API_KEY = os.environ.get('OPENAI_CABABAS_API_KEY')
PROJECT_ID = os.environ.get('OPENAI_CABABAS_PROJECT_ID')
ORGANIZATION_ID = os.environ.get('OPENAI_WYU2_ORGANIZATION_ID')
PRESET_PATH = "Resources\\Preset.txt"
HISTORY_PATH = "Resources\\History.json"

RATE_LIMIT = 4
LAST_REQ = time.time()

enabled = True

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

    if not enabled and not ignore_flag:
        return "sowy wallibe says no ai rn ):"
    
    if current_time-LAST_REQ < RATE_LIMIT:
        return random.choice(FACES)

    PRESET_FILE = open(PRESET_PATH, "r")
    messages = []

    # Add all previous history to messages
    for m in history:
        messages.append(m)
    messages.append({"role":"system", "content" : PRESET_FILE.read()})
    PRESET_FILE.close()

    # Add prompt to history
    formatted_prompt = {"role": "user","content": content}
    messages.append(formatted_prompt)

    # Generate a response using ChatGPT
    chat_completion = AI_Client.chat.completions.create(
        messages=messages,
        model=MODEL,
        max_tokens=20,
        seed=0,
        temperature=1,
        logit_bias={"1734": -100}
    )
    response = chat_completion.choices[0].message.content

    finish_reason = chat_completion.choices[0].finish_reason
    print(f'{TColors.B_FINISH_REASON}> Finish reason: {finish_reason}{TColors.RESET}')

    if (finish_reason == 'content_filter'): # Make sure content filter wasn't triggered
        return "That is not allowed :("

    elif (finish_reason == 'length'):
        response = response + "... *yawn* -_-"

    # Add response to history
    history.append(formatted_prompt)
    history.append({
        "role": "assistant","content": response
    })

    while (len(history) > 100):
        history.pop(0)

    saveHistory()

    LAST_REQ = current_time
    return response

def saveHistory():
    global history

    SAVE_FILE = open(HISTORY_PATH, "w")
    SAVE_FILE.write(json.dumps(history))
    SAVE_FILE.close()

def loadHistory():
    global history

    HISTORY_FILE = open(HISTORY_PATH, "r")
    history = json.loads(HISTORY_FILE.read())
    HISTORY_FILE.close()

def clearHistory():
    global history

    history.clear()