import numpy as np
import sys
#for calculate the loss
from sklearn.metrics import log_loss
from sklearn.metrics.scorer import make_scorer

#import three machine learning models
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit

#for standardizing the data
from sklearn import preprocessing
from sklearn.model_selection import GridSearchCV

import os
from os import mkdir, listdir
from os.path import join, isdir, dirname
from time import strftime

import constants as ct

import configparser
import argparse
import logging
import random
import pandas

import pickle

from sklearn.externals import joblib


logger = logging.getLogger('cumul')
random.seed(1123)
np.random.seed(1123)
'''params'''
r = 1000

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
    logger.info('%4d %4d %4d %4d %4d'%(tp, wp, fp, p, n))
    try:
        r_precision = tp*n / (tp*n+wp*n+r*p*fp)
    except:
        r_precision = 0.0
    # logger.info('r-precision:%.4f',r_precision)
    # return r_precision
    return tp/p

def read_conf(file):
    cf = configparser.ConfigParser()
    cf.read(file)  
    return dict(cf['default'])


def parse_arguments():

    parser = argparse.ArgumentParser(description='It simulates adaptive padding on a set of web traffic traces.')

    parser.add_argument('fp',
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


#SVM with RBF kernel for open world!!
def GridSearch(train_X,train_Y):
    #find the optimal gamma
    param_grid = [
    { 
     'C': [2**11,2**13,2**15,2**17],
     'gamma' : [2**-3,2**-1,2**1,2**3]
    }
    ]

    my_scorer = make_scorer(score_func, greater_is_better=True)

    # clf = GridSearchCV(estimator = SVC(kernel = 'rbf'), param_grid = param_grid, \
    #     scoring = 'accuracy', cv = 10, verbose = 2, n_jobs = -1)
    clf = GridSearchCV(estimator = SVC(kernel = 'rbf'), param_grid = param_grid, \
        scoring = my_scorer, cv = 5, verbose = 1, n_jobs = -1)
    clf.fit(train_X, train_Y)
    # logger.info('Best estimator:%s'%clf.best_estimator_)
    # logger.info('Best_score_:%s'%clf.best_score_)
    return clf


if __name__ == '__main__':
    global MON_SITE_NUM
    args = parse_arguments()
    logger.info("Arguments: %s" % (args))

    cf = read_conf(ct.confdir)
    MON_SITE_NUM = int(cf['monitored_site_num'])


    logger.info('loading data...')
    dic = np.load(args.fp).item()   
    X = np.array(dic['feature'])
    y = np.array(dic['label'])
    

    #normalize the data
    scaler = preprocessing.MinMaxScaler((-1,1))
    X = scaler.fit_transform(X)  
    logger.info('data are transformed into [-1,1]')

    # find the optimal params
    logger.info('GridSearchCV...')
    clf = GridSearch(X,y)

   
    C = clf.best_params_['C']
    gamma = clf.best_params_['gamma']
    # C, gamma = 131072, 8.000000
    # C, gamma = 8192, 8.00
    logger.info('Best params are: %d %f'%(C,gamma))


    # sss = StratifiedShuffleSplit(n_splits=10, test_size=0.1, random_state=0)
    # ps,nps,tps,wps,fps = 0,0,0,0,0

    # folder_num = 0
    # for train_index, test_index in sss.split(X,y):
    #     # logger.info('Testing fold %d'%folder_num)
    #     folder_num += 1
    #     # print("TRAIN:", train_index, "TEST:", test_index)
    #     X_train, X_test = X[train_index], X[test_index]
    #     y_train, y_test = y[train_index], y[test_index]   
    #     model = SVC(C = C, gamma = gamma, kernel = 'rbf')
    #     model.fit(X_train, y_train)
    #     y_pred = model.predict(X_test)
    #     r_precision = score_func(y_test, y_pred)
    #     # logger.info('%d-presicion is %.4f'%(r, r_precision))


    model = SVC(C = C, gamma = gamma, kernel = 'rbf')
    model.fit(X, y)
    joblib.dump(model, 'ranpad2_0131_1719.pkl')
    print('model have been saved')

