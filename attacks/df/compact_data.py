#to compact data into [2, -2, 3, -8...] version
#need to first call makedata.py and then compact data

import numpy as np
import math
import os 
import argparse
import logging
import configparser
import const 
import glob
import multiprocessing as mp
import pandas as pd
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
logger = logging.getLogger('df-compact')


LENGTH = 1500

def init_logger():
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

def parallel(flist,n_jobs = 20): 
    pool = mp.Pool(n_jobs)
    data_dict = pool.map(compact, flist)
    return data_dict

def compact(x, MON_SITE_NUM = 100):
    new_x = []
    sign = np.sign(x[0])

    cnt = 0
    for e in x:
        if np.sign(e) == sign: 
            cnt += 1
        else:
            new_x.append(int(cnt * sign))
            cnt = 1
            sign = np.sign(e)
    new_x.append(int(cnt * sign))
    return new_x


if __name__== '__main__':
    '''initialize logger'''
    logger = init_logger()
    
    '''read config file'''
    cf = read_conf(const.confdir)
    MON_SITE_NUM = int(cf['monitored_site_num'])
    MON_INST_NUM = int(cf['monitored_inst_num'])
    if cf['open_world'] == '1':
        UNMON_SITE_NUM = int(cf['unmonitored_site_num'])
        
    '''read in arg'''
    parser = argparse.ArgumentParser(description='DF feature compression')
    parser.add_argument('data',
                        metavar='<traces path>',
                        help='Path to the directory with the traffic traces to be simulated.')
    args = parser.parse_args()
    

    outputdir = const.outputdir+ args.data.split('/')[-1].split('.')[0] + '_compact.npy'

    data = np.load(args.data).item()
    x, y = data['feature'], data['label']
    compact_x = parallel(x)
    compact_x = pad_sequences(compact_x, padding ='post', truncating = 'post', value = 0, maxlen = LENGTH)

    data_dict = {'feature': compact_x, "label": y}
    np.save(outputdir, data_dict)
    logger.info("Save to file {}".format(outputdir))

