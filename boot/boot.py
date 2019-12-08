from config_parser.config import CONFIG
from boot.argparse import ArgumentParser

parser = ArgumentParser(CONFIG.name)
parser.bind(CONFIG)
print(CONFIG)
