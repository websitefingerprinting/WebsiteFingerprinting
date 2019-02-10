import logging
import argparse
import pandas as pd
import numpy as np
import glob
import os
import sys
import multiprocessing as mp

logger = logging.getLogger('ovhd')
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
                        default = '.merge',
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

def calc_single_ovhd(t):
    logger.info('Processing file {}'.format(t))
    with open(t,'r') as f:
        trace = pd.Series(f.readlines()).str.slice(0,-1)
        trace = trace.str.split('\t',expand = True)
        size = trace[1].astype('float')
    RPOV = size.where(abs(size) == 888).count()
    MPOV = size.where(abs(size) == 999).count()
    TOTAL = size.count() - RPOV - MPOV
    return (RPOV, MPOV, TOTAL)
def parallel(flist, n_jobs = 25):
    pool = mp.Pool(n_jobs)
    ovhds  = pool.map(calc_single_ovhd, flist)    
    return ovhds

if __name__ == '__main__':
    args = parse_arguments()
    flist = glob.glob(os.path.join(args.dir,'*'+args.format))
    # ovhds = []
    # for f in flist:
    #     overhead = calc_single_ovhd(f)
    #     ovhds.append(overhead)
    ovhds = parallel(flist)
    ovhds = list(zip(*ovhds))
    rpovhds = np.array(ovhds[0])
    mpovhds = np.array(ovhds[1])
    total = np.array(ovhds[2])
    rpovhds = 1.0*rpovhds.sum()/total.sum()
    mpovhds = 1.0*mpovhds.sum()/total.sum()
    logger.info('total packets:           {:.4f} +- {:.4f}'.format(total.mean(), total.std()))
    logger.info('Merge Padding overhead:  {:.4f} '.format(mpovhds))
    logger.info('Random Padding overhead: {:.4f} '.format(rpovhds))
    # logger.info('total packets:           {:.4f} +- {:.4f}'.format(total.mean(), total.std()))
    # logger.info('Merge Padding overhead:  {:.4f} +- {:.4f}'.format(mpovhds.mean(), mpovhds.std()))
    # logger.info('Random Padding overhead: {:.4f} +- {:.4f}'.format(rpovhds.mean(), rpovhds.std()))
    





