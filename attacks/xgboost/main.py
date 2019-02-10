#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 13:13:28 2018

"""
import time
import random
import numpy as np
import logging
import glob
import os
import sys
import subprocess
import argparse
from os import makedirs
import constants as ct
from xgboost import XGBClassifier
from sklearn.externals import joblib 



logger = logging.getLogger('xgboost')

def config_logger(args):
    # Set file
    log_file = sys.stdout
    if args.log != 'stdout':
        log_file = open(args.log, 'w')
    ch = logging.StreamHandler(log_file)

    # Set logging format
    ch.setFormatter(logging.Formatter(ct.LOG_FORMAT))
    logger.addHandler(ch)

    # Set level format
    logger.setLevel(logging.INFO)



def parse_arguments():

    parser = argparse.ArgumentParser(description='XGboost split algorithm.')

    parser.add_argument('t',
                        metavar='<traces path>',
                        help='Path to the directory with the traffic traces to be simulated.')
    parser.add_argument('-mode',
                        metavar='<mode>',
                        default = 'train',
                        help='Extract features for training set or test set.')
    parser.add_argument('-model',
                        metavar='<model>',
                        default = None,
                        help='path of model')
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


if __name__ == '__main__':
    args = parse_arguments()
    if args.mode == 'train':
        logger.info('loading data...')
        dic = np.load(args.t).item()   
        X = np.array(dic['feature'])
        y = np.array(dic['label'])        

        logger.info('Training...')
        logger.info("Training data shape: {}".format(X.shape))
        t = time.time()
        
        model = XGBClassifier()
        model.fit(X,y)
        logger.info("trainin time is {:.4f} s".format((time.time()-t)))
        logger.info(model)
        model_path = os.path.join( ct.modeldir, args.t.split('/')[-1].split('.')[0]) +'.pkl'
        joblib.dump(model, model_path)
    elif args.mode == 'test':
        model =  joblib.load(args.model)
        if args.model == None:
            logger.error('Please specify the model path!')
        else:
            tmp = os.path.join(args.t, '*.npy')
            flist = glob.glob(tmp)
            testfolder = os.path.join(ct.scoredir,args.t.split('/')[-2])
            print("testfolder:",testfolder)
            if not os.path.exists(testfolder):
                makedirs(testfolder)           
            for f in flist:
                logger.info('Processing {}'.format(f))
                fname = f.split('/')[-1].split('.')[0]
                dic = np.load(f).item()   
                X = np.array(dic['feature'])
#                location = np.array(dic['location'])
                truesplits = dic['truesplits']
                proba_y = model.predict_proba(X)
                dic['score'] = proba_y
                outputdir = os.path.join(testfolder, fname+'-score')
                np.save(outputdir,dic)
    elif args.mode == 'debug':
        dimension = int(args.t)
        X= np.random.random((8000,dimension))
        y = np.random.randint(0,2,(8000,))
        model = XGBClassifier()
        t = time.time()
        for i in range(5):
            model.fit(X,y)
        print("trainin time is {:.4f} s".format((time.time()-t)/5.0))
    else:
        logger.error('Mode error:{}!!'.format(args.mode))               