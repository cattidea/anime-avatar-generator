import os

import cv2
import matplotlib.pyplot as plt
import numpy as np


class DataLoader():

    def __init__(self, data_dir, img_shape=(64, 64, 3), cache_size=128):
        self.data_dir = data_dir
        self.img_names = np.array(os.listdir(self.data_dir))
        self.data_length = len(self.img_names)
        self.img_shape = img_shape

        self.cache_size = cache_size
        self.cache = np.zeros(
            (self.cache_size, *self.img_shape), dtype=np.uint8)
        self.flag = np.zeros((self.cache_size, ), dtype=np.bool)

        self.scale_func = lambda x: x
        self.aug_func = lambda x: x
        self.batch_size = 64

    def get_item(self, idx):
        img_name = self.img_names[idx]
        img_path = os.path.join(self.data_dir, img_name)
        img = read_img(img_path, (self.img_shape[1], self.img_shape[0]))
        return img

    def __getitem__(self, idx):
        if idx < self.cache_size:
            if self.flag[idx]:
                return self.cache[idx]
            else:
                img = self.get_item(idx)
                self.cache[idx] = img
                self.flag[idx] = True
                return img
        else:
            return self.get_item(idx)

    def scale(self, scale_func):
        self.scale_func = scale_func
        return self

    def batch(self, batch_size):
        self.batch_size = batch_size
        return self

    def __iter__(self):
        permutation = np.random.permutation(self.data_length)
        for i in range(0, self.data_length, self.batch_size):
            batch_permutation = permutation[i: i+self.batch_size]
            data_batch = np.zeros(
                (batch_permutation.shape[0], *self.img_shape), dtype=np.float32)
            if all(batch_permutation < self.cache_size) and all(self.flag[batch_permutation]):
                data_batch[:] = self.cache[batch_permutation]
            else:
                for i, idx in enumerate(batch_permutation):
                    data_batch[i] = self[idx]
            data_batch = self.scale_func(data_batch)
            yield data_batch


class DataLoaderWithoutCache():

    def __init__(self, data_dir, img_shape=(64, 64, 3), cache_size=None):
        self.data_dir = data_dir
        self.img_names = np.array(os.listdir(self.data_dir))
        self.data_length = len(self.img_names)
        self.img_shape = img_shape

        self.scale_func = lambda x: x
        self.aug_func = lambda x: x
        self.batch_size = 64

        self.data = self.init_data()

    def init_data(self):
        data = np.zeros((self.data_length, *self.img_shape), dtype=np.uint8)
        for i in range(self.data_length):
            data[i] = self.get_item(i)
        return data

    def get_item(self, idx):
        img_name = self.img_names[idx]
        img_path = os.path.join(self.data_dir, img_name)
        img = read_img(img_path, (self.img_shape[1], self.img_shape[0]))
        return img

    def scale(self, scale_func):
        self.scale_func = scale_func
        return self

    def batch(self, batch_size):
        self.batch_size = batch_size
        return self

    def augment(self, aug_func):
        self.aug_func = aug_func
        return self

    def __iter__(self):
        permutation = np.random.permutation(self.data_length)
        for i in range(0, self.data_length, self.batch_size):
            batch_permutation = permutation[i: i+self.batch_size]
            data_batch = self.data[batch_permutation]
            data_batch = self.aug_func(data_batch)
            data_batch = data_batch.astype(np.float32)
            data_batch = self.scale_func(data_batch)
            yield data_batch


def show_batch(imgs, cols=None):
    fig = plt.figure(figsize=(10, 10))
    num_imgs, h, w, c = imgs.shape
    if cols is None:
        cols = int(np.ceil(np.sqrt(num_imgs)))
    rows = int(np.ceil(num_imgs / cols))

    img_concat = np.zeros((rows*h, cols*w, c), dtype=np.uint8)
    for i in range(num_imgs):
        row_idx, col_idx = i//cols, i % cols
        img_concat[row_idx*h: (row_idx+1)*h,
                   col_idx*w: (col_idx+1)*w] = imgs[i]
    plt.imshow(img_concat)
    plt.axis('off')
    plt.show()


def read_img(img_path, size):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, size)
    return img
