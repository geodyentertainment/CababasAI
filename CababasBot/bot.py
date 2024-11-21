import discord
from discord import Client, Intents, InteractionResponded, Member, Status, Guild, NotFound, HTTPException, InteractionResponse, Interaction, User
from discord.app_commands import CommandTree
from discord.ext import commands

from CababasBot import activities
from CababasBot.config_manager import Settings
from CababasBot.logger import BRIGHT_GREEN, BRIGHT_RED, L_LOG, get_traceback, ClientLogger


class Cababas(Client):
    def __init__(self, **options):
        self.log = ClientLogger(self)
        self.tree:CommandTree|None = None
        self.ready = False
        self.whitelisted_guilds:list[Guild] = []
        self.admin_guilds:list[Guild] = []
        intents = Intents.default()
        intents.message_content = True
        self.chatbot = commands.Bot(command_prefix='$',intents=intents)

        super().__init__(intents=intents, **options)

    async def setup_hook(self) -> None:
        await self.log.task('Creating command tree...')
        while self.tree is None:
            try:
                self.tree = CommandTree(client=self)
            except AttributeError:
                self.tree = None
        await self.log.task_completed('Created command tree.           ')

    async def on_ready(self):
        await self.change_presence(status=Status.invisible,activity=activities.Loading())
        await self.log.task(f'Setting up commands...')
        try:
            await self.setup_commands()
        except Exception as e:
            await self.log.error(f'Could not set up commands: {get_traceback(e)}')
        await self.change_presence(status=Status.idle, activity=activities.PlayingWithFood())
        self.ready = True

    async def setup_commands(self):
        self.whitelisted_guilds = await self.get_whitelisted_guilds()
        self.admin_guilds = await self.get_admin_guilds()
        
        self.whitelisted_guilds += self.admin_guilds

        async def check_flags(interaction:Interaction,check_manager:bool|None=False,silent:bool|None=False) -> bool:
            try:
                self.whitelisted_guilds = await self.get_whitelisted_guilds()

                guild = interaction.guild
                author = interaction.user

                if not isinstance(guild, Guild):
                    if not silent:
                        await interaction.response.send_message(content='Could not find guild. Please try again.',ephemeral=True)
                    return False
                elif (not isinstance(author, User)) and (not isinstance(author, Member)):
                    if not silent:
                        await interaction.response.send_message(content='Could not find author. Please try again.',ephemeral=True)
                    return False

                if check_manager:
                    self.admin_guilds = await self.get_admin_guilds()
                    self.whitelisted_guilds += self.admin_guilds

                    try:
                        managers:dict[str,int] = await Settings.get_key_data(Settings.SEC_DISCORD, Settings.KEY_MANAGERS, self.log)
                        if not isinstance(managers, dict):
                            raise TypeError('Managers are not in a valid dictionary.')
                    except Exception as e:
                        if not silent:
                            await interaction.response.send_message(content='Could not identify managers.',ephemeral=True)
                        await self.log.error(f'Could not get command managers: {get_traceback(e)}')
                        return False

                    if guild not in self.admin_guilds:
                        if not silent:
                            await interaction.response.send_message(content='No',ephemeral=True)
                        await self.log.log(f'Manager command was accessed illegally from guild {guild.name} ({guild.id})')
                        return False
                    if author.id not in managers.values():
                        if not silent:
                            await interaction.response.send_message(content='You can\'t run this.',ephemeral=True)
                        await self.log.log(f'Manager command {BRIGHT_RED}unauthorized{L_LOG} for {author.name} ({author.id})')
                        return False
                    else:
                        await self.log.log(f'Manager command {BRIGHT_GREEN}authorized{L_LOG} for {author.name} ({author.id})')
                else:
                    if not (await self.is_enabled()):
                        if not silent:
                            await interaction.response.send_message(content='Bot is currently disabled.',ephemeral=True)
                        return False
                    if guild not in self.whitelisted_guilds:
                        if not silent:
                            await interaction.response.send_message(content='No',ephemeral=True)
                        return False
            except InteractionResponded:
                pass
            except Exception as e:
                await self.log.error(f'Exception while checking command flags: {get_traceback(e)}')
                return False

            return True

        @self.tree.command(
            name='toggle-discord-enabled',
            description='Enable / Disable the bot\'s commands. (only accessible by managers)',
            guilds=self.admin_guilds,
            extras={
                'on':True,
                'off':False
            }
        )
        async def toggle_discord_enabled(interaction:Interaction,choice:bool|None):
            if not (await check_flags(interaction=interaction,check_manager=True)):
                return

            if choice is None:
                current_state = await Settings.get_key_data(Settings.SEC_DISCORD, Settings.KEY_ENABLED, self.log)
                if isinstance(current_state, bool):
                    choice = not current_state
                else:
                    choice = False
            success = await Settings.set_key_data(Settings.SEC_DISCORD, Settings.KEY_ENABLED, choice, self.log)
            try:
                if success:
                    await interaction.response.send_message(content=f'Set bot command status to `{choice}`',ephemeral=True)
                else:
                    await interaction.response.send_message(content=f'Unable to set bot command status to `{choice}`. Check logs for any errors.',ephemeral=True)
            except InteractionResponded:
                pass

        @self.tree.command(
            name='shutdown',
            description='Attempt to shut down the bot process. (only accessible by managers)',
            guilds=self.admin_guilds
        )
        async def shutdown(interaction:Interaction):
            if not (await check_flags(interaction=interaction,check_manager=True)):
                return
            try:
                await interaction.response.send_message(content=f'Shutdown sent. Bye bye! 👋👋👋', ephemeral=True)
            except InteractionResponded:
                pass
            except Exception as e:
                await self.log.log(f'Ignoring the following error for the shutdown command: {get_traceback(e)}')
            await self.log.task_completed(f'Shutting down process.')
            exit()
        for guild in self.whitelisted_guilds:
            try:
                await self.tree.sync(guild=guild)
            except Exception as e:
                await self.log.error(f'Failed to sync command tree to guild {type(guild)}{guild.id}: {get_traceback(e)}')
                return
            

        await self.log.task_completed(f'Commands successfully set up.')

    async def is_enabled(self):
        return await Settings.get_key_data(Settings.SEC_DISCORD, Settings.KEY_ENABLED, self.log)
    
    async def get_whitelisted_guilds(self) -> list[Guild]:
        try:
            return await self.fetch_whitelisted_guilds((await Settings.get_key_data(Settings.SEC_DISCORD, Settings.KEY_COMMANDS_WHITELIST, self.log)))
        except Exception as e:
            await self.log.error(f'Could not get whitelisted guilds: {get_traceback(e)}')
            return []
        
    async def get_admin_guilds(self) -> list[Guild]:
        try:
            return await self.fetch_whitelisted_guilds((await Settings.get_key_data(Settings.SEC_DISCORD, Settings.KEY_COMMANDS_ADMIN, self.log)))
        except Exception as e:
            await self.log.error(f'Could not get admin whitelisted guilds: {get_traceback(e)}')
            return []

    async def fetch_whitelisted_guilds(self, whitelist:dict[str,int]) -> list[Guild]:
        result = []
        for key in whitelist:
            guild_id = whitelist[key]
            try:
                result.append((await self.fetch_guild(guild_id)))
            except NotFound:
                pass
            except HTTPException as e:
                await self.log.error(f'Failed to fetch whitelisted guild {key}-{guild_id} due to HTTP error: {get_traceback(e)}')
            except Exception as e:
                await self.log.error(f'Failed to fetch whitelisted guild {key}-{guild_id} due to unknown error: {get_traceback(e)}')
        return result