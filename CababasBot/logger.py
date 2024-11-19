from discord import Client

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

class Logger:
    def __init__(self, bot:Client):
        self.bot = bot

    def log(self, message: str) -> None:
        print(f'{RESET}{self.bot.user.name}{WHITE}> {message}{RESET}')

    def success(self, message: str) -> None:
        print(f'{RESET}{self.bot.user.name}{L_SUCCESS}> {message}{RESET}')

    def error(self, error_message: str) -> None:
        print(f'{RESET}{self.bot.user.name}{L_ERROR}> {error_message}{RESET}')

    def task(self, task_message: str) -> None:
        print(f'{RESET}{self.bot.user.name}{L_TASK}> {task_message}{RESET}', end='\r', flush=True)

    def task_completed(self, task_message: str) -> None:
        print(f'{RESET}{self.bot.user.name}{L_TASK_COMPLETED}> {task_message}{RESET}')