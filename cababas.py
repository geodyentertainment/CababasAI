import discord
import asyncio
from discord import app_commands
from discord import Activity
from discord import ActivityType
from discord import Status
from discord import User
from discord import ui
from typing import Any
from random import choice

import console as cons
import os_manager
import rng
import faces
from ai import generate_response
from rng import chance_to_string

DISCORD_STATUS = [
    Status.online,
    Status.dnd,
    Status.idle
]

DISCORD_ACTIVITY_TYPES = [
    ActivityType.playing,
    ActivityType.listening,
    ActivityType.watching,
    ActivityType.competing,
    ActivityType.streaming
]

DISCORD_ACTIVITY_PLAYING = [
    'Eating Simulator',
    'Roblox',
    'Genshin Impact',
    'Honkai: Star Rail',
    'Mario Kart',
    'with food'
]

DISCORD_ACTIVITY_LISTENING = [
    'Spotify',
    'Laufey',
    'Skibidi Fortnite',
    'Mahler',
    'Food ASMR'
]

DISCORD_ACTIVITY_WATCH = [
    'YouTube',
    'Discord',
    'EOM Robotics',
    'monicaand_clairesprobaking',
    'Food ASMR'
]

DISCORD_ACTIVITY_COMPETING = [
    'FRC',
    'Eating Competition'
]

DISCORD_ACTIVITY_STREAMING = [
    'Eating Simulator',
    'Roblox',
    'Genshin Impact',
    'Honkai: Star Rail'
    'Mario Kart',
    'with food',
    'YouTube',
    'Discord',
    'homework',
    'CS',
    'VSCode'
]

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
        
        await self.change_presence(status=discord.Status.invisible, activity=discord.Activity(name='Loading...',type=discord.ActivityType.playing))
        
        cons.task(f'Updating resource files...')
        try:
            await os_manager.resources.update_files()
            cons.task_completed(f'Resource files updated.               ')
        except Exception as e:
            cons.error(f'An error occurred while updating resource files: {str(e)}. Bot will be stopped.')
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
            cons.error(f'An error occurred while syncing app commands: {str(e)}. Bot will continue to run.')
        
        self.ready = True
        cons.success(f'Successfully set up the server. Bot is ready for use.')
        
        # Cycling through random presences
        while True:
            await self.change_presence(status=choice(DISCORD_STATUS), activity=self.generate_random_activity())
            await asyncio.sleep(600)

    # Received message
    async def on_message(self, message:discord.Message):
        if not self.ready: return # Ignore the following if the bot has not been set up yet.

        sender = message.author
        channel = message.channel
        is_dm = (message.guild == None)
        content = message.clean_content
        
        if sender.id == self.user.id:
            return
        
        if sender.id in self.debounce:
            await message.reply(f'u alweady running command {choice(faces.CONFUSED)}',delete_after=5.0)
            return
        
        self.debounce.append(sender.id)

        if content.lower().startswith('cab '):
            if is_dm:
                await message.reply('sowwy :( no dms pls',delete_after=5.0)
                self.debounce.remove(sender.id)
                return
            
            if not self.enabled:
                await message.reply('sowwy :( commands disable rn',delete_after=5.0)
                self.debounce.remove(sender.id)
                return

            async with channel.typing():
                response, is_success = await generate_response(sender, message)
            
                if is_success:
                    await message.reply(response,mention_author=False)
                else:
                    await message.reply(response,mention_author=False,delete_after=10.0)    
        self.debounce.remove(sender.id)
        
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
            if not await self.check_flags(interaction,True): return
            self.debounce.append(interaction.user.id)
            
            self.enabled = choice

            cons.log(f'{interaction.user.name}-({interaction.user.id}) is accessing "toggle-commands" with a status of {str(choice)}')
            await interaction.response.send_message(f'Command status is now [{choice}]', ephemeral=True)
            self.debounce.remove(interaction.user.id)
            
        @self.tree.command(
                name='toggle-commands-ai',
                description='Toggle AI on/off GLOBALLY.',
                guilds=self.get_whitelisted_guilds(),
                extras={
                    'on':True,
                    'off':False
                }
        )
        async def toggle_commands_ai(interaction:discord.Interaction, choice:bool):
            if not await self.check_flags(interaction,True): return
            self.debounce.append(interaction.user.id)
            
            await os_manager.resources.settings.ai_settings.set_enabled(choice)

            cons.log(f'{interaction.user.name}-({interaction.user.id}) is accessing "toggle-commands-ai" with a status of {str(choice)}')
            await interaction.response.send_message(f'AI status is now [{choice}]', ephemeral=True)
            self.debounce.remove(interaction.user.id)

        @self.tree.command(
                name='rng',
                description='Randomly roll a rank.',
                guilds=self.get_whitelisted_guilds()
        )
        async def rng_command(interaction:discord.Interaction):
            await self.command_rng(interaction=interaction)

        @self.tree.command(
                name='rng-view-rank',
                description='View your current rank.',
                guilds=self.get_whitelisted_guilds(),
                extras={
                    'user'
                }
        )
        async def rng_view_rank(interaction:discord.Interaction, user:User|None):
            if not await self.check_flags(interaction,False): return
            self.debounce.append(interaction.user.id)
            
            if user == None:
                user = interaction.user

            try:
                rank = await rng.get_user_rank(user.id)
                await interaction.response.send_message(f'<@{user.id}> rank is `{rank}` ({chance_to_string(rng.get_chance(rank)*100)}%)', ephemeral=True,silent=True)    
            except Exception as e:
                await interaction.response.send_message(f'someting go wrong {choice(faces.SAD)} pls try again later', ephemeral=True, delete_after=10.0)    
                cons.error(f'Error while sending {user.name} ({user.id}) their RNG rank: {str(e)}')
            self.debounce.remove(interaction.user.id)
            
        @self.tree.command(
                name='rng-ranks-list',
                description='View all the aquireable ranks and their chances of being rolled.',
                guilds=self.get_whitelisted_guilds()
        )
        async def rng_browse_ranks(interaction:discord.Interaction):
            if not await self.check_flags(interaction,False): return
            self.debounce.append(interaction.user.id)
            
            user = interaction.user

            try:
                embed = await rng.browse_ranks(user.id)
                await interaction.response.send_message(embed=embed,ephemeral=True)    
            except Exception as e:
                await interaction.response.send_message('someting go wrong :( pls try again later', ephemeral=True, delete_after=10.0)    
                cons.error(f'Error while {user.name} ({user.id}) was browsing RNG ranks: {str(e)}')
            self.debounce.remove(user.id)
            
    async def command_rng(self, interaction:discord.Interaction) -> None:
        if not await self.check_flags(interaction,False): return
            
        view = rng_roll_view(client=self)
                
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
                await interaction.channel.send(f'✨ WOWIE {choice(faces.HAPPY)} ✨ <@{user.id}> rolled new rank `{current_roll}` ({chance_to_string(rng.get_chance(current_roll)*100)}%)') 
                await interaction.response.send_message(ephemeral=True,delete_after=10.0,view=view) 
                self.debounce.remove(user.id)
                return
            await interaction.response.send_message(f'u roll `{current_roll}` ({chance_to_string(rng.get_chance(current_roll)*100)}%)',ephemeral=True,delete_after=10.0,view=view)  
        except discord.HTTPException as e:
            cons.error(f'Error sending RNG results of [{current_roll}] to {user.name} ({user.id}): {str(e)}')
        self.debounce.remove(user.id)

    # Stop the bot
    async def stop(self) -> None:
        cons.error(f'Terminating process...')
        exit(0)
        
    async def check_flags(self, interaction:discord.Interaction, is_manager_command:bool) -> bool:
        if not self.ready:
                await interaction.response.send_message('hold on pls', ephemeral=True, delete_after=10.0)
                return False
            
        if not self.enabled:
            await interaction.response.send_message(f'sowwy dev say no command rn {choice(faces.SAD)}', ephemeral=True, delete_after=10.0)
            return False
        
        if interaction.user.id in self.debounce:
            await interaction.response.send_message(f'u alweady running command {choice(faces.CONFUSED)}', ephemeral=True, delete_after=10.0)
            return False
        
        if is_manager_command:
            if not await os_manager.resources.settings.discord.is_manager(interaction.user.id):
                await interaction.response.send_message(f'u no alowed to use dis {choice(faces.SAD)}', ephemeral=True, delete_after=10.0)
                return False
        
        return True
        
    def generate_random_activity(self) -> Activity:
        random_type = choice(DISCORD_ACTIVITY_TYPES)
        if random_type == ActivityType.playing:
            return Activity(type=random_type,name=choice(DISCORD_ACTIVITY_PLAYING))
        elif random_type == ActivityType.listening:
            return Activity(type=random_type,name=choice(DISCORD_ACTIVITY_LISTENING))
        elif random_type == ActivityType.watching:
            return Activity(type=random_type,name=choice(DISCORD_ACTIVITY_WATCH))
        elif random_type == ActivityType.competing:
            return Activity(type=random_type,name=choice(DISCORD_ACTIVITY_COMPETING))
        elif random_type == ActivityType.streaming:
            return Activity(type=random_type,name=choice(DISCORD_ACTIVITY_STREAMING))
        return Activity(type=random_type,name='stuff')

    # Get an array of the whitelisted guilds
    def get_whitelisted_guilds(self) -> list[discord.Object]:
        result = []
        for id in os_manager.WHITELISTED_GUILDS.values():
            result.append(discord.Object(id=id))
        return result
    
class rng_roll_view(ui.View):
    def __init__(self,client:CababasBot,face:str, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.client = client
            
    @ui.button(label=f're-roll {choice(faces.HAPPY)}',style=discord.ButtonStyle.blurple)
    async def button_callback(self,interaction:discord.Interaction,button:ui.Button):
        # button.disabled = True
        # button.style = discord.ButtonStyle.gray
        # button.label = "Expired"
        # await interaction.response.edit_message(view=self)
        await self.client.command_rng(interaction)