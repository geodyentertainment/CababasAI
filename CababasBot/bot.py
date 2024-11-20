import secrets
from discord import Client, Intents, Status
from CababasBot import logger, activities, config_manager
from CababasBot.config_manager import Settings


class Cababas(Client):
    def __init__(self, **options):
        self.log = logger.ClientLogger(self)

        token = secrets.DISCORD_TOK_TEST
        intents = Intents.default()
        intents.message_content = True

        super().__init__(intents=intents, **options)

        self.run(token)

    async def on_ready(self):
        self.log.task_completed(f'Logged in.')
        await self.change_presence(status=Status.invisible,activity=activities.Loading())

        self.log.task(f'Configurating...')

        print(Settings.get_key_data(Settings.SEC_DISCORD, Settings.KEY_ENABLED, self.log))

client = Cababas()