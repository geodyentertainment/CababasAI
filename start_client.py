from CababasBot import secrets
from CababasBot.bot import Cababas

print('Startup')

client = Cababas()
client.run(secrets.DISCORD_TOK_TEST)
