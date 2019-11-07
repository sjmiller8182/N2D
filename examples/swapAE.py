import os
import n2d
from n2d import datasets as data
import random as rn
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use(['seaborn-white', 'seaborn-paper'])
sns.set_context("paper", font_scale=1.3)
matplotlib.use('agg')
import tensorflow as tf
from keras import backend as K

import tensorflow as tf
import sys
import umap
from keras.layers import Dense, Input
from keras.models import Model

x,y, y_names = data.load_fashion()


class denoisingAutoEncoder:
    def __init__(self, dims, noise_factor = 0.5, act = 'relu'):
        self.noise_factor = noise_factor
        self.dims = dims
        self.act = act
        self.x = Input(shape = (dims[0],), name = 'input')
        self.h = self.x
        n_stacks = len(self.dims) - 1
        for i in range(n_stacks - 1):
            self.h = Dense(self.dims[i + 1], activation = self.act, name = 'encoder_%d' %i)(self.h)
        self.h = Dense(self.dims[-1], name = 'encoder_%d' % (n_stacks -1))(self.h)
        for i in range(n_stacks - 1, 0, -1):
            self.h = Dense(self.dims[i], activation = self.act, name = 'decoder_%d' % i )(self.h)
        self.h = Dense(dims[0], name = 'decoder_0')(self.h)

        self.Model = Model(inputs = self.x, outputs = self.h)

    def add_noise(self, x):
        # denoising mechanism from lovely keras blog post:
        # https://blog.keras.io/building-autoencoders-in-keras.html
        x_clean = x
        x_noisy = x_clean + self.noise_factor * np.random.normal(loc = 0.0, scale = 1.0, size = x_clean.shape)
        x_noisy = np.clip(x_noisy, 0., 1.)

        return x_clean, x_noisy

    def pretrain(self, dataset, batch_size = 256, pretrain_epochs = 1000,
                     loss = 'mse', optimizer = 'adam',weights = None,
                     verbose = 0, weightname = 'fashion'):
        if weights == None:
            x, x_noisy = self.add_noise(dataset)
            self.Model.compile(
                loss = loss, optimizer = optimizer
            )
            self.Model.fit(
                x_noisy, x,
                batch_size = batch_size,
                epochs = pretrain_epochs
            )
            # make this less stupid
            self.Model.save_weights("weights/" + weightname + "-" +
                                    str(pretrain_epochs) +
                                    "-ae_weights.h5")
        else:
            self.Model.load_weights(weights)


n_clusters = 10

model = n2d.n2d(x, autoencoder = denoisingAutoEncoder, nclust = n_clusters, ae_args={'noise_factor': 0.5})

model.preTrainEncoder(weight_id="fashion_denoise")


manifoldGMM = n2d.UmapGMM(n_clusters)

model.predict(manifoldGMM)

model.visualize(y, names=None, dataset = "fashion_denoise", nclust = n_clusters)
print(model.assess(y))