from discord import Client, Intents, Status
from discord.app_commands import CommandTree

from CababasBot import logger, activities


class Cababas(Client):
    def __init__(self, **options):
        self.log = logger.ClientLogger(self)
        self.tree = CommandTree(self)

        intents = Intents.default()
        intents.message_content = True

        super().__init__(intents=intents, **options)

    async def on_ready(self):
        self.log.task_completed(f'Logged in.')
        await self.change_presence(status=Status.invisible,activity=activities.Loading())

        self.log.task(f'Loading commands...')


