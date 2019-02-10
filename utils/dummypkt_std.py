#To calculate the std of dummy packets added
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

    parser.add_argument('-o',
                        metavar='<original traces path>',
                        help='Path to the directory with the traffic traces to be simulated.')

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

def calc_single_std(ind):
    global original_dir, defended_dir
    # logger.info('Processing class {}'.format(ind))
    oflist = glob.glob(join(original_dir, str(ind)+"-*"))
    dflist = glob.glob(join(defended_dir, str(ind)+"-*"))
    dummy_num = []
    for of,df in zip(oflist, dflist):
        with open(of,'r') as f:
            olen = len(f.readlines())
        with open(df,'r') as f:
            dlen = len(f.readlines())   
        dummy_num.append(1.0*(dlen-olen))
    
    return np.array(dummy_num).std()


def parallel(n_jobs = 20):
    pool = mp.Pool(n_jobs)
    inds = np.arange(0,100)
    stds  = pool.map(calc_single_std, inds)    
    return stds

if __name__ == '__main__':
    global original_dir, defended_dir
    args = parse_arguments()
    original_dir = args.o
    defended_dir = args.p
    # ovhds = []
    # for f in flist:
    #     overhead = calc_single_ovhd(f)
    #     ovhds.append(overhead)
    stds = parallel()
    print(pd.Series(stds))
    name = defended_dir.split('/')[-2]+".npy"
    np.save(name, np.array(stds))
    logger.info("Save to {}".format(name))
    # print("Average time is {:.2f}".format(np.array(times).mean()))
 
    





