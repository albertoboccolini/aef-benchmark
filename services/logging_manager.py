import logging

BLUE = "\033[94m"
RED = "\033[91m"
RESET = "\033[0m"


def log_info(message):
    logging.info(f"{BLUE}{message}{RESET}")


def log_error(message):
    logging.error(f"{RED}{message}{RESET}")
