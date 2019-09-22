#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 10 16:28:28 2018

@author: aaron
"""
from keras.models import load_model
# from train import *
# from makedata import *
import sys
import logging
import argparse
import configparser
import const
import numpy as np


import keras
import tensorflow as tf
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
config = tf.ConfigProto( device_count = {'GPU': 1 , 'CPU': 20} ) 
config.gpu_options.allow_growth = True
sess = tf.Session(config=config) 
keras.backend.set_session(sess)


logger = logging.getLogger('df')

def read_conf(file):
    cf = configparser.ConfigParser()
    cf.read(file)  
    return dict(cf['default'])
def config_logger(args):
    # Set file
    log_file = sys.stdout
    if args.log != 'stdout':
        log_file = open(args.log, 'w')
    ch = logging.StreamHandler(log_file)

    # Set logging format
    ch.setFormatter(logging.Formatter(const.LOG_FORMAT))
    logger.addHandler(ch)

    # Set level format
    logger.setLevel(logging.INFO)

def parse_arguments():

    parser = argparse.ArgumentParser(description='Evaluate.')

    parser.add_argument('-m',
                        metavar='<model path>',
                        help='Path to the directory of the model')
    parser.add_argument('-p',
                        metavar='<feature path>',
                        help='Path to the directory of the extracted features')

    parser.add_argument('--log',
                        type=str,
                        dest="log",
                        metavar='<log path>',
                        default='stdout',
                        help='path to the log file. It will print to stdout by default.')
    # Parse arguments
    args = parser.parse_args()
    config_logger(args)
    return args

def score_func(ground_truths, predictions):
    global MON_SITE_NUM
    tp, wp, fp, p, n = 0, 0, 0, 0 ,0
    for truth,prediction in zip(ground_truths, predictions):
    #    if truth >= MON_SITE_NUM:
     #       continue
        if truth < MON_SITE_NUM:
            p += 1
        else:
            n += 1
        if prediction < MON_SITE_NUM:
            if truth == prediction:
                tp += 1
            else:
                if truth < MON_SITE_NUM:
                    wp += 1
                    # logger.info('Wrong positive:%d %d'%(truth, prediction))
                else:
                    fp += 1
                    # logger.info('False positive:%d %d'%(truth, prediction))
    print('{} {} {} {} {}'.format(tp, wp, fp, p, n))
    try:
        r_precision = tp*n / (tp*n+wp*n+r*p*fp)
    except:
        r_precision = 0.0
    # logger.info('r-precision:%.4f',r_precision)
    # return r_precision
    return tp/p




    
if __name__ == '__main__':    
    global MON_SITE_NUM
    args = parse_arguments()
    # logger.info("Arguments: %s" % (args))
    cf = read_conf(const.confdir)
    MON_SITE_NUM = int(cf['monitored_site_num'])
    
    
    model = load_model(args.m)

    # logger.info('loading test data...')
    dic = np.load(args.p).item()   
    X = np.array(dic['feature'])
    y = np.array(dic['label'])
    if y.shape[-1] > 1:
        #means the data is one-hot encoded
        y = np.argmax(y, axis= 1)
    
    if len(X.shape) < 3:
        X = X[:, :, np.newaxis]

    y_pred = model.predict(X)
    y_pred = np.argmax(y_pred,axis = 1)
    print(sum(y_pred==MON_SITE_NUM))
    score_func(y, y_pred)
