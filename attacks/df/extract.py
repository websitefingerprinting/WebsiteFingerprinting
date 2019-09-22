#This turns dataset into [num, length] 1D sequences
import numpy as np
import math
import os 
from os.path import join
import argparse
import logging
import configparser
import const 
import multiprocessing as mp
import pandas as pd
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
logger = logging.getLogger('df')


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

def parallel(flist, n_jobs = 20): 
    pool = mp.Pool(n_jobs)
    data_dict = pool.map(extractfeature, flist)
    return data_dict

def extractfeature(f):
    global MON_SITE_NUM
    fname = f.split('/')[-1]
    # logger.info('Processing %s...'%fname)
#    try:
#        with open(f,'r') as f:
#            tcp_dump = f.readlines()
##            return tcp_dump, 1
#
#        feature = pd.Series(tcp_dump).str.slice(0,-2).str.split('\t',expand = True).astype(int)
#        print(feature)
#           feature = np.array(feature.iloc[:,1])
#
#        
#    except:
#        raise ValueError("..")
    with open(f,'r') as f:
        tcp_dump = f.readlines()
#            return tcp_dump, 1

    feature = pd.Series(tcp_dump).str.slice(0,-1).str.split('\t',expand = True).astype("float")
    feature = np.array(feature.iloc[:,1]).astype("int")
    if '-' in fname:
        label = fname.split('-')
        label = int(label[0])
    else:
        label = MON_SITE_NUM
    return (feature,label)


if __name__== '__main__':
    global MON_SITE_NUM
    '''initialize logger'''
    logger = init_logger()
    
    '''read config file'''
    cf = read_conf(const.confdir)
    MON_SITE_NUM = int(cf['monitored_site_num'])
    MON_INST_NUM = int(cf['monitored_inst_num'])
    num_class = MON_SITE_NUM
    if cf['open_world'] == '1':
        UNMON_SITE_NUM = int(cf['unmonitored_site_num'])
        num_class += 1
        
    '''read in arg'''
    parser = argparse.ArgumentParser(description='DF feature extraction')
    parser.add_argument('traces_path',
                        metavar='<traces path>',
                        help='Path to the directory with the traffic traces to be simulated.')
    parser.add_argument('-format',
                        metavar='<trace suffix>',
                        default = '.cell',
                        help='trace suffix')
    parser.add_argument('-l',
                        metavar='<feature length>',
                        type = int,
                        default = 5000,
                        help='generated feature length')

    args = parser.parse_args()
    
  
    # fpath = os.path.join(args.traces_path, '*/*')
    # flist = glob.glob(fpath)
    # if len(flist) == 0:
    #     fpath = os.path.join(args.traces_path,'*')
    #     flist = glob.glob(fpath)
    #     if len(flist)  == 0:
    #         logger.error('Path {} is incorrect!'.format(fpath))


    # raw_data_dict = parallel(flist,n_jobs = 20)
    # features, label = zip(*raw_data_dict)
    # features = pad_sequences(features, padding ='post', truncating = 'post', value = 0, maxlen = LENGTH)
    
    # labels = to_categorical(label, num_classes = MON_SITE_NUM+1) 
    
    outputdir = const.outputdir+args.traces_path.split('/')[-2]

    
    fpath = os.path.join(args.traces_path,'*')
    flist = []

    for i in range(MON_SITE_NUM):
        for j in range(MON_INST_NUM):
            flist.append(join(args.traces_path, str(i)+'-'+str(j)+args.format))
    for i in range(UNMON_SITE_NUM):
        flist.append(join(args.traces_path, str(i)+args.format))
    data_dict = {'feature':[],'label':[]}
    raw_data_dict = parallel(flist, n_jobs = 20)
    features, label = zip(*raw_data_dict)
    features = pad_sequences(features, padding ='post', truncating = 'post', value = 0, maxlen = args.l)
    
    labels = to_categorical(label, num_classes = num_class) 

    print("feature shape:{}, label shape:{}".format(features.shape, labels.shape))
    data_dict['feature'], data_dict['label'] = features, labels
    np.save(outputdir,data_dict)        

    logger.info('save to %s'% ( outputdir+".npy"))

