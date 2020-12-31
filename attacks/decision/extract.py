import sys
import subprocess
import numpy
import numpy as np
import os
import pandas as pd

import math
import os 
import argparse
import logging
import configparser
import const 
import glob
import multiprocessing as mp
import heapq

def extract(times, sizes):
    #params
    K = 500
    stride = 25
    density_K = 100
    
    features = []
    #Transmission size,time, outgoing pkt num features: 3#
    features.append(len(sizes))
    features.append(times[-1] - times[0])
    features.append( (sizes > 0).sum())
    
    nexttimes = times[1:]
    nexttimes = np.append(nexttimes, times[0])
    #inter arrival time mean, std : 2#
    ita = (nexttimes - times)[:-1]
    features.append(ita.mean())
    features.append(ita.std())
    #k largest ita mean, std, first 100 ita, percentile:  K + 2 + 4#
    nlargest = heapq.nlargest(K, ita)
    features.append(np.array(nlargest).mean())
    features.append(np.array(nlargest).std())
    features.append(np.percentile(nlargest,25))
    features.append(np.percentile(nlargest,50))
    features.append(np.percentile(nlargest,75))
    features.append(np.percentile(nlargest,100))
    features.extend(nlargest + [0]*(K - len(nlargest)))

    
    # #outgoing pkt densities's mean, std, how many "dense" outgoing pkts  2#
    # densities = []
    # sparses = [] 
    # index = np.where(sizes > 0)[0]
    # for ind in index:
    #     lower, upper = max(0, ind-stride), min(ind+stride, len(times)-1)
    #     density = 1.0* ((sizes[lower:upper] > 0).sum()) / (times[upper] - times[lower])
    #     if density <= 1.0/(times[upper] - times[lower]):
    #         sparses.append(density)
    #     else:
    #         densities.append(density)  
    # densities = np.array(densities)
    # features.append(densities.mean())
    # features.append(densities.std())
    # features.append(len(densities))
    
    # #Top k outgoing packet density std, mean ,percentile: K + 2 + 4# 
    # nlargest = heapq.nlargest(density_K, densities)
    # features.append(np.array(nlargest).mean())
    # features.append(np.array(nlargest).std())
    # features.append(np.percentile(nlargest,25))
    # features.append(np.percentile(nlargest,50))
    # features.append(np.percentile(nlargest,75))
    # features.append(np.percentile(nlargest,100))    
    # features.extend(nlargest + [0]*(density_K - len(nlargest)))
    return features

    

        
        
        
        
def init_logger():
    logger = logging.getLogger('decision')
    logger.setLevel(logging.INFO)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter(const.LOG_FORMAT)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger


def parallel(flist,n_jobs = 20):
    pool = mp.Pool(n_jobs)
    features = pool.map(work, flist)
    return features

def work(file):
    logger.debug("Processing file {}".format(file))
    with open(file,'r') as f:
        f = f.readlines()
    df = pd.Series(f)
    df = df.str.slice(0,-1).str.split('\t',expand=True)
    times = np.array(df.iloc[:,0].astype('float') )
    sizes = df.iloc[:,1].astype('int')
    sizes =  np.array((sizes/abs(sizes))).astype('int')

  
    features = extract(times, sizes)
    return features
    

if __name__== '__main__':
    '''initialize logger'''
    logger = init_logger()
        
    '''read in arg'''
    parser = argparse.ArgumentParser(description='Decision finding')
    parser.add_argument('traces_path',
                        metavar='<traces path>',
                        help='Path to the directory with the traffic traces to be simulated.')
    parser.add_argument('-num',
                        type = int,
                        default = None,
                        metavar='<num of the traces in a l-trace>',
                        help='..')    
    args = parser.parse_args()
    data_dict = {'feature':[],'label':[]}
    fpath = os.path.join(args.traces_path, '*/*.merge')
    flist = glob.glob(fpath)
    if len(flist) == 0:
        fpath = os.path.join(args.traces_path,'*.merge')
        flist = glob.glob(fpath)
        if len(flist)  == 0:
            logger.error('Path {} is incorrect!'.format(fpath))
    flist.sort(key=lambda d:int(d.split('/')[-1].split('.')[0]))



#    features= work(flist[0])
    
    data_dict['feature'] = parallel(flist,n_jobs = 20)
    #there will be a file record the number of merged traces in input folder
    if args.num == None:
        data_dict['label'] = np.load(os.path.join(args.traces_path,'num.npy'), allow_pickle = True) -2 
    else:
        data_dict['label'] = np.ones(len(data_dict['feature']))* (args.num-2)
    outputdir = const.featuredir+args.traces_path.split('/')[-2]
    np.save(outputdir,data_dict)        

    logger.debug('Save to %s.npy'%outputdir)
