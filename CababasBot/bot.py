import secrets
from discord import Client, Intents, Status
from CababasBot import logger, activities


class Cababas(Client):
    def __init__(self, **options):
        self.log = logger.Logger(self)

        token = secrets.DISCORD_TOK_TEST
        intents = Intents.default()
        intents.message_content = True

        super().__init__(intents=intents, **options)

        self.run(token)

    async def on_ready(self):
        self.log.task_completed(f'Logged in as {self.user.name}')
        await self.change_presence(status=Status.invisible,activity=activities.Loading())

        self.log.task(f'Configurating...')


client = Cababas()