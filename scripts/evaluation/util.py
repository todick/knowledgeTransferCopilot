from colorama import Fore, Style

VERBOSE = False


def log(message):
    if VERBOSE:
        print(message)


def info(message):
    print(message)


def success(message):
    print(f"{Fore.GREEN}{message}{Fore.RESET}")


def warn(message):
    print(f"{Fore.YELLOW}{message}{Fore.RESET}")


def error(message):
    print(f"{Fore.RED}{message}{Fore.RESET}")
