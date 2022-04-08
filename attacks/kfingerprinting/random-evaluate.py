#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is for experiment: random number of splits

@author: aaron
"""
from main import *
import const as ct
import logging
import glob
import multiprocessing as mp
from extract import TOTAL_FEATURES
logger = logging.getLogger('kf')
global trainleaves
global model
import  os

####note I modified get_single_neighbour in this code!!!!!!!!!!


def parse_arguments():

    parser = argparse.ArgumentParser(description='Evaluate.')

    parser.add_argument('-m',
                        metavar='<model path>',
                        help='Path to the directory of the model')
    parser.add_argument('-p',
                        metavar='<raw feature path>',
                        help='Path to the directory of the extracted features')
    parser.add_argument('-o',
                        metavar='<leaf path>',
                        help='Path to the directory of the extracted features')    
    parser.add_argument('-mode',
                        metavar='<head or other>',
                        help='To test head or other folder') 
    parser.add_argument('--log',
                        type=str,
                        dest="log",
                        metavar='<log path>',
                        default='stdout',
                        help='path to the log file. It will print to stdout by default.')
    # Parse arguments
    args = parser.parse_args()
    return args



def init_logger():
    logger = logging.getLogger('kf')
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


# def hdist(leaf1,leaf2):
#     if len(leaf1) != len(leaf2):
#         raise Exception("hdist called with wrong lengths {} {}".format(len(leaf1), len(leaf2)))
#     d = 0
#     for i in range(0,len(leaf1)):
#         d += hamming_dist(leaf1[i],leaf2[i])
#     return d

# def hamming_dist(x,y):
#     return 1 - int(x==y)

# def get_single_neighbor(testleaf):
#     # logger.info('Getting neighbor of class %d', testleaf[1])
#     global trainleaves
#     K = 3
#     dists  = []
#     for j, trainleaf in enumerate(trainleaves):
#         dists.append(hdist(testleaf,trainleaf[0]))
#     guessclasses_ind = heapq.nsmallest(K, enumerate(dists), key=lambda x: x[1]) 
#     guessclasses = []
#     for i in guessclasses_ind:
#         guessclasses.append(trainleaves[i[0]][1])
#     if len(set(guessclasses)) == 1:
#         return guessclasses[0]
#     else:
#         return 100


def get_single_neighbor(testleaf):
    global trainleaves, MON_SITE_NUM
    K = 3
    # print(trainleaves[:2])
    trainleaf, trainlabel = list(zip(*trainleaves))[0], list(zip(*trainleaves))[1]
    trainleaf = np.array(trainleaf)
    trainlabel = np.array(trainlabel)
    atile = np.tile(testleaf, (trainleaf.shape[0],1))
    dists = np.sum(atile != trainleaf, axis = 1)
    k_neighbors = trainlabel[np.argsort(dists)[:K]]
    if len(set(k_neighbors)) == 1:
        return k_neighbors[0]
    else:
        return MON_SITE_NUM

def extractfeature(f):
    global MON_SITE_NUM
    fname = f.split('/')[-1].split(".")[0]
    # logger.info('Processing %s...'%fname)
    try:
        if '-' in fname:
            label = fname.split('-')
            label = (int(label[0]), int(label[1]))
        else:
            label = (MON_SITE_NUM, int(fname))
        with open(f,'r') as f:
            tcp_dump = f.readlines()
        feature = TOTAL_FEATURES(tcp_dump)
        return (feature, label)
    except Exception as e:
        # a trace that is too short
        return ([0] * 175, label)

def pred_sing_trace(fdir):
    global model
    y_dirs = glob.glob(os.path.join(fdir, '*'))
    y_dirs.sort(key=lambda d: int(d.split('/')[-1])) # remember to sort!!
    X_test  = []
    y_pred = []
    [X_test.append(extractfeature(f)[0]) for f in y_dirs]
    testleaves= model.apply(X_test)
    [y_pred.append(get_single_neighbor(testleaf)) for testleaf in testleaves]


    outputdir = os.path.join(ct.randomdir, fdir.split('/')[-3], fdir.split('/')[-2])
    trace_id = fdir.split('/')[-1]

    with open(os.path.join(outputdir, trace_id + '-predresult.txt'),'w') as f:
        [f.write(str(y)+'\n') for y in y_pred]

def parallel(fdirs,n_jobs = 20):
    pool = mp.Pool(n_jobs)
    pool.map(pred_sing_trace, fdirs)    

if __name__ == '__main__':   
    global trainleaves, model, MON_SITE_NUM
    init_logger()
    args = parse_arguments()
    logger.info("Arguments: %s" % (args))
    cf = read_conf(ct.confdir)
    MON_SITE_NUM = int(cf['monitored_site_num'])
    logger.info('loading model...')
    model =  joblib.load(args.m)
    train_leaf = np.load(args.o, allow_pickle = True).item()
    trainleaves = list(train_leaf)


    testfolder = args.p
    fdirs = glob.glob(os.path.join(args.p,args.mode,'*'))
    outputdir = os.path.join(ct.randomdir, fdirs[0].split('/')[-3], fdirs[0].split('/')[-2])
    print(outputdir)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    # for f in fdirs:
    #     pred_sing_trace((f,model))
    parallel(fdirs)

    


