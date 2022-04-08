#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is for experiment: random number of splits

@author: aaron
"""
import logging
import glob 
import multiprocessing as mp 
import os 
os.environ["CUDA_VISIBLE_DEVICES"]="1"
import sys
from keras.models import load_model
import argparse
import numpy as np
import configparser
from keras.preprocessing.sequence import pad_sequences
import const
import pandas as pd 
import tensorflow as tf
import keras 


config = tf.ConfigProto( device_count = {'GPU': 1 , 'CPU': 20} ) 
config.gpu_options.allow_growth = True
sess = tf.Session(config=config) 
keras.backend.set_session(sess)

logger = logging.getLogger('df')
LENGTH = 10000
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

    parser = argparse.ArgumentParser(description='Random Evaluate.')

    parser.add_argument('-m',
                        metavar='<model path>',
                        help='Path to the directory of the model')
    parser.add_argument('-p',
                        metavar='<raw feature path>',
                        help='Path to the directory of the extracted features')   
    parser.add_argument('-mode',
                        metavar='<head or other>',
                        help='To test head or other')    

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

def parallel(fdirs, n_jobs = 20): 
    # pool = mp.Pool(n_jobs)
    # pool.map(pred_sing_trace, fdirs)
    for fdir in fdirs:
        pred_sing_trace(fdir)

def extractfeature(f):
    fname = f.split('/')[-1]
    with open(f,'r') as f:
        tcp_dump = f.readlines()
#            return tcp_dump, 1

    feature = pd.Series(tcp_dump).str.slice(0,-1).str.split('\t',expand = True).astype("float")
    feature = np.array(feature.iloc[:,1]).astype("int")
    return feature

def pred_sing_trace(fdir):
    global MON_SITE_NUM, model
    y_dirs = glob.glob(os.path.join(fdir, '*'))
    y_dirs.sort(key=lambda d: int(d.split('/')[-1])) # remember to sort!!
    # logger.info("Process {}".format(y_dirs)) 
    X_test  = []
    [X_test.append(extractfeature(f)) for f in y_dirs]
    X_test = pad_sequences(X_test, padding ='post', truncating = 'post', value = 0, maxlen = LENGTH)
    X_test = X_test[:, :, np.newaxis]
    y_pred = model.predict(X_test)
    y_pred = np.argmax(y_pred, axis = 1)

    outputdir = os.path.join(const.randomdir, fdir.split('/')[-3], fdir.split('/')[-2])
    trace_id = fdir.split('/')[-1]
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    with open(os.path.join(outputdir,trace_id + '-predresult.txt'),'w') as f:
        [f.write(str(y)+'\n') for y in y_pred]
    # logger.info("Write into file {}".format(os.path.join(outputdir,trace_id + '-predresult.txt')))

    
if __name__ == '__main__':    
    global MON_SITE_NUM, model
    args = parse_arguments()
    # logger.info("Arguments: %s" % (args))
    cf = read_conf(const.confdir)
    MON_SITE_NUM = int(cf['monitored_site_num'])
    
    
    model = load_model(args.m)

    testfolder = args.p
    fdirs = glob.glob(os.path.join(args.p,args.mode,'*'))
    #     pred_sing_trace((f,scaler,model))
    parallel(fdirs)

    # dic = np.load(args.p).item()   
    # X = np.array(dic['feature'])
    # y = np.array(dic['label'])
    # X = scaler.transform(X)
    # logger.info('data are transformed into [-1,1]')

    # y_pred = model.predict(X)
    # score_func(y, y_pred)
