import numpy as np
import tensorflow as tf

"""
refs:
- [TensorFlow Tutorials](https://tensorflow.google.cn/tutorials/generative/dcgan)
- [TensorFlow DCGAN](https://github.com/carpedm20/DCGAN-tensorflow/blob/master/model.py)
- [Pytorch DCGAN Example](https://github.com/pytorch/examples/blob/master/dcgan/main.py)
- [Keras DCGAN](https://github.com/jacobgil/keras-dcgan/blob/master/dcgan.py)
"""


class DCGAN():
    def __init__(self, image_shape=(64, 64, 3), glr=1e-4, dlr=1e-4, nz=100, ngf=64, ndf=64, ngfc=1024, ndfc=1024):
        self.image_shape = image_shape
        self.image_height, self.image_width, self.image_channel = image_shape
        self.nz = nz
        self.ngf = ngf
        self.ndf = ndf
        self.ngfc = ngfc
        self.ndfc = ndfc

        self.generator = self.make_generator()
        self.discriminator = self.make_discriminator()

        self.cross_entropy = tf.keras.losses.BinaryCrossentropy()

        self.generator_optimizer = tf.keras.optimizers.Adam(glr)
        self.discriminator_optimizer = tf.keras.optimizers.Adam(dlr)

    def make_generator(self):
        map_height, map_width = self.image_height, self.image_width
        for _ in range(4):
            map_height = conv_out_size_same(map_height, stride=2)
            map_width = conv_out_size_same(map_width, stride=2)

        return tf.keras.Sequential([
            tf.keras.layers.Dense(
                map_height*map_width*self.ngf*8, use_bias=False, input_shape=(self.nz,)),
            tf.keras.layers.Reshape((map_height, map_width, self.ngf*8)),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.ReLU(),

            tf.keras.layers.Conv2DTranspose(
                self.ngf*4, (5, 5), strides=(2, 2), padding='same', use_bias=False),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.ReLU(),

            tf.keras.layers.Conv2DTranspose(
                self.ngf*2, (5, 5), strides=(2, 2), padding='same', use_bias=False),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.ReLU(),

            tf.keras.layers.Conv2DTranspose(self.ngf, (5, 5), strides=(
                2, 2), padding='same', use_bias=False),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.ReLU(),

            tf.keras.layers.Conv2DTranspose(
                self.image_shape[-1],  (5, 5), strides=(2, 2), padding='same', use_bias=False),
            tf.keras.layers.Activation('tanh')
        ], name="Generator")

        return model

    def make_discriminator(self):
        return tf.keras.Sequential([
            tf.keras.layers.Conv2D(self.ndf, (5, 5), strides=(2, 2), padding='same',
                                   input_shape=self.image_shape),
            tf.keras.layers.LeakyReLU(),

            tf.keras.layers.Conv2D(
                self.ndf*2, (5, 5), strides=(2, 2), padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.LeakyReLU(),

            tf.keras.layers.Conv2D(
                self.ndf*4, (5, 5), strides=(2, 2), padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.LeakyReLU(),

            tf.keras.layers.Conv2D(
                self.ndf*8, (5, 5), strides=(2, 2), padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.LeakyReLU(),

            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(1),
            tf.keras.layers.Activation('sigmoid')
        ], name="Discriminator")

    def summary(self):
        self.generator.summary()
        print()
        self.discriminator.summary()

    @tf.function
    def train_step(self, images, num_iter_disc=5, num_iter_gen=1):

        batch_size = images.shape[0]
        true_labels = tf.ones(
            (batch_size, 1)) + tf.random.uniform((batch_size, 1), minval=-0.2, maxval=0.2)
        wrong_labels = tf.zeros(
            (batch_size, 1)) + tf.random.uniform((batch_size, 1), minval=0, maxval=0.2)

        with tf.GradientTape() as disc_tape:
            real_output = self.discriminator(images, training=True)
            real_loss = tf.keras.losses.binary_crossentropy(
                true_labels, real_output)

            noise = gen_random((batch_size, self.nz))
            generated_images = self.generator(noise, training=True)
            fake_output = self.discriminator(generated_images, training=True)
            fake_loss = tf.keras.losses.binary_crossentropy(
                wrong_labels, fake_output)
            disc_loss = real_loss + fake_loss

        gradients_of_discriminator = disc_tape.gradient(
            disc_loss, self.discriminator.trainable_variables)
        self.discriminator_optimizer.apply_gradients(
            zip(gradients_of_discriminator, self.discriminator.trainable_variables))

        with tf.GradientTape() as gen_tape:
            noise = gen_random((batch_size, self.nz))
            generated_images = self.generator(noise, training=True)
            real_output = self.discriminator(images, training=True)
            fake_output = self.discriminator(generated_images, training=True)
            gen_loss = tf.keras.losses.binary_crossentropy(
                true_labels, fake_output)

        gradients_of_generator = gen_tape.gradient(
            gen_loss, self.generator.trainable_variables)
        self.generator_optimizer.apply_gradients(
            zip(gradients_of_generator, self.generator.trainable_variables))


def conv_out_size_same(size, stride=2):
    return int(np.ceil(size / stride))


def gen_random(shape):
    noise = tf.random.normal(shape=shape, mean=0.0, stddev=np.exp(-1.0/np.pi))
    return noise
