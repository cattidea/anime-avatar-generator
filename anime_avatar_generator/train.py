import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
import imgaug as ia
import imgaug.augmenters as iaa
import tensorflow as tf
import os

from anime_avatar_generator.data_processor.data_loader import DataLoader, show_batch, DataLoaderWithoutCache
from anime_avatar_generator.models.dcgan import DCGAN, gen_random

batch_size = 256
cache_size = 1024 * 64
nz = 100
glr = 2e-4
dlr = 2e-4
img_dir = 'data/faces/'
IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS = 64, 64, 3
BASE_DIR = ""
num_examples_to_generate = 36
seed = gen_random((num_examples_to_generate, nz))


def normalize(img: np.ndarray):
    return (img - 127.5) / 127.5

def denormalize(img: np.ndarray):
    return  img * 127.5 + 127.5


sometimes = lambda aug: iaa.Sometimes(0.5, aug)

aug = iaa.Sequential(
    [
        iaa.Fliplr(0.5), # horizontally flip 50% of all images
        sometimes(iaa.CropAndPad(
            percent=(-0.05, 0.1),
            pad_mode=ia.ALL,
            pad_cval=(0, 255)
        )),
        sometimes(iaa.Affine(
            scale={"x": (0.9, 1.1), "y": (0.9, 1.1)}, # scale images to 80-120% of their size, individually per axis
            translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)}, # translate by -20 to +20 percent (per axis)
            rotate=(-10, 10), # rotate by -45 to +45 degrees
            order=[0, 1], # use nearest neighbour or bilinear interpolation (fast)
            cval=(0, 255), # if mode is constant, use a cval between 0 and 255
            mode=ia.ALL # use any of scikit-image's warping modes (see 2nd image from the top for examples)
        )),
    ],
    random_order=True
)






def show_generator(generator, seed):
    predictions = generator(seed, training=False).numpy()
    images = denormalize(predictions).astype(np.uint8)
    show_batch(images)





def run():
    data_loader = DataLoaderWithoutCache(data_dir=os.path.join(BASE_DIR, img_dir), img_shape=(IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS), cache_size=cache_size)
    data_loader.scale(normalize).batch(batch_size).augment(lambda x: aug(images=x))
    img_batch = denormalize(next(iter(data_loader)))
    show_batch(img_batch)

    dcgan = DCGAN(image_shape=(IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS), dlr=dlr, glr=glr, nz=nz)
    dcgan.summary()

    show_generator(dcgan.generator, seed)

    for epoch in range(500):
        for batch_idx, img_batch in enumerate(data_loader):
            dcgan.train_step(img_batch, num_iter_disc=1, num_iter_gen=1)
            print(f'epoch: {epoch}, batch: {batch_idx}    ', end='\r')
        show_generator(dcgan.generator, seed)
