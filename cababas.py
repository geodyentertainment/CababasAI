import discord
from discord import app_commands
from typing import Any

import console as cons
import os_manager
import rng
from ai import generate_response

class CababasBot(discord.Client):
    ready:bool # Flag determining if the command tree is ready or not
    enable:bool
    tree:app_commands.CommandTree # The command tree
    debounce = []

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
        self.tree = app_commands.CommandTree(self)

        self.create_slash_commands()

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
            for guild in self.get_whitelisted_guilds():
                await self.tree.sync(guild=guild)
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
        content = message.clean_content
        guild = message.guild

        if content.startswith('cab'):
            if is_dm:
                await message.reply('sowwy :( no dms pls',delete_after=5.0)
                return
            
            if not self.enabled:
                await message.reply('sowwy :( commands disable rn',delete_after=5.0)
                return
        
            async with channel.typing():
                response, is_success = await generate_response(content, sender, guild.id)
            
                if is_success:
                    await message.reply(response,mention_author=False)
                else:
                    await message.reply(response,mention_author=False,delete_after=10.0)    
            return
        
    def create_slash_commands(self) -> None:
        @self.tree.command(
                name='toggle-commands',
                description='Toggle commands on/off GLOBALLY.',
                guilds=self.get_whitelisted_guilds(),
                extras={
                    'on':True,
                    'off':False
                }
        )
        async def toggle_commands(interaction:discord.Interaction, choice:bool):
            if not self.ready:
                await interaction.response.send_message('hold on pls', ephemeral=True)
                return
            
            if interaction.user.id in self.debounce:
                await interaction.response.send_message('u alweady running command', ephemeral=True, delete_after=5.0)
                return
            self.debounce.append(interaction.user.id)

            if await os_manager.resources.settings.discord.is_manager(interaction.user.id):
                self.enabled = choice

                cons.log(f'{interaction.user.name}-({interaction.user.id}) is accessing "toggle-commands" with a status of {str(choice)}')
                await interaction.response.send_message(f'Command status is now [{choice}]', ephemeral=True)
            else:
                await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            self.debounce.remove(interaction.user.id)

        @self.tree.command(
                name='rng',
                description='Randomly roll a rank.',
                guilds=self.get_whitelisted_guilds()
        )
        async def rng_command(interaction:discord.Interaction):
            if not self.ready:
                await interaction.response.send_message('hold on pls', ephemeral=True)
                return
            
            if not self.enabled:
                await interaction.response.send_message('sowwy dev say no command rn :(', ephemeral=True)
                return
            
            if interaction.user.id in self.debounce:
                await interaction.response.send_message('u alweady running command', ephemeral=True, delete_after=5.0)
                return
            self.debounce.append(interaction.user.id)
            
            user = interaction.user

            try:
                current_roll, is_new_rank = await rng.user_roll(user.id)
            except Exception as e:
                await interaction.response.send_message('someting go wrong :( pls try again later', ephemeral=True, delete_after=10.0)    
                cons.error(f'Error while {user.name} ({user.id}) was rolling RNG: {str(e)}')
                self.debounce.remove(user.id)
                return
            
            try:
                if is_new_rank:
                    await interaction.response.send_message(f'✨ WOWIE :D ✨ u roll new rank `{current_roll}` ({str(round(rng.get_chance(current_roll)*100, 2))}%)') 
                    self.debounce.remove(user.id)
                    return
                await interaction.response.send_message(f'u roll `{current_roll}` ({str(round(rng.get_chance(current_roll)*100,2))}%)',ephemeral=True,delete_after=20.0)  
            except discord.HTTPException as e:
                cons.error(f'Error sending RNG results of [{current_roll}] to {user.name} ({user.id}): {str(e)}')
            self.debounce.remove(user.id)

        @self.tree.command(
                name='rng-view-rank',
                description='View your current rank.',
                guilds=self.get_whitelisted_guilds()
        )
        async def rng_view_rank(interaction:discord.Interaction):
            if not self.ready:
                await interaction.response.send_message('hold on pls', ephemeral=True, delete_after=10.0)
                return
            
            if not self.enabled:
                await interaction.response.send_message('sowwy dev say no command rn :(', ephemeral=True, delete_after=10.0)
                return
            
            if interaction.user.id in self.debounce:
                await interaction.response.send_message('u alweady running command', ephemeral=True, delete_after=10.0)
                return
            self.debounce.append(interaction.user.id)
            
            user = interaction.user

            try:
                rank = await rng.get_user_rank(user.id)
                await interaction.response.send_message(f'ur rank is `{rank}` ({str(round(rng.get_chance(rank)*100, 2))}%)', ephemeral=True)    
            except Exception as e:
                await interaction.response.send_message('someting go wrong :( pls try again later', ephemeral=True, delete_after=10.0)    
                cons.error(f'Error while sending {user.name} ({user.id}) their RNG rank: {str(e)}')
            self.debounce.remove(user.id)
            
        @self.tree.command(
                name='rng-ranks-list',
                description='View all the aquireable ranks and their chances of being rolled.',
                guilds=self.get_whitelisted_guilds()
        )
        async def rng_browse_ranks(interaction:discord.Interaction):
            if not self.ready:
                await interaction.response.send_message('hold on pls', ephemeral=True, delete_after=10.0)
                return
            
            if not self.enabled:
                await interaction.response.send_message('sowwy dev say no command rn :(', ephemeral=True, delete_after=10.0)
                return
            
            if interaction.user.id in self.debounce:
                await interaction.response.send_message('u alweady running command', ephemeral=True, delete_after=10.0)
                return
            self.debounce.append(interaction.user.id)
            
            user = interaction.user

            try:
                embed = await rng.browse_ranks(user.id)
                await interaction.response.send_message(embed=embed,ephemeral=True)    
            except Exception as e:
                await interaction.response.send_message('someting go wrong :( pls try again later', ephemeral=True, delete_after=10.0)    
                cons.error(f'Error while {user.name} ({user.id}) was browsing RNG ranks: {str(e)}')
            self.debounce.remove(user.id)

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