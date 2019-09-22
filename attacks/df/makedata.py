#This turns dataset into [num, length] 1D sequences
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
logger = logging.getLogger('df')


LENGTH = 10000


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
    parser.add_argument('-mode',
                        metavar='<whether generate only train and/or test>',
                        help='train,test, all, whole',
                        default = "whole")
    parser.add_argument('-format',
                        metavar='<suffix of files>',
                        help='The suffix of files',
                        default = ".cell")
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

    flist = []
    for i in range(MON_SITE_NUM):
        for j in range(MON_INST_NUM):
            flist.append(  os.path.join( args.traces_path, str(i) + '-' + str(j) + args.format) )
    for i in range(UNMON_SITE_NUM):
        flist.append( os.path.join( args.traces_path, str(i)+ args.format) )

    if args.mode == "all":
        ##this is for evaluating front, 9:1 ,training : testing
        # fpath = os.path.join(args.traces_path,'*')
        # flist = glob.glob(fpath)
        data_dict = {'feature':[],'label':[]}
        raw_data_dict = parallel(flist, n_jobs = 20)
        features, label = zip(*raw_data_dict)
        features = pad_sequences(features, padding ='post', truncating = 'post', value = 0, maxlen = LENGTH)
        
        labels = to_categorical(label, num_classes = num_class) 

        train_X, test_X, train_y, test_y = train_test_split(features, labels, shuffle = True, test_size=0.1, stratify = label)

        logger.info("Training data:{}, {}, Testing data:{}, {}".format(train_X.shape, train_y.shape, \
                    test_X.shape,test_y.shape))
       

        data_dict['feature'], data_dict['label'] = train_X, train_y
        np.save(outputdir+"_train",data_dict)        

        logger.info('save to %s'% ( outputdir+"_train.npy"))

        data_dict['feature'], data_dict['label'] = test_X, test_y
        np.save(outputdir+"_test.npy",data_dict)        

        logger.info('save to %s'%(outputdir+"_test.npy"))
    elif args.mode == "whole":
        ##this is to generate a dataset without splitting into train and test
        # fpath = os.path.join(args.traces_path,'*')
        # flist = glob.glob(fpath)
        data_dict = {'feature':[],'label':[]}
        raw_data_dict = parallel(flist, n_jobs = 20)
        features, label = zip(*raw_data_dict)
        features = pad_sequences(features, padding ='post', truncating = 'post', value = 0, maxlen = LENGTH)
        
        labels = to_categorical(label, num_classes = num_class) 

        # train_X, test_X, train_y, test_y = train_test_split(features, labels, shuffle = True, test_size=0.1, stratify = label)

        logger.info("Data size:{}, {}".format(features.shape, labels.shape))
       

        data_dict['feature'], data_dict['label'] = features, labels
        np.save(outputdir,data_dict)        

        logger.info('save to %s'% ( outputdir+".npy"))

    elif args.mode == "train":
        #this is for glue training set 
        # fpath = os.path.join(args.traces_path,'*')
        # flist = glob.glob(fpath)
        data_dict = {'feature':[],'label':[]}
        raw_data_dict = parallel(flist, n_jobs = 20)
        features, label = zip(*raw_data_dict)
        features = pad_sequences(features, padding ='post', truncating = 'post', value = 0, maxlen = LENGTH)
        
        labels = to_categorical(label, num_classes = num_class) 

 
        logger.info("Training data:{}, {}".format(features.shape, labels.shape))


        data_dict['feature'], data_dict['label'] = features, labels
        np.save(outputdir+"_train",data_dict)        

        logger.info('save to %s'% ( outputdir+"_train.npy"))    
    elif args.mode == "test":
        #this is for glue testing set
        headfpath = os.path.join(args.traces_path, 'head/*/*')
        otherfpath = os.path.join(args.traces_path, 'other/*/*')
        headflist = glob.glob(headfpath)
        otherflist = glob.glob(otherfpath)


        raw_data_dict = parallel(headflist, n_jobs = 20)
        features, label = zip(*raw_data_dict)
        features = pad_sequences(features, padding ='post', truncating = 'post', value = 0, maxlen = LENGTH)
        labels = to_categorical(label, num_classes = num_class) 


        data_dict = {'feature':[],'label':[]}
        logger.info("Test head data:{}, {}".format(features.shape, labels.shape))
        data_dict['feature'], data_dict['label'] = features,labels
        np.save(outputdir+"_head.npy",data_dict)        

        logger.info('save to %s'%(outputdir+"_head.npy"))    


        if len(otherflist) > 1:
            data_dict = {'feature':[],'label':[]}
            raw_data_dict = parallel(otherflist, n_jobs = 20)
            features, label = zip(*raw_data_dict)
            features = pad_sequences(features, padding ='post', truncating = 'post', value = 0, maxlen = LENGTH)
            labels = to_categorical(label, num_classes = MON_SITE_NUM+1)  

            logger.info("Test other data:{}, {}".format(features.shape, labels.shape))
            data_dict['feature'], data_dict['label'] = features,labels
            np.save(outputdir+"_other.npy",data_dict)        
            logger.info('save to %s'%(outputdir+"_other.npy"))  
