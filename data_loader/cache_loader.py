import os
import json
import h5py
import pickle
import hashlib

from config_parser.config import CONFIG

key_maps = {
    'general': lambda *args, **kwargs: __general_key_map(*args, **kwargs)
}


class CacheNotFoundError(Exception):

    def __init__(self, name):
        self.message = "Can not found cache {}".format(name)


class Cacher():
    """ Python 通用数据缓存器 """

    def __init__(self, path, ext=".pkl", name=None):
        self.path = path
        self.ext = ext
        self.name = name

    def read(self):
        if os.path.exists(self.path):
            data = self._load()
            if self.name:
                print("Cache >> {}".format(self.name))
        else:
            raise CacheNotFoundError(self.path)
        return data

    def save(self, data):
        self._dump(data)
        if self.name:
            print("Cache << {}".format(self.name))

    def _load(self):
        with open(self.path, 'rb') as f:
            data = pickle.load(f)
        return data

    def _dump(self, data):
        with open(self.path, 'wb') as f:
            pickle.dump(data, f)


class H5Cacher(Cacher):
    """ H5 数据缓存器 """

    def __init__(self, path, name=None):
        super().__init__(self, path, ".h5", name)

    def _load(self):
        data = {}
        try:
            h5f = h5py.File(self.path, 'r')
            for key in h5f.keys():
                data[key] = h5f[key][:]
        finally:
            h5f.close()
        return data

    def _dump(self, data):
        try:
            h5f = h5py.File(self.path, 'w')
            for key in data.keys():
                h5f[key] = data[key]
        finally:
            h5f.close()


class JSONCacher(Cacher):
    """ JSON 数据缓存器 """

    def __init__(self, path, name=None):
        super().__init__(self, path, ".json", name)

    def _load(self):
        with open(self.path, 'r', encoding="utf8") as f:
            data = json.load(f)
        return data

    def _dump(self, data):
        with open(self.path, 'w', encoding="utf8") as f:
            json.dump(data, f, indent=2)


class CacheLoader():
    """ 数据装饰器
    获取数据前先检查是否有本地 Cache ，若无则重新获取并保存
    暂时只支持全数据缓存，不支持子数据缓存

    约定：
    - 函数名使用 'get_' 前缀

    TODO:
    - [ ] 控制 Cache 上限大小
    """

    def __init__(self, key_map='general', enable=CONFIG.cache.enable, ext=".pkl"):
        self.key_map = key_maps.get(key_map, key_map)
        self.enable = enable
        self.ext = ext
        self.name = None

    def get_file_path(self, *args, **kw):

        file_name = self.name
        hash = self.key_map(*args, **kw)
        file_path = os.path.join(CONFIG.cache.root, file_name)
        file_path += f'-{hash}{self.ext}'
        return file_path

    def __call__(self, func):
        func_name = func.__name__
        if func_name.startswith('get_'):
            self.name = func_name.lstrip('get_')
        else:
            print('[warn] function {func_name} is not start with "get"')
            self.name = func_name
        def load_data(*args, **kw):
            file_path = self.get_file_path(*args, **kw)
            cacher = Cacher(file_path, ext=self.ext, name=self.name)

            if self.enable and os.path.exists(file_path):
                data = cacher.read()
            else:
                data = func(*args, **kw)
                cacher.save(data)
            return data
        return load_data


class Md5():

    def __init__(self):
        self.__core = hashlib.md5()

    def update(self, b):
        self.__core.update(b)

    def result(self):
        return self.__core.hexdigest()

    def update_file(self, path, chunk_size = 8192):
        """ 添加文件 """
        with open(path, 'rb') as f:
            while True:
                b = f.read(chunk_size)
                if not b :
                    break
                self.update(b)

    def update_dir(self, path):
        """ 添加整个文件夹 """
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                print(filename)
                file_path = os.path.join(dirpath, filename)
                self.update_file(file_path)

    def update_byteable(self, data):
        """ 添加可 bytes 的数据 """
        self.update(bytes(data))

    def update_string(self, string):
        """ 添加一个字符串 """
        self.update(string.encode())


def __general_key_map(*args, **kwargs):
    """ 通用缓存哈希计算函数

    约定：
    - 绑定的文件夹应使用 kwargs 形式传入，且后缀 '_dir'
    - 绑定的文件应使用 kwargs 形式传入，且后缀 '_file'
    """
    md5 = Md5()
    for arg in args:
        if isinstance(arg, str):
            md5.update_string(arg)
        else:
            md5.update_byteable(arg)
    for key, value in kwargs.items():
        if key.endswith('_dir'):
            md5.update_dir(value)
        elif key.endswith('_file'):
            md5.update_file(value)
        elif isinstance(value, str):
            md5.update_string(value)
        else:
            md5.update_byteable(value)

    return md5.result()
