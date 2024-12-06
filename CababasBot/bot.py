from discord import Client, Embed, Intents, InteractionResponded, Member, Status, Guild, NotFound, HTTPException, Interaction, \
    User, Message, TextChannel, Forbidden
from discord.app_commands import CommandTree, choices, Choice
from discord.ext import commands

from CababasBot import activities, snowday
from CababasBot.chatbot import chat_completion, history
from CababasBot.chatbot.calculator import input_to_tokens, calculate_cost, TYPE_INPUT, TYPE_OUTPUT
from CababasBot.config_manager import Settings
from CababasBot.logger import BRIGHT_GREEN, BRIGHT_RED, L_LOG, get_traceback, ClientLogger, RED, RESET


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

    async def on_message(self, message:Message):
        config = await Settings.get_data(self.log)

        content = message.content
        sender = message.author

        if sender.id == self.user.id:
            return

        if not isinstance(content, str):
            return

        chatbot_prefix = await Settings.get_key_data(Settings.SEC_DISCORD, Settings.KEY_AI_PREFIX, self.log, config)
        if not isinstance(chatbot_prefix, str):
            chatbot_prefix = 'cab'
        else:
            chatbot_prefix = chatbot_prefix.lower()

        if (self.ready == True) and (content.lower().startswith(f'{chatbot_prefix} ')) and (await Settings.get_key_data(Settings.SEC_AI,Settings.KEY_ENABLED,self.log,config) == True) and (await Settings.get_key_data(Settings.SEC_DISCORD,Settings.KEY_ENABLED,self.log,config) == True):
            history_id = message.guild.id
            content = content[len(chatbot_prefix) + 1:]
            await self.log.log(f'Received request for completion from {sender.name} ({sender.id}) in {message.channel.id}')
            try:
                async with message.channel.typing():
                    print_msg = f'Creating completion for {sender.name} ({sender.id}):'
                    passing_history = await history.prompt_to_history(history_id, content, history.ROLE_USER,
                                                                str(sender.id), self.log, config)
                    processed_history = history.read_history(passing_history)
                    print_msg += f'\nHistory length: {len(passing_history)}'
                    print_msg += f'\nPrompt: > "{content}"'

                    prompt_tokens = input_to_tokens(content)
                    if prompt_tokens > await Settings.get_key_data(Settings.SEC_AI, Settings.KEY_MAX_PROMPT_TOK, self.log, config):
                        print_msg += f'\n{RED}Prompt contains too many tokens ({prompt_tokens}).{L_LOG}'
                        response = f'too long!'
                    else:
                        completion = await chat_completion.generate_completion(
                            history=processed_history,
                            config=config,
                            logger=self.log
                        )

                        response = completion.choices[0].message.content
                        finish_reason = completion.choices[0].finish_reason
                        print_msg += f'\nResponse: < "{response}"'
                        print_msg += f'\nFinish reason: {finish_reason}'

                        if finish_reason == 'length':
                            response = f'{response} ... *yawn*'

                        input_tokens = completion.usage.prompt_tokens
                        output_tokens = completion.usage.completion_tokens
                        input_cost = await calculate_cost(TYPE_INPUT, input_tokens, self.log, config)
                        output_cost = await calculate_cost(TYPE_OUTPUT, output_tokens, self.log, config)

                        print_msg += f'\nInput tokens: {input_tokens} {RED}${input_cost}{L_LOG}'
                        print_msg += f'\nOutput tokens: {output_tokens} {RED}${output_cost}{L_LOG}'
                        print_msg += f'\nTotal tokens: {input_tokens + output_tokens} {RED}${input_cost+output_cost}{L_LOG}'

                        await history.append_passed_history(history_id, passing_history, response, self.log)

                        # Attempt logging completion to channel
                        try:
                            comp_channel = int(
                                await Settings.get_key_data(Settings.SEC_DISCORD, Settings.KEY_COMPLETION_CHANNEL))
                        except TypeError:
                            await self.log.error(f'Completion channel ID is not numeric, could not be converted to int.')
                            return

                        try:
                            channel = self.get_channel(comp_channel)
                            if not isinstance(channel, TextChannel):
                                await self.log.error(
                                    f'Incorrect error channel type {type(channel)}. {TextChannel} required.')
                                return
                            embed = Embed()
                            embed.title = f'Completion {str(completion.id)[:5]}'
                            embed.description = f'<@{sender.id}> in channel <#{message.channel.id}>.'
                            embed.add_field(
                                name=f'Prompt',
                                value=f'`{content}`',
                                inline=False
                            )
                            embed.add_field(
                                name=f'Response',
                                value=f'`{response}`',
                                inline=False
                            )
                            embed.add_field(
                                name=f'Input',
                                value=f'`{input_tokens}` (||${round(input_cost, 4)}||)',
                                inline=True
                            )
                            embed.add_field(
                                name=f'Output',
                                value=f'`{output_tokens}` (||${round(output_cost, 4)}||)',
                                inline=True
                            )
                            embed.add_field(
                                name=f'Total',
                                value=f'`{input_tokens + output_tokens}` (||${round(input_cost + output_cost, 4)}||)',
                                inline=True
                            )
                            await channel.send(embed=embed)
                        except Forbidden:
                            await self.log.error(
                                f'Please check that bot has permissions to send messages in the completion channel {comp_channel}.')
                        except HTTPException as e:
                            await self.log.error(f'Failed to send completion log to channel: {get_traceback(e)}')

                    await message.reply(content=response, mention_author=False)

                await self.log.log(print_msg)
            except Exception as e:
                await self.log.error(f'Could not generate completion for {sender.name} ({sender.id}) "{content}": {get_traceback(e)}')
    async def setup_commands(self):
        self.whitelisted_guilds = await self.get_whitelisted_guilds()
        self.admin_guilds = await self.get_admin_guilds()
        
        self.whitelisted_guilds += self.admin_guilds

        async def check_flags(interaction:Interaction,check_manager:bool|None=False,silent:bool|None=False,ignore_ready:bool|None=False) -> bool:
            try:
                if not self.ready and not ignore_ready:
                    return False

                current_guild = interaction.guild
                author = interaction.user

                if not isinstance(current_guild, Guild):
                    if not silent:
                        await interaction.response.send_message(content='Could not find guild. Please try again.',ephemeral=True)
                    return False
                elif (not isinstance(author, User)) and (not isinstance(author, Member)):
                    if not silent:
                        await interaction.response.send_message(content='Could not find author. Please try again.',ephemeral=True)
                    return False

                if check_manager:
                    try:
                        managers:dict[str,int] = await Settings.get_key_data(Settings.SEC_DISCORD, Settings.KEY_MANAGERS, self.log)
                        if not isinstance(managers, dict):
                            raise TypeError('Managers are not in a valid dictionary.')
                    except Exception as e:
                        if not silent:
                            await interaction.response.send_message(content='Could not identify managers.',ephemeral=True)
                        await self.log.error(f'Could not get command managers: {get_traceback(e)}')
                        return False

                    if current_guild not in self.admin_guilds:
                        if not silent:
                            await interaction.response.send_message(content='No',ephemeral=True)
                        await self.log.log(f'Manager command was accessed illegally from guild {current_guild.name} ({current_guild.id})')
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
                    if current_guild not in self.whitelisted_guilds:
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
            name='toggle-section',
            description='Enable / Disable a section. (only accessible by managers)',
            guilds=self.admin_guilds
        )
        @choices(
            section=[
                Choice(name="Discord (section)", value=Settings.SEC_DISCORD),
                Choice(name="AI (section)", value=Settings.SEC_AI)
            ]
        )
        async def toggle_discord_enabled(interaction:Interaction,section:str|None,value:bool|None):
            if not (await check_flags(interaction=interaction,check_manager=True)):
                return

            if section is None:
                section = Settings.SEC_DISCORD

            if value is None:
                current_state = await Settings.get_key_data(section, Settings.KEY_ENABLED, self.log)
                if isinstance(current_state, bool):
                    value = not current_state
                else:
                    value = False
            success = await Settings.set_key_data(section, Settings.KEY_ENABLED, value, self.log)
            try:
                if success:
                    await interaction.response.send_message(content=f'Set {section} status to `{value}`',ephemeral=True)
                    await self.log.log(f'Set {section} status to `{value}`')
                else:
                    await interaction.response.send_message(content=f'Unable to set {section} status to `{value}`. Check logs for any errors.',ephemeral=True)
            except InteractionResponded:
                pass

        @self.tree.command(
            name='shutdown',
            description='Attempt to shut down the bot process. (only accessible by managers)',
            guilds=self.admin_guilds
        )
        async def shutdown(interaction:Interaction):
            if not (await check_flags(interaction=interaction,check_manager=True,ignore_ready=True)):
                return
            try:
                await interaction.response.send_message(content=f'Shutdown sent. Bye bye! 👋👋👋', ephemeral=True)
            except InteractionResponded:
                pass
            except Exception as e:
                await self.log.log(f'Ignoring the following error for the shutdown command: {get_traceback(e)}')
            await self.log.task_completed(f'Shutting down process.')
            exit()

        @self.tree.command(
            name='refresh-guilds',
            description='Refresh the stored whitelisted guilds.',
            guilds = self.admin_guilds
        )
        async def refresh_guilds(interaction:Interaction):
            if not (await check_flags(interaction=interaction,check_manager=True,ignore_ready=True)):
                return
            try:
                self.whitelisted_guilds = await self.get_whitelisted_guilds()
                self.admin_guilds = await self.get_admin_guilds()
                self.whitelisted_guilds += self.admin_guilds
                await interaction.response.send_message(content=f'Whitelisted: `{self.whitelisted_guilds}`', ephemeral=True)
            except InteractionResponded:
                pass
            except Exception as e:
                await self.log.error(f'Could not refresh guilds: {get_traceback(e)}')

        @self.tree.command(
            name='snowday',
            description='Is tomorrow going to be a snowday?',
            guilds=self.whitelisted_guilds
        )
        async def snowday_tmr(interaction:Interaction):
            if not (await check_flags(interaction=interaction,check_manager=False,ignore_ready=False)):
                return
            try:
                prediction = snowday.predict(
                    str(await Settings.get_key_data(Settings.SEC_SNOWDAY, Settings.KEY_POSTAL, self.log)),
                )
                chance = await prediction.chance_tmrw()
                if chance is None:
                    await interaction.response.send_message(content=f'idk :(')
                    return
                await interaction.response.send_message(content=f'Snowday tmr is {int(chance)}% ️ ❄️')
            except InteractionResponded:
                pass
            except Exception as e:
                await self.log.error(f'Could not predict snowday: {get_traceback(e)}')
                await interaction.response.send_message(content=f'Try again, something went wrong :(', ephemeral=True)

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
                await self.log.error(f'[WARNING]: Could not fetch whitelisted guild {key}: {guild_id}, check that the bot is in this guild!',silent=True)
            except HTTPException as e:
                await self.log.error(f'Failed to fetch whitelisted guild {key}-{guild_id} due to HTTP error: {get_traceback(e)}')
            except Exception as e:
                await self.log.error(f'Failed to fetch whitelisted guild {key}-{guild_id} due to unknown error: {get_traceback(e)}')
        return result