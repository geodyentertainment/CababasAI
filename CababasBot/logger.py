import traceback

from discord import Client, TextChannel, HTTPException, Forbidden

from CababasBot.env_secrets import ERROR_CHANNEL_ID

BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
LIGHT_GRAY = '\033[37m'
DARK_GRAY = '\033[90m'
BRIGHT_RED = '\033[91m'
BRIGHT_GREEN = '\033[92m'
BRIGHT_YELLOW = '\033[93m'
BRIGHT_BLUE = '\033[94m'
BRIGHT_MAGENTA = '\033[95m'
BRIGHT_CYAN = '\033[96m'
WHITE = '\033[97m'
RESET = '\033[0m'

L_SUCCESS = GREEN
L_ERROR = RED
L_LOG = LIGHT_GRAY
L_TASK = YELLOW
L_TASK_COMPLETED = WHITE
L_CHARGE = BRIGHT_RED

def get_traceback(err: Exception) -> str:
    return ''.join(traceback.format_exception(type(err), err, err.__traceback__))


class PrefixedLogger:
    def __init__(self, prefix: str | None = ''):
        self.prefix = prefix

    def get_prefix(self) -> str:
        return self.prefix

    async def log(self, message: str) -> None:
        log(message, self.get_prefix())

    async def success(self, message: str) -> None:
        success(message, self.get_prefix())

    async def error(self, error_message: str, *argv) -> None:
        error(error_message, self.get_prefix())

    async def task(self, task_message: str) -> None:
        task(task_message, self.get_prefix())

    async def task_completed(self, task_message: str) -> None:
        task_completed(task_message, self.get_prefix())

class ClientLogger(PrefixedLogger):
    def __init__(self, client: Client | None):
        self.client = client
        super().__init__()

    def get_prefix(self) -> str:
        try:
            return f'[CLIENT] {self.client.user.name}'
        except AttributeError:
            return '[CLIENT] (client username not loaded yet)'

    async def error(self, error_message: str, silent:bool|None=False) -> None:
        await super().error(error_message)
        if not silent:
            try:
                channel_id = int(ERROR_CHANNEL_ID)
            except TypeError:
                await super().error(f'Error channel ID {ERROR_CHANNEL_ID} is not numeric, could not be converted to int.')
                return

            try:
                channel = self.client.get_channel(channel_id)
                if not isinstance(channel, TextChannel):
                    await super().error(f'Incorrect error channel type {type(channel)}. {TextChannel} required.')
                    return

                await channel.send(content=f'```\n{error_message}\n```')
            except Forbidden:
                error(f'Please check that "{self.get_prefix()}" has permissions to send messages in the error channel {channel_id}.')
            except HTTPException as e:
                error(f'Failed to send error to error channel: {get_traceback(e)}')



def log(message: str, prefix: str | None = '') -> None:
    print(f'{RESET}{prefix}{L_LOG} > {message}{RESET}')

def success(message: str, prefix: str | None = '') -> None:
    print(f'{RESET}{prefix}{L_SUCCESS} > {message}{RESET}')

def error(error_message: str, prefix: str | None = '') -> None:
    print(f'{RESET}{prefix}{L_ERROR} > {error_message}{RESET}')

def task(task_message: str, prefix: str | None = '') -> None:
    print(f'{RESET}{prefix}{L_TASK} > {task_message}{RESET}', end='\r', flush=True)

def task_completed(task_message: str, prefix: str | None = '') -> None:
    print(f'{RESET}{prefix}{L_TASK_COMPLETED} > {task_message}{RESET}')