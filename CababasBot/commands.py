import discord
from discord import Client, Interaction
from discord.app_commands import CommandTree


class SlashCommands(CommandTree):
    def __init__(self, client: Client):
        super().__init__(client)