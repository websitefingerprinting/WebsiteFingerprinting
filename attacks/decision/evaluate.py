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
from sklearn.externals import joblib 
from sklearn.preprocessing import MinMaxScaler
import os
from train import relax_acc
import pandas as pd
# from pprint import pprint
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

if __name__ == '__main__':
    '''initialize logger'''
    logger = init_logger()
    '''read config'''
    parser = argparse.ArgumentParser(description='k-FP decision finding')
    parser.add_argument('p',
                        metavar='<test feature path>',
                        help='Path to the directory of the test extracted features')
    parser.add_argument('-m',
                        metavar='<path of model>',
                        help='Path to the directory of the test extracted features')
    args = parser.parse_args()
    logger.info('loading model...')
    model =  joblib.load(args.m)  

    logger.info('loading data...')
    testname = args.p.split('/')[-1].split('.')[0]
    dic = np.load(args.p).item()   
    X_test = np.array(dic['feature'])
    y_test = np.array(dic['label'])
    # print(np.unique(y_test))
    y_pred = model.predict(X_test)  
    conf_mat = confusion_matrix(y_test,y_pred,labels=list(range(2-2,17-2)))
    print("Confusion matrix: \n{}".format(pd.DataFrame(conf_mat, columns = np.arange(2,17))))
    logger.info("Acc is {:.4f}, relax_acc is {:.4f}".\
        format(relax_acc(conf_mat,0,1)/len(y_test), relax_acc(conf_mat, -2,3)/len(y_test)))
    resultdir = os.path.join(const.outputdir, testname)
    '''Note the output is the number of splits = pages -1,  not pages or   labels = pages -2 '''
    data_dict = {"k": y_pred+1, "conf_mat": conf_mat}
    np.save(resultdir,data_dict)
    logger.info("K, conf_mat is saved to {}.npy".format(resultdir))
