import argparse

from config_parser.parser import config_to_tree

class ArgumentParser(object):

    def __init__(self, name):
        self.core = argparse.ArgumentParser(description=name)
        self.core.add_argument('action', choices=['train', 'test'], help='test or train')

    def bind(self, config):
        linear_config = config.linear()
        for key, value in linear_config.items():
            kwargs = {'action': None, 'default': None}
            if isinstance(value, bool):
                kwargs['action'] = 'store_' + str(value).lower()
            else:
                kwargs['default'] = value
            self.core.add_argument('--'+key, **kwargs)
        args = self.core.parse_args()
        for key in linear_config:
            linear_config[key] = args.__dict__[key.replace('-', '_')]
        config.update(config_to_tree(linear_config))
