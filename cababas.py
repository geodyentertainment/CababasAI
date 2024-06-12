from typing import Any
import discord
from time import sleep

import console as cons
import os_manager

class CababasBot(discord.Client):
    ready:bool # Flag determining if the command tree is ready or not
    tree:discord.app_commands.CommandTree # The command tree

    def __init__(self, **options: Any) -> None:
        cons.task(f'Initiating bot...')
        # Setting ready flag to false
        self.ready = False
        self.enabled = True

        # Creating intents
        intents = discord.Intents.default()
        intents.message_content = True

        # Calling the super-constructor to createt the session
        super().__init__(intents=intents, **options)
        cons.log(f'Bot initiated.       ')

        cons.task(f'Creating tree...')
        # Create command tree (for slash commands)
        self.tree = discord.app_commands.CommandTree(self)
        @self.tree.command(
            name="enable",
            description="Enable the bot's commands GLOBALLY. Only selected users can use this.",
            guilds=self.get_whitelisted_guilds()
        )
        async def enable_commands(interaction:discord.Interaction):
            if not self.ready: return

            if await os_manager.resources.settings.is_manager(interaction.user.id):
                self.enabled = True
                await interaction.response.send_message(content='commands enable :3',delete_after=3.0)
                return
            
            await interaction.response.send_message(content='u cant use dis :(',delete_after=3.0)

        @self.tree.command(
            name="disable",
            description="Disable the bot's commands GLOBALLY. Only selected users can use this.",
            guilds=self.get_whitelisted_guilds()
        )
        async def disable_commands(interaction:discord.Interaction):
            if not self.ready: return

            if await os_manager.resources.settings.is_manager(interaction.user.id):
                self.enabled = False
                await interaction.response.send_message(content='commands disable :3', delete_after=3.0)
                return

            await interaction.response.send_message(content='u cant use dis :(', delete_after=3.0)

        cons.log(f'Command tree created.')
        
    # Bot is online
    async def on_ready(self):
        cons.success(f'Logged in as {self.user}.\n')
        # Creating any possible missing files
        cons.task(f'Updating resource files...')
        try:
            await os_manager.resources.update_files()
            cons.task_completed(f'Resource files updated.               ')
        except Exception as e:
            cons.error(f'An error occurred while updating resource files: {str(e)}.')
            self.ready = False
            await self.stop()
            return
        
        # Syncing slash commands
        cons.task(f'Syncing the command tree...')
        try:
            await self.tree.sync(guild=discord.Object(id=1249087176592068659))
            cons.task_completed(f'Command tree synced to {str(len(os_manager.WHITELISTED_GUILDS))} guild(s).')
        except Exception as e:
            cons.error(f'An error occurred while syncing app commands: {str(e)}.')
            self.ready = False
            await self.stop()
            return
        
        self.ready = True
        cons.line()
        cons.success(f'Successfully set up the server. Bot is ready for use.')

    # Received message
    async def on_message(self, message:discord.Message):
        if not self.ready: return # Ignore the following if the bot has not been set up yet.

        sender = message.author
        channel = message.channel
        is_dm = (message.guild == None)

        if message.clean_content.startswith('cab'):
            if not self.enabled:
                message.reply('sowwy :( commands disable rn',delete_after=5.0)
            return

    # Stop the bot
    async def stop(self) -> None:
        cons.error(f'Terminating process...')
        exit(0)

    # Get an array of the whitelisted guilds
    def get_whitelisted_guilds(self) -> list[discord.Object]:
        result = []
        for id in os_manager.WHITELISTED_GUILDS.values():
            result.append(discord.Object(id=id))
        return result