
import sys
import os
from os import mkdir
from os.path import join, isdir
from time import strftime
import numpy as np
import glob
import pandas as pd
import configparser
import argparse
import logging

logger = logging.getLogger('Getsplit')

#around x- neighbor, x+ neighbor  won't have another split
global neighbor 
neighbor = 40

def parse_arguments():

    parser = argparse.ArgumentParser(description='Get split in a score file.')

    parser.add_argument('p',
                        metavar='<trace path>',
                        help='score file path.') 
    parser.add_argument('-k',
                        metavar='<dir: num of pred splits>',
                        default = None,
                        help='num of splits') 
    parser.add_argument('-d',
                        metavar='<relaxed accuracy>',
                        default = 0,
                        type = int,
                        help='how far can we consider a predict as correct')   
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
    LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
    ch.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(ch)

    # Set level format
    logger.setLevel(logging.INFO)

def GetSplit(scorefile, num_of_splits = None):
    global neighbor
    s = []
    dic = np.load(scorefile).item()
    truesplits = dic['truesplits']
    scores = dic['score'][:,0]
    locations = dic['location']
    
    n = len(truesplits) if num_of_splits == None else num_of_splits
    
    scores  = scores[::-1]
    locations = locations[::-1]
    for i in range(n):
#        logger.info('Iteration: {}'.format(i))
        argmax = np.argmax(scores)
        # logger.info('Find a split at index {}, pkt no. {}, maxscore {}'.format(argmax, int(locations[argmax]),scores[argmax]))
        scores[argmax] =  - np.inf
        for ind in range(argmax-1,-1,-1):
            '''larger neighbor'''
            if locations[ind]  < neighbor + locations[argmax]:
                scores[ind] = - np.inf
#                logger.info("Find neighbor {}, because its pkt no. is {}".format(ind, int(scores[ind][0])))
            else:
                break
        for ind in range(argmax+1, len(scores)):
            '''smaller neighbor'''
            if locations[ind] > locations[argmax] - neighbor:
                scores[ind] = -np.inf
#                logger.info("Find neighbor {}, because its pkt no. is {}".format(ind, int(scores[ind][0])))
        
            else:
                break
        s.append(int(locations[argmax]))
    return s, truesplits
    
if __name__ == '__main__':
    args = parse_arguments()
    logger.debug(args)
    scoresfile = glob.glob(join(args.p,'*-score.npy'))
    scoresfile.sort(key=lambda d:int(d.split('/')[-1].split('-')[0]))
    
    if args.k != None:
        total_num_of_splits = np.load(args.k).item()['k']

    acc = 0
    total = [0,0] #left pre, right truth
    
    with open(join(args.p,'splitresult.txt'),'w') as f:
        f.write('First row is prediction, second is truesplit.\n')
        for i,scorefile in enumerate(scoresfile):
            num_of_splits = None if args.k == None else total_num_of_splits[i]
            preds ,truesplits = GetSplit(scorefile, num_of_splits)
            # print("processing {}".format(scorefile))
            sorted_preds = sorted(preds)
            # print("true: {}, \n pred:{}".format(truesplits,sorted_preds))
            [f.write(str(p)+'\t') for p in sorted_preds[:-1]]
            f.write(str(sorted_preds[-1])+'\n')
            [f.write(str(p)+'\t') for p in truesplits[:-1]]
            f.write(str(truesplits[-1])+'\n')             
            #count accuracy
            total[0] += len(preds)
            total[1] += len(truesplits)
            # if len(preds) != 10 or len(truesplits) != 10:
                # print("!!! pred: {}, truesplits:{}, scorefile:{} ".format(len(preds),len(truesplits),scorefile))
            for pred in preds:
                if len(truesplits) == 0:
                    break
                closearg, close = min(enumerate(truesplits), key=lambda x:abs(x[1]-pred))
                # logger.info("Closest point for {} is {}".format(pred, close))
                if abs(close-pred) <= args.d :
                    acc += 1
#                    logger.info('Closest point for {} is {},index {}'.format(pred, close, closearg))
#                    logger.info(truesplits)
                    truesplits = np.delete(truesplits, closearg)


            


        accr = acc*1.0/max(total)
        logger.info("Acc: {}/max(pred:{}, true:{})= {:.4f}".format(acc,total[0], total[1], accr))
    