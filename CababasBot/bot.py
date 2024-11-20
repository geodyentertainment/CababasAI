from discord import Client, Intents, Status, Guild, NotFound, HTTPException
from discord.app_commands import CommandTree
from discord.ext import commands
from discord.ext.commands import Context

from CababasBot import activities
from CababasBot.config_manager import Settings
from CababasBot.logger import get_traceback, ClientLogger


class Cababas(Client):
    def __init__(self, **options):
        self.log = ClientLogger(self)
        self.tree:CommandTree|None = None
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
        await self.log.task(f'Syncing commands...')
        try:
            await self.setup_commands()
            await self.log.task_completed(f'Commands synced.')
        except Exception as e:
            await self.log.error(f'Could not sync commands: {get_traceback(e)}')
        await self.change_presence(status=Status.idle, activity=activities.PlayingWithFood())

    async def setup_commands(self):
        try:
            whitelisted_guilds = await self.fetch_whitelisted_guilds((await Settings.get_key_data(Settings.SEC_DISCORD, Settings.KEY_COMMANDS_WHITELIST)))
        except TypeError:
            await self.log.error(f'Could not get command whitelisted guilds, TypeError while getting dict.')
            return

        @self.tree.command(
            name='test',
            description='This is a test',
            guilds=whitelisted_guilds
        )
        async def test_cmd(ctx: Context):
            await self.log.log("Hi")

        for guild in whitelisted_guilds:
            try:
                await self.tree.sync(guild=guild)
            except Exception as e:
                await self.log.error(f'Failed to sync command tree to guild {type(guild)}{guild.id}: {get_traceback(e)}')


    async def fetch_whitelisted_guilds(self, whitelist:dict[str,int]) -> list[Guild]:
        result = []
        for guild_id in whitelist.values():
            try:
                result.append((await self.fetch_guild(guild_id)))
                raise Exception('Test exception')
            except NotFound:
                pass
            except HTTPException as e:
                await self.log.error(f'Failed to fetch whitelisted guild {guild_id} due to HTTP error: {get_traceback(e)}')
            except Exception as e:
                await self.log.error(f'Failed to fetch whitelisted guild {guild_id} due to unknown error: {get_traceback(e)}')
        return result