import discord
import asyncio
import time
import random
from os import path
from discord import app_commands
from discord import Activity
from discord import ActivityType
from discord import Status
from discord import User
from discord import ui
from typing import Any
from random import choice
from PIL.Image import Image

import console as cons
import os_manager
import rng
import faces
import pfp
import voice_chat
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

LOVE_GIF = 'https://cdn.discordapp.com/attachments/1249693861115334678/1253673044379963422/CababasLove.gif'
CABABAS_ASCII_PATH = 'resources/Images/cababas.txt'

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
        
        self.ready = True
        
        # Syncing slash commands
        cons.task(f'Syncing the command tree...')
        try:
            for guild in self.get_whitelisted_guilds():
                await self.tree.sync(guild=guild)
            cons.task_completed(f'Command tree synced to {str(len(os_manager.WHITELISTED_GUILDS))} guild(s).')
        except Exception as e:
            cons.error(f'An error occurred while syncing app commands: {str(e)}. Bot will continue to run.')
        
        cons.success(f'Successfully set up the server. Bot is ready for use.')
        
        while True:
            try:
                guild = self.get_guild(os_manager.VC_GUILD)
                if guild != None:
                    await self.auto_handle_voice_chats(guild=guild)
            except Exception as e:
                cons.error(f'Could not determine if the bot should leave or join a voice channel: {str(e)}')
                await voice_chat.leave(self)
            
            try: # Cycle through random presences
                random_activity = await self.generate_random_activity()
                await self.change_presence(status=choice(DISCORD_STATUS), activity=random_activity)
            except Exception as e:
                cons.error(f'Could not generate random activity: {str(e)}')
                
            await asyncio.sleep(random.randint(600,1800))
            # await asyncio.sleep(10)
    
    async def auto_handle_voice_chats(self, guild:discord.Guild):
        channels = guild.voice_channels
        
        if voice_chat.check_if_in_vc(self):
            for channel in channels:
                if not voice_chat.check_if_in_vc(self):
                    break
                if (await voice_chat.should_leave_vc(channel=channel)):
                    await voice_chat.leave(self, channel.id)
        else:
            for channel in channels:
                if voice_chat.check_if_in_vc(self):
                    break
                if (await voice_chat.should_join_vc(channel=channel)):
                    await voice_chat.join(self, channel.id)
                

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

        try:
            if not content.lower().startswith('cab '):
                return
            
            if is_dm:
                self.debounce.remove(sender.id)
                await message.reply('sowwy :( no dms pls',delete_after=5.0)
                return
            
            if not self.enabled:
                self.debounce.remove(sender.id)
                await message.reply('sowwy :( commands disable rn',delete_after=5.0)
                return

            async with channel.typing():
                response, is_success = await generate_response(sender, message)
            
                if is_success:
                    await message.reply(response,mention_author=False)
                else:
                    await message.reply(response,mention_author=False,delete_after=10.0) 
        except Exception as e:
             self.debounce.remove(sender.id)
             await message.reply(f'`bad error occurred {choice(faces.CONFUSED)}`',mention_author=False)
             cons.error(str(e))
           
        self.debounce.remove(sender.id)
        
    def create_slash_commands(self) -> None:
        developer_guilds = [discord.Object(os_manager.DEVELOPER_GUILD)]
        whitelisted_guilds = self.get_whitelisted_guilds()
        
        @self.tree.command(
                name='toggle-commands',
                description='Toggle commands on/off GLOBALLY. Only selected users are allowed to user this.',
                guilds=developer_guilds,
                extras={
                    'on':True,
                    'off':False
                }
        )
        async def toggle_commands(interaction:discord.Interaction, choice:bool):
            if not await self.check_flags(interaction,True): return            
            try:
                self.enabled = choice

                cons.log(f'{interaction.user.name}-({interaction.user.id}) is accessing "toggle-commands" with a status of {str(choice)}')
                await interaction.response.send_message(f'Command status is now [{choice}]', ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f'`bad error occurred {choice(faces.CONFUSED)}`')
                cons.error(str(e))
                        
        @self.tree.command(
                name='toggle-commands-ai',
                description='Toggle AI on/off GLOBALLY. Only selected users are allowed to user this.',
                guilds=developer_guilds,
                extras={
                    'on':True,
                    'off':False
                }
        )
        async def toggle_commands_ai(interaction:discord.Interaction, choice:bool):
            if not await self.check_flags(interaction,True): return            
            try:
                await os_manager.resources.settings.ai_settings.set_enabled(choice)

                cons.log(f'{interaction.user.name}-({interaction.user.id}) is accessing "toggle-commands-ai" with a status of {str(choice)}')
                await interaction.response.send_message(f'AI status is now [{choice}]', ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f'`bad error occurred {choice(faces.CONFUSED)}`')   
                cons.error(str(e))
                            
        @self.tree.command(
                name='backup-resources',
                description='Create a backup. Only selected users are allowed to user this.',
                guilds=developer_guilds,
                extras={
                    'dm'
                }
        )
        async def backup_resources(interaction:discord.Interaction, dm:bool|None=False):
            if not await self.check_flags(interaction,True): return
            user = interaction.user            
            try:
                await self.command_backup_resource(interaction,dm)
            except Exception as e:
                await interaction.response.send_message(f'`bad error occurred {choice(faces.CONFUSED)}`')   
                cons.error(str(e))
                        
        @self.tree.command(
                name='join-voice',
                description='Join a voice channel. Only selected users are allowed to user this.',
                guilds=developer_guilds,
                extras={
                    'Channel ID'
                }
        )
        async def join_voice(interaction:discord.Interaction, channel_id:str):
            if not await self.check_flags(interaction,True): return
            self.debounce.append(interaction.user.id)
            
            if voice_chat.check_if_in_vc(self):
                self.debounce.remove(interaction.user.id)
                await interaction.response.send_message(f'me alweady in voice channel {choice(faces.SAD)}',ephemeral=True)   
                return
            
            channel_id:int
            try:
                channel_id = int(channel_id)
            except Exception:
                self.debounce.remove(interaction.user.id)
                await interaction.response.send_message(f'pls give valid id {choice(faces.SAD)}',ephemeral=True)  
                return
            try:
                await voice_chat.join(self, channel_id)
                await interaction.response.send_message(f'joined {choice(faces.HAPPY)}',ephemeral=True)  
            except Exception as e:
                self.debounce.remove(interaction.user.id)
                await interaction.response.send_message(f'`bad error occurred {choice(faces.CONFUSED)}` {str(e)}',ephemeral=True)   
                cons.error(f'Error while joining a voice channel: {str(e)}')
                return
                
            self.debounce.remove(interaction.user.id)
            
        @self.tree.command(
                name='clear-debounce',
                description='Clears the debounce list. Only selected users are allowed to user this.',
                guilds=developer_guilds
        )
        async def clear_debounce(interaction:discord.Interaction):            
            self.debounce.clear()
            cons.log(f'Debounce cleared by {interaction.user.name} ({interaction.user.id})')
            await interaction.response.send_message(f'cleared debounce! {choice(faces.HAPPY)}',ephemeral=True)  
            
        @self.tree.command(
                name='leave-voice',
                description='Leave a voice channel. Only selected users are allowed to user this.',
                guilds=developer_guilds,
                extras={
                    "id"
                }
        )
        async def leave_voice(interaction:discord.Interaction,id:str|None=""):
            if not await self.check_flags(interaction,True): return
            self.debounce.append(interaction.user.id)
            
            if not voice_chat.check_if_in_vc(self):
                await interaction.response.send_message(f'me not in voice channel {choice(faces.SAD)}',ephemeral=True)   
                self.debounce.remove(interaction.user.id)
                return
            
            channel_id = None
            try:
                channel_id = int(id)
            except Exception:
                channel_id = None
            
            try:
                await voice_chat.leave(self, channel_id)
                await interaction.response.send_message(f'left {choice(faces.HAPPY)}',ephemeral=True)  
            except Exception as e:
                self.debounce.remove(interaction.user.id)
                await interaction.response.send_message(f'`bad error occurred {choice(faces.CONFUSED)}` {str(e)}',ephemeral=True)   
                cons.error(str(e))
                return
                
            self.debounce.remove(interaction.user.id)

        @self.tree.command(
                name='rng',
                description='Randomly roll a rank.',
                guilds=whitelisted_guilds
        )
        async def rng_command(interaction:discord.Interaction):
            await self.command_rng(interaction=interaction)

        @self.tree.command(
                name='rng-view-rank',
                description='View your current rank.',
                guilds=whitelisted_guilds,
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
                self.debounce.remove(interaction.user.id)
                await interaction.response.send_message(f'someting go wrong {choice(faces.SAD)} pls try again later', ephemeral=True, delete_after=10.0)    
                cons.error(f'Error while sending {user.name} ({user.id}) their RNG rank: {str(e)}')
                return
            self.debounce.remove(interaction.user.id)
            
        @self.tree.command(
                name='rng-ranks-list',
                description='View all the aquireable ranks and their chances of being rolled.',
                guilds=whitelisted_guilds
        )
        async def rng_browse_ranks(interaction:discord.Interaction):
            if not await self.check_flags(interaction,False): return
            self.debounce.append(interaction.user.id)
            
            user = interaction.user

            try:
                embed = await rng.browse_ranks(user.id)
                await interaction.response.send_message(embed=embed,ephemeral=True)    
            except Exception as e:
                self.debounce.remove(interaction.user.id)
                await interaction.response.send_message('someting go wrong :( pls try again later', ephemeral=True, delete_after=10.0)    
                cons.error(f'Error while {user.name} ({user.id}) was browsing RNG ranks: {str(e)}')
                return
                
            self.debounce.remove(user.id)
            
        @self.tree.command(
                name='love',
                description='Cababas love!',
                guilds=whitelisted_guilds
        )
        async def cababas_love(interaction:discord.Interaction):
            if not await self.check_flags(interaction,False): return
            self.debounce.append(interaction.user.id)
            
            try:
                await interaction.response.send_message(content=LOVE_GIF) 
            except Exception as e:
                self.debounce.remove(interaction.user.id)
                await interaction.response.send_message(f'`bad error occurred {choice(faces.CONFUSED)}`')   
                cons.error(str(e))
                return
               
            self.debounce.remove(interaction.user.id)
            
        @self.tree.command(
                name='murder',
                description='Murder someone >:)',
                guilds=whitelisted_guilds,
                extras={
                    'Victim'
                }
        )
        async def cababas_murder(interaction:discord.Interaction, victim:User):
            if not await self.check_flags(interaction,False): return
            self.debounce.append(interaction.user.id)
            
            try:
                pfp_img:Image = pfp.murder(victim,True if victim.id == self.user.id else False)
                await interaction.response.send_message(content=f'<@{interaction.user.id}> make me kill <@{victim.id}> {choice(faces.SAD)}',file=pfp.image_to_file(pfp_img),silent=True)
            except Exception as e:
                self.debounce.remove(interaction.user.id)
                cons.error(f'Error while running murder command: {str(e)}')
                return
               
            self.debounce.remove(interaction.user.id)
            
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
        
    async def command_backup_resource(self, interaction:discord.Interaction, dm:bool|None=False) -> None:
        try:
            user = interaction.user
            
            archive_path = f'{str(await os_manager.resources.create_backup())}.zip'
        
            attachement_name = f'backup-{round(time.time())}.zip'
            if dm:
                user_dm = await user.create_dm()
                await user_dm.send(f'Backup created: ', file=discord.File(fp=archive_path,filename=attachement_name))
            
            backup_channel:discord.TextChannel = self.get_channel(1249484273916837889)
            await backup_channel.send(f'```\nBackup created by {user.name} ({user.id})\n```', file=discord.File(fp=archive_path,filename=attachement_name))
        except Exception as e:
            await interaction.response.send_message(f'An Python error occurred while backing up: {str(e)}',ephemeral=True)
            cons.error(str(e))
            return

        await interaction.response.send_message(f'Backup created.',ephemeral=True,delete_after=20)

    # Stop the bot
    async def stop(self) -> None:
        cons.error(f'Terminating process...')
        exit(0)
        
    async def check_flags(self, interaction:discord.Interaction, is_manager_command:bool|None=False) -> bool:
        if not self.ready:
            await interaction.response.send_message('hold on pls', ephemeral=True, delete_after=10.0)
            return False
            
        if not self.enabled and not is_manager_command:
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
        
    async def generate_random_activity(self) -> Activity:
        random_type = choice(DISCORD_ACTIVITY_TYPES)
        random_names = await os_manager.resources.activities.getNames(random_type)
        return Activity(type=random_type,name=choice(random_names))

    # Get an array of the whitelisted guilds
    def get_whitelisted_guilds(self) -> list[discord.Object]:
        result = []
        for id in os_manager.WHITELISTED_GUILDS.values():
            result.append(discord.Object(id=id))
        return result
    
class rng_roll_view(ui.View):
    def __init__(self,client:CababasBot, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.client = client
            
    @ui.button(label=f're-roll {choice(faces.HAPPY)}',style=discord.ButtonStyle.blurple)
    async def button_callback(self,interaction:discord.Interaction,button:ui.Button):
        # button.disabled = True
        # button.style = discord.ButtonStyle.gray
        # button.label = "Expired"
        # await interaction.response.edit_message(view=self)
        await self.client.command_rng(interaction)