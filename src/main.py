from start import start
from prompt import prompt
from config_file import get_config, args
from utils.root import is_root
from sys import exit

if not is_root():
    print("This program needs to be run as root.")
    exit(1)

config = get_config()

if not config:
    config = prompt()

if args.verbose:
    config.verbose = True
if args.log_file:
    config.log_file = args.log_file

start(config)