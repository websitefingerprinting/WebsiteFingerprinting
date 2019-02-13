#To calculate distribution of dummy packets in a trace
import logging
import argparse
import pandas as pd
import numpy as np
import glob
import os
import sys
import multiprocessing as mp
from os.path import join 
from pprint import pprint
logger = logging.getLogger('std')
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

    parser = argparse.ArgumentParser(description='Calculate overhead for a trace folder.')

    parser.add_argument('-p',
                        metavar='<original traces path>',
                        help='Path to the directory with the traffic traces to be simulated.')

    parser.add_argument('-format',
                        metavar='<format>',
                        default = '',
                        help='file format, default: "xx.merge" ')

    parser.add_argument('--log',
                        type=str,
                        dest="log",
                        metavar='<log path>',
                        default='stdout',
                        help='path to the log file. It will print to stdout by default.')

    args = parser.parse_args()
    config_logger(args)

    return args

def calc_single_dist(fdir):
    with open(fdir,'r') as f:
        lines = f.readlines()
    trace = pd.Series(lines).str.slice(0,-1).str.split('\t',expand = True).copy()
    trace = trace.astype("float")
    lasttime = trace.iloc[-1,0]
    trace = trace.values
    totaldummy = trace[np.where(abs(trace[:,1])> 2)]
    quartertrace = trace[np.where(trace[:,0] <= lasttime / 4.0)]
    halftrace = trace[np.where(trace[:,0] <= lasttime/2.0 )]
    quarter = len(np.where(abs(quartertrace[:,1]) > 2) [0]) / len(totaldummy)
    half = len(np.where(abs(halftrace[:,1]) > 2)[0]) /len(totaldummy)
    # print(np.where(abs(quartertrace[:,1]) > 2) )
    # print(len(totaldummy))
    # print(np.where(abs(halftrace[:,1])>2)[0])
    return [quarter, half]



def parallel(flist, n_jobs = 20):
    pool = mp.Pool(n_jobs)
    result  = pool.map(calc_single_dist,flist)    
    return result

if __name__ == '__main__':
    global defended_dir
    args = parse_arguments()
    defended_dir = args.p
    flist = glob.glob(join(defended_dir, "*")) 

    result = parallel(flist)

    quarters ,halfs = list(zip(*result))
    # print(quarters)
    print(np.array(quarters).mean(), np.array(halfs).mean())

    
 
    





