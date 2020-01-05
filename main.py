import os
import requests

from config_parser.config import CONFIG
from config_parser.argparse import ArgumentParser

def initialize():
    if not os.path.exists(CONFIG.data.cascade_file):
        lbpcascade_animeface_url = 'https://raw.githubusercontent.com/nagadomi/lbpcascade_animeface/master/lbpcascade_animeface.xml'
        with open(CONFIG.data.cascade_file, 'w') as f:
            f.write(requests.get(lbpcascade_animeface_url).text)

if __name__ == '__main__':
    parser = ArgumentParser(CONFIG.name, actions=['train', 'test', 'docs', 'crawl'])
    parser.bind(CONFIG)
    initialize()

    if CONFIG.action == 'train':
        pass
    elif CONFIG.action == 'test':
        from data_loader import image_handler
        pass
    elif CONFIG.action == 'docs':
        from docs import docs_dev
        docs_dev()
    elif CONFIG.action == 'crawl':
        from utils.process import new_process
        new_process(["python3", "image_crawler/crawler.py"])
