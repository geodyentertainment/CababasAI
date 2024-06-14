## String colors (printing)
class Colors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m' # orange on some systems
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
    RESET = '\033[0m' # reference to return to standard terminal text color

    L_SUCCESS = GREEN
    L_ERROR = RED
    L_LOG = LIGHT_GRAY
    L_TASK = YELLOW
    L_TASK_COMPLETED = WHITE
    L_CHARGE = BRIGHT_RED

def line() -> None:
    print('\n')

def log(message:str) -> None:
    print(f'{Colors.WHITE}> {message}{Colors.RESET}')

def success(message:str) -> None:
    print(f'{Colors.L_SUCCESS}> {message}{Colors.RESET}')

def error(error:str) -> None:
    print(f'{Colors.L_ERROR}> {error}{Colors.RESET}')

def task(task:str) -> None:
    print(f'{Colors.L_TASK}> {task}{Colors.RESET}',end='\r',flush=True)

def task_completed(task:str) -> None:
    print(f'{Colors.L_TASK_COMPLETED}> {task}{Colors.RESET}')