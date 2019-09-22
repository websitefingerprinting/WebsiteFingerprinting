from keras import backend as K
from keras.utils import np_utils
from keras.optimizers import Adamax
from model import DFNet
import numpy as np
import time
import random
import os
import argparse
import logging
import const
import keras
import tensorflow as tf
config = tf.ConfigProto( device_count = {'GPU': 1 , 'CPU': 20} ) 
config.gpu_options.allow_growth = True
sess = tf.Session(config=config) 
keras.backend.set_session(sess)

def init_logger():
    logger = logging.getLogger('kf')
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter(const.LOG_FORMAT)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger

def loadData(fpath):
	train = np.load(fpath).item()
	train_X ,train_y = train['feature'], train['label']
	return train_X, train_y


if __name__ == "__main__":
    random.seed(0)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    EXP_Type = 'OpenWorld_NoDef'
    print ("Experimental Type: ", EXP_Type)
    # network and training
    NB_EPOCH = 30
    print ("Number of Epoch: ", NB_EPOCH)
    BATCH_SIZE = 128
    VERBOSE = 1
    LENGTH = 5000
    OPTIMIZER = Adamax(lr=0.002, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0)

    NB_CLASSES = 100+1 # number of outputs: 95 Monitored websites + 1 Unmonitored websites
    INPUT_SHAPE = (LENGTH,1)

    '''initialize logger'''
    logger = init_logger()
    '''read config'''
    parser = argparse.ArgumentParser(description='k-FP attack')
    parser.add_argument('feature_path',
                        metavar='<feature path>',
                        help='Path to the directory of the extracted features')
    args = parser.parse_args()



    X_train, y_train = loadData(args.feature_path)
    K.set_image_dim_ordering("tf") # tf is tensorflow
    # consider them as float and normalize
    X_train = X_train.astype('float32')
    y_train = y_train.astype('float32')
    # print(y_train)


    # we need a [Length x 1] x n shape as input to the DFNet (Tensorflow)
    X_train = X_train[:, :,np.newaxis]


    print(X_train.shape[0], 'training samples')


    # # convert class vectors to binary class matrices
    # y_train = np_utils.to_categorical(y_train, NB_CLASSES)
    # y_valid = np_utils.to_categorical(y_valid, NB_CLASSES)


    print ("Preparing Data for training")
    # initialize the optimizer and model
    print (time.sleep(2))
    model = DFNet.build(input_shape=INPUT_SHAPE, classes=NB_CLASSES)

    model.compile(loss="categorical_crossentropy", optimizer=OPTIMIZER,
    	metrics=["accuracy"])
    print ("Model compiled")

    # Start training
    history = model.fit(X_train, y_train,
    		batch_size=BATCH_SIZE, epochs=NB_EPOCH, verbose=VERBOSE,validation_split=0.1)

    # Save model
    print ("Saving Model")
    model_id = args.feature_path.split('/')[-1].split('.')[0].split('_train')[0]
    savedpath = os.path.join(const.modeldir,'%s.h5'%str(model_id))
    model.save(savedpath)
    print ("Saving Model Done!", savedpath)

