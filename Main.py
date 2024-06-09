import discord
import openai
import time
import CababasAI
from PrintColors import TColors
# from dotenv import load_dotenv

# load_dotenv()

import os

## Variables
TOKEN = os.environ['CABABAS_BOT_TOKEN']
COMMANDS = {
    "TEST" : ".test",
    "TALK" : "cab",
    "SYSTEMCONFIG" : "_system",
    "TOGGLE_AI" : "_toggleAI",
    "GET_HISTORY" : "_history",
    "FLASH_HISTORY" : "_flash"
}
WHITELISTED_CHANNELS = {
    "STRIP_CLUB" : 1234653607295455343,
    "TEST" : 1249087177350975510,
    "PRIVATETEST" : 1249174901412200538
}
MODERATORS = {
    "GEODY" : 775117392644407296,
    "WALLIBE" : 1164735044200435734
}
BOT_ID = 1249083390980915201
ERRORS_CHANNEL_ID = 1249121134398668951
COST_CHANNEL_ID = 1249480355690319894

## Code
class Wallibe(discord.Client):
    processing_message = False

    # Initialisation
    async def on_ready(self:discord.Client):
        self.processing_message = False
        print(f'{TColors.B_SUCCESS}> Logged in as {TColors.B_USER}{self.user}{TColors.B_SUCCESS}!{TColors.RESET}')

        try:
            CababasAI.loadHistory()
            print(f'{TColors.B_SUCCESS}> Loaded AI history.{TColors.RESET}')
        except Exception as e:
            await self.log_error_silent("Could not load message history: " + str(e))

        if (CababasAI.enabled):
            try:
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="\"cab\""), status=discord.Status.dnd)
                print(f'{TColors.B_SUCCESS}> Set activity.{TColors.RESET}')
            except Exception as e:
                await self.log_error_silent("Could not set Discord activity: " + str(e))
        else:
            try:
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="AI disabled :("), status=discord.Status.do_not_disturb)
                print(f'{TColors.B_SUCCESS}> Set activity.{TColors.RESET}')
            except Exception as e:
                await self.log_error_silent("Could not set Discord activity: " + str(e))

    # Message reading
    async def on_message(self, message:discord.Message):
        sender:discord.Member = message.author
        content:str = message.content
        channel:discord.TextChannel = message.channel

        if (not message.guild):
            return

        if sender.id != BOT_ID: # Make sure sender isn't the bot itself
            print(f'{TColors.B_RECEIVE}> Message from {TColors.B_USER}{sender}{TColors.B_RECEIVE}: {TColors.B_MESSAGE_CONTENT}"{content}"{TColors.RESET}')

            if content.startswith(COMMANDS["TEST"]):
                sendContent:str = "This is a test!"

                await self.send_msg(channel, sendContent)  
            elif content.startswith(COMMANDS["SYSTEMCONFIG"]):
                if (await self.is_mod(sender.id)):
                    print(f'> {sender} is accessing System Config command.')
                    try:
                        config = content.removeprefix(COMMANDS["SYSTEMCONFIG"] + " ")
                        CababasAI.history.append({"role": "system","content": config})
                        print(f'{TColors.B_SUCCESS}> Successfulyl appended system: {TColors.B_MESSAGE_CONTENT}"{config}"{TColors.RESET}')
                        await self.send_msg(channel, f'i will remember: {config}')
                    except Exception as e:
                        await self.log_error("An error occurred while adding system configuration: " + str(e))

            elif content.startswith(COMMANDS["TOGGLE_AI"]):
                if (await self.is_mod(sender.id)):
                    print(f'> {sender} is accessing AI Toggle command.')
                    CababasAI.enabled = not CababasAI.enabled

                    if (CababasAI.enabled):
                        await self.send_msg(channel, f'ai enabled :3')
                        try:
                            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="\"cab\""), status=discord.Status.dnd)
                            print(f'{TColors.B_SUCCESS}> Set activity.{TColors.RESET}')
                        except Exception as e:
                            await self.log_error_silent("Could not set Discord activity: " + str(e))
                    else:
                        try:
                            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="AI disabled :("), status=discord.Status.do_not_disturb)
                            print(f'{TColors.B_SUCCESS}> Set activity.{TColors.RESET}')
                        except Exception as e:
                            await self.log_error_silent("Could not set Discord activity: " + str(e))
                        await self.send_msg(channel, f'ai disabled :3')

            elif content.startswith(COMMANDS["GET_HISTORY"]):
                if (await self.is_mod(sender.id)):
                    print(f'> {sender} is accessing view history command.')
                    try:
                        dm:discord.DMChannel = await sender.create_dm()

                        history_file = open(CababasAI.HISTORY_PATH, "rb")

                        ctime:str = str(time.time())

                        await dm.send("```\nHistory Backup " + ctime + "\n```", file=discord.File(history_file, "historybackup"+ctime+".json"))
                    except Exception as e:
                        await self.log_error(channel, "Error while sending AI history: " + str(e))

            elif content.startswith(COMMANDS["FLASH_HISTORY"]):
                if (await self.is_mod(sender.id)):
                    print(f'> {sender} is accessing flash history command.')

                    try:
                        CababasAI.clearHistory()
                        CababasAI.saveHistory()
                        await self.send_msg(channel, f'Memory flashed :3')
                    except Exception as e:
                        await self.log_error(channel, "Error while flashing AI history: " + str(e))

            elif content.startswith(COMMANDS["TALK"] + " "):
                # if self.processing_message:
                #     return
                # self.processing_message = True

                for c in WHITELISTED_CHANNELS:
                    if channel.id == WHITELISTED_CHANNELS[c]:
                        print(f'{TColors.B_SUCCESS}> Channel is whitelisted for AI use!{TColors.RESET}')
                        await self.response_ai(channel, content.removeprefix(COMMANDS["TALK"] + " "))
                        break

                # self.processing_message = False

            print("> \n")

    async def response_ai(self, channel:discord.TextChannel, content:str):
        try:
            async with channel.typing():
                if (channel.id == WHITELISTED_CHANNELS["PRIVATETEST"]):
                    response, cost = CababasAI.process_response_ai_flag(content, True)
                else:
                    response, cost = CababasAI.process_response_ai(content)

            await self.send_msg(channel, response)
            await self.log_cost(cost)

        except openai.RateLimitError as e1:
            await self.send_msg(channel, "Cababas being rate limited ):")
        except openai.OpenAIError as e2:
            await self.log_error(channel, f'An OpenAIError occurred: {str(e2)}')
        except Exception as e3:
            await self.log_error(channel, f'An error occurred: {str(e3)}')

    # Function for sending messages alone
    async def send_msg(self, channel:discord.TextChannel, message:str):
        print(f'{TColors.B_SEND}> Sending: {TColors.B_MESSAGE_CONTENT}"{message}"{TColors.RESET}')
        await channel.send(message)

    async def log_cost(self, cost:float):
        cost_channel:discord.TextChannel = self.get_channel(COST_CHANNEL_ID)
        if (cost > CababasAI.RECOMMENDED_COST):
            await cost_channel.send(f'`WARNING: COST OVER RECOMMENDED ${CababasAI.RECOMMENDED_COST} AMOUNT: CHARGED ${cost}')

    async def log_error(self, channel:discord.TextChannel, error:str):
        await self.log_error_silent(error)
        await self.send_msg(channel, "`erm tell wallibe to check logs :3`")

    async def log_error_silent(self, error:str):
        error_channel:discord.TextChannel = self.get_channel(ERRORS_CHANNEL_ID)
        print(f'{TColors.B_WARNING}> Error: {TColors.B_MESSAGE_CONTENT}"\n{error}\n"{TColors.RESET}')
        await error_channel.send("```\n" + error + "\n```")

    async def is_mod(self, user_id:int):
        for mod in MODERATORS:
            if user_id == MODERATORS[mod]:
                return True
        return False


# Bot startup
intents = discord.Intents.default()
intents.reactions = True
intents.message_content = True

client = Wallibe(intents=intents)
client.run(TOKEN)