import numpy as np 
import argparse
import logging
import configparser
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedShuffleSplit,ShuffleSplit
from sklearn.metrics import confusion_matrix
import const
import multiprocessing
import random
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler
import os

random.seed(1123)
np.random.seed(1123)

def init_logger():
    logger = logging.getLogger('decision')
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




def read_conf(file):
    cf = configparser.ConfigParser()
    cf.read(file)  
    return dict(cf['default'])


def relax_acc(conf_mat, low = 0, upper = 0):
    s = 0.0
    for k in range(low,upper):
        s += conf_mat.diagonal(offset = k).sum()
    return s

if __name__ == '__main__':
    '''initialize logger'''
    logger = init_logger()
    '''read config'''
    parser = argparse.ArgumentParser(description='k-FP decision finding')
    parser.add_argument('p',
                        metavar='<train data dir>',
                        help='Path to the directory of the extracted training features')
    args = parser.parse_args()
    
    
    logger.info('loading data...')
    dic = np.load(args.p, allow_pickle=True).item()
    
    X = np.array(dic['feature'])
    y = np.array(dic['label'])

    model = RandomForestClassifier(n_jobs=-1, n_estimators=1000, oob_score=True)
    model.fit(X,y)
    modeldir = args.p.split('/')[-1].split('.')[0] +'.pkl'
    modeldir = os.path.join(const.modeldir, modeldir)
    joblib.dump(model, modeldir)
    logger.info("Model is saved to {}".format(modeldir))




    # acc  = []
    # result = []
    # folder_num = 0
    # for train_index, test_index in sss.split(X,y):
    #   logger.info('Testing fold %d'%folder_num)
    #   folder_num += 1 
    #   X_train, X_test = X[train_index], X[test_index]
    #   y_train, y_test = y[train_index], y[test_index]
    #   model.fit(X_train, y_train)
    #   y_pred = model.predict(X_test)
    #   acc.append(model.score(X_test,y_test))
    #   conf_mat = confusion_matrix(y_test,y_pred,labels=list(range(0,10)))
    #   result.append(relax_acc(conf_mat,-2,3))
    #   logger.info("Confusion matrix: \n{}".format(conf_mat))
    # acc = np.array(acc)
    # result = 1.0*np.array(result)/len(y_test)
    # logger.info("Average acc is         {:.4f} +- {:.4f}".format(acc.mean(),acc.std()))
    # logger.info("Average relaxed acc is {:.4f} +- {:.4f}".format(result.mean(),result.std()))