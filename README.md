# Cababas AI
A Cameluo Cababas Discord bot that runs an **AI chatbot**, and other Cababas themed commands.

## Developer Overview
### How To Run
#### Install Python
You need to have Python installed on your machine in order to compile this project.
The installations can be found [here](https://www.python.org/downloads/).

To check the current python version, run the following command in your terminal:
```commandline
py
```

#### Install the required dependencies
Dependencies are listed in the requirements.txt file. These can be installed using pip.

```commandline
pip install -r requirements.txt
```

#### Set Up Environment variables
A `.env` file needs to be created under the main directory. This file should contain the following variables:

`OPENAI_CABABAS_API_KEY` - OpenAI API key **(do not share this)**

`OPENAI_CABABAS_PROJECT` - OpenAI project ID **(do not share this)**

`OPENAI_CABABAS_ORGANIZATION` - OpenAI organization ID **(do not share this)**

`OPENAI_CABABAS_MODEL` - The OpenAI model to run.

`DISCORD_CABABAS_TOKEN` - Your Discord bot's token. **(do not share this)**

`ERROR_CHANNEL_ID` - The ID of the channel where the bot will attempt to log errors to.

Here's an example of what this might look like *(these are not real keys and IDs)*:

`Located in /.../CababasAI/.env`
```
OPENAI_CABABAS_API_KEY=sk-proj-ewrh3fhwef83hkfhdw8234fgsdf
OPENAI_CABABAS_PROJECT=proj_HdsANFiHJFEWN83HFJNsnda
OPENAI_CABABAS_ORGANIZATION=org-jhsDSnbwkSDkfmF
OPENAI_CABABAS_MODEL=gpt-3.5-turbo
DISCORD_CABABAS_TOKEN=MT3rwjSDKFoemhkn95mdsoamekgo49nDiasfesmaige
ERROR_CHANNEL_ID=349572937591652
```

#### Running The Startup File
Navigate to the main directory, and run the `start_client.py` file.
```commandline
py start_client.py
```

#### Configuring Bot Settings
Once the bot has been started, a new directory called `config` should be created. There is a `json` file containing bot settings. Some of these can be changed using integrated bot commands, but others will have to be manually changed in this file.

Here's what the file content might look like:
```json
{
  "discord": {
    "enabled": true,
    "managers": {
      "Geody": 775117392644407296,
      "Wallibe": 1164735044200435734
    }, 
    "commands_whitelisted_guilds": {}, 
    "ai_whitelisted_guilds": {}
  }, 
  "ai": {
    "enabled": false,
    "history_memory": 11,
    "temperature": 0.79,
    "top_p": 1,
    "logit_bias": {
      "1734": -100
    },
    "seed": 572875094,
    "get_max_prompt_tokens": 40,
    "max_completion_tokens": 20,
    "frequency_penalty": 0,
    "presence_penalty": 0
  }
}
```

### How Does The Bot Work?
WIP