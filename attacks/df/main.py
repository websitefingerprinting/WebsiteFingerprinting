#10-cv deep fingerprinting code
from keras import backend as K
from keras.utils import np_utils
from keras.optimizers import Adamax
from keras.utils import to_categorical
from model import DFNet
import numpy as np
import time
import random
import os
import argparse
import configparser
import logging
import const
import keras
import tensorflow as tf
from sklearn.model_selection import StratifiedShuffleSplit
config = tf.ConfigProto( device_count = {'GPU': 1 , 'CPU': 20} ) 
config.gpu_options.allow_growth = True
sess = tf.Session(config=config) 
keras.backend.set_session(sess)
def read_conf(file):
    cf = configparser.ConfigParser()
    cf.read(file)  
    return dict(cf['default'])


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

def score_func(ground_truths, predictions):
    global MON_SITE_NUM
    tp, wp, fp, p, n = 0, 0, 0, 0 ,0
    for truth,prediction in zip(ground_truths, predictions):
        if truth != MON_SITE_NUM:
            p += 1
        else:
            n += 1
        if prediction != MON_SITE_NUM:
            if truth == prediction:
                tp += 1
            else:
                if truth != MON_SITE_NUM:
                    wp += 1
                    # logger.info('Wrong positive:%d %d'%(truth, prediction))
                else:
                    fp += 1
                    # logger.info('False positive:%d %d'%(truth, prediction))
    # logger.info('{} {} {} {} {}'.format(tp, wp, fp, p, n))
    try:
        r_precision = tp*n / (tp*n+wp*n+r*p*fp)
    except:
        r_precision = 0.0
    # logger.info('r-precision:%.4f',r_precision)
    # return r_precision
    return tp, wp, fp, p, n



if __name__ == "__main__":
    cf = read_conf(const.confdir)
    MON_SITE_NUM = int(cf['monitored_site_num'])
    random.seed(0)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    EXP_Type = 'OpenWorld_NoDef'
    # print ("Experimental Type: ", EXP_Type)
    # network and training
    NB_EPOCH = 20
    # print ("Number of Epoch: ", NB_EPOCH)
    BATCH_SIZE = 128
    VERBOSE = 1
    LENGTH = 1500
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



    X, y = loadData(args.feature_path)
    K.set_image_dim_ordering("tf") # tf is tensorflow
    # consider them as float and normalize
    X = X.astype('float32')
    y = y.astype('float32')
    # print(y_train)


    # we need a [Length x 1] x n shape as input to the DFNet (Tensorflow)
    if len(X.shape) < 3:
        X = X[:, :,np.newaxis]
    if y.shape[1] == 1:
        y = y.flatten()
        y = to_categorical(y, num_classes = NB_CLASSES) 
    # print(X.shape[0], 'data samples')

    sss = StratifiedShuffleSplit(n_splits=10, test_size=0.1, random_state=0)
    tps, wps, fps, ps, ns = 0, 0, 0, 0, 0
    start_time = time.time()
    folder_num = 1
    for train_index, test_index in sss.split(X,y):
        # logger.info('Testing fold %d'%folder_num)
        folder_num += 1 
#       if folder_num > 2:
#           break
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        
        
        # initialize the optimizer and model
        # print (time.sleep(2))
        model = DFNet.build(input_shape=INPUT_SHAPE, classes=NB_CLASSES)

        model.compile(loss="categorical_crossentropy", optimizer=OPTIMIZER,
            metrics=["accuracy"])
        # print ("Model compiled")

        # Start training
        history = model.fit(X_train, y_train,
                batch_size=BATCH_SIZE, epochs=NB_EPOCH, verbose=VERBOSE,validation_split=0.1)

        y_pred = model.predict(X_test)
        y_pred = np.argmax(y_pred,axis = 1)
        y_test = np.argmax(y_test, axis= 1)

        tp, wp, fp, p, n = score_func(y_test, y_pred)
        tps += tp
        wps += wp
        fps += fp     
        ps += p
        ns += n  
        print("{:3d} {:3d} {:3d} {:3d} {:3d}".format(tp, wp, fp, p, n))
    print("{:3d} {:3d} {:3d} {:3d} {:3d}".format(tps, wps, fps, ps, ns))
    # print("time:", time.time()-start_time)

