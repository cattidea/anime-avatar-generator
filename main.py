import os
import sys
import requests

if __name__ == '__main__':
    action = sys.argv[1]

    if action == 'train':
        pass
    elif action == 'test':
        pass
    elif action == 'docs':
        from docs import docs_dev
        docs_dev()
