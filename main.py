from config_parser.config import CONFIG
from config_parser.argparse import ArgumentParser

parser = ArgumentParser(CONFIG.name, actions=['train', 'test', 'docs', 'crawl'])
parser.bind(CONFIG)

if CONFIG.action == 'train':
    pass
elif CONFIG.action == 'test':
    pass
elif CONFIG.action == 'docs':
    from docs import docs_dev
    docs_dev()
elif CONFIG.action == 'crawl':
    from utils.process import new_process
    new_process(["python3", "image_crawler/crawler.py"])
