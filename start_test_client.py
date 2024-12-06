from CababasBot import env_secrets
from CababasBot.bot import Cababas

client = Cababas()
client.run(env_secrets.DISCORD_TOK_TEST)
