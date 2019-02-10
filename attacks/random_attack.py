##Analyse the results of Glue with split decision and findding
from subprocess import call
from os.path import join
import argparse
import logging
import sys
import os
import pandas as pd 
import glob
from pprint import pprint
import multiset as mts
import numpy as np

logger = logging.getLogger('random-atk-results')
NUM_OF_SENSITIVE = 100
def config_logger(args):
    # Set file
    log_file = sys.stdout
    if args.log != 'stdout':
        log_file = open(args.log, 'w')
    ch = logging.StreamHandler(log_file)

    # Set logging format
    LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
    ch.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(ch)

    # Set level format
    logger.setLevel(logging.INFO)

def parse_arguments():

    parser = argparse.ArgumentParser(description='XGboost split algorithm.')

    parser.add_argument('-truth',
                        metavar='<true webpages>',
                        help='dir of true webpages, ..../list')
    parser.add_argument('-pred',
                        metavar='<pred webpages>',
                        help='dir of pred webpages, .../x-preresults.txt')
    # parser.add_argument('-mode',
    #                     metavar='<head or other>',
    #                     help='to test head or other')
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

def ParseTruth(dir_truth):
    with open(dir_truth,'r') as f:
        lines = f.readlines()
    truth = []
    p, n = 0, 0
    # if mode == 'head':
    #     begin, end = 0,1
    # elif mode == 'other':
    #     begin, end = 1, len(lines)
    # print(lines[:4])
    for line in lines:
        names = line.split('\t')[:-1]
        mergelist = []
        for name in names:
            tmp = name.split('/')[-1]
            if '-' in tmp:
                p += 1
                tmp = int(tmp.split('-')[0])
            else:
                #nonsensitive webpage id
                n += 1
                tmp = NUM_OF_SENSITIVE
            mergelist.append(tmp)
        truth.append(mergelist)
    return truth, p, n 
def ParsePred(dir_pred):
    subfolder = 'head'
    r = glob.glob(join(dir_pred, subfolder,'*-predresult.txt'))
    r.sort(key = lambda x: int(x.split('/')[-1].split('-')[0]))
    pred = []
    for pdir in r:
        with open(pdir,'r') as f:
            lines = pd.Series(f.readlines()).str.slice(0,-1).astype('int')
        pred.append(list(lines))

    subfolder = 'other'
    r = glob.glob(join(dir_pred, subfolder,'*-predresult.txt'))
    r.sort(key = lambda x: int(x.split('/')[-1].split('-')[0]))
    for i,pdir in enumerate(r):
        with open(pdir,'r') as f:
            lines = pd.Series(f.readlines()).str.slice(0,-1).astype('int')   
        pred[i].extend(list(lines))
    return pred
if __name__ == '__main__':
    args = parse_arguments()
    truths, p, n = ParseTruth(args.truth)
    preds = ParsePred(args.pred)
    fp, wp, tp = 0, 0, 0 
    cnt = 0
    flag = 0 
    for truth, pred in zip(truths, preds):
        # print(truth)
        # print(pred)
        # print( )
        # cnt += 1
        # if cnt >6: 
        #     break
        l = len(truth)
        if len(pred) > l:
            pred = pred[:l]
        else:
            pred.extend( [NUM_OF_SENSITIVE] * (l-len(truth)))

        for tt, pp in zip(truth, pred):
            if pp < NUM_OF_SENSITIVE:
                if pp == tt:
                    tp += 1
                    flag = 1
                elif pp != tt and tt < NUM_OF_SENSITIVE:
                    wp += 1
                    flag= 1
                elif pp!= tt and tt == NUM_OF_SENSITIVE:
                    fp += 1
                    flag = 1
        # if flag :
        #     print("{} {} {} {} {}".format(tp,wp,fp, p, n))
        #     print(truth)
        #     print(pred) 
        # flag = 0

    print("{} {} {} {} {}".format(tp,wp,fp, p, n))
    
    # fp, tp = 0, 0 
    # cnt = 0
    # for truth, pred in zip(truths, preds):
    #     # cnt += 1
    #     # if cnt > 20:
    #     #     break
    #     truth = mts.Multiset(truth)
    #     pred = np.array(pred)
    #     pred_p = pred[np.where(pred< NUM_OF_SENSITIVE)]
    #     # print(len(pred_p))
    #     if len(pred_p) > 0:
    #         # print("truth:{}, pred:{}, predp: {}".format(truth, pred, pred_p))
    #         pred_p = mts.Multiset(pred_p)
    #         tp += len(truth.intersection(pred_p))
    #         fp += len(pred_p-truth)
    #         # print("tp:{} fp:{}".format(tp,fp))

    # print("{} {} {} {} {}".format(tp,0,fp, p, n))

