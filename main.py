from os_manager import environment as env
import cababas

client = cababas.CababasBot()
client.run(env.DISCORD_TOK)