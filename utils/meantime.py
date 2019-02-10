#To calculate the mean time of webpage#
import logging
import argparse
import pandas as pd
import numpy as np
import glob
import os
import sys
import multiprocessing as mp

logger = logging.getLogger('mean')
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

    parser.add_argument('dir',
                        metavar='<traces path>',
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

def calc_single_time(t):
    logger.info('Processing file {}'.format(t))
    with open(t,'r') as f:
        lines = f.readlines()
        start = float(lines[0].split()[0])
        end = float(lines[-1].split()[0])
    return float(end-start)
def parallel(flist, n_jobs = 2):
    pool = mp.Pool(n_jobs)
    times  = pool.map(calc_single_time, flist)    
    return times

if __name__ == '__main__':
    args = parse_arguments()
    flist = glob.glob(os.path.join(args.dir,'*'+args.format))
    # ovhds = []
    # for f in flist:
    #     overhead = calc_single_ovhd(f)
    #     ovhds.append(overhead)
    times = parallel(flist)
    # print(times)
    print("Average time is {:.2f}".format(np.array(times).mean()))
 
    





