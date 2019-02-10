#normalize trace pkd direction to be -1 and 1#
import pandas as pd 
import argparse
import logging
import os
import numpy as np
import multiprocessing as mp
import glob 
logger = logging.getLogger('norm')

def config_logger(args):
    # Set file
    log_file = sys.stdout
    if args.log != 'stdout':
        log_file = open(args.log, 'w')
    ch = logging.StreamHandler(log_file)

    # Set logging format
    ch.setFormatter(logging.Formatter(ct.LOG_FORMAT))
    logger.addHandler(ch)

    # Set level format
    logger.setLevel(logging.INFO)

def parse_arguments():
    parser = argparse.ArgumentParser(description='It simulates adaptive padding on a set of web traffic traces.')

    parser.add_argument('p',
                        metavar='<traces path>',
                        help='Path to the directory with the traffic traces to be simulated.')

    parser.add_argument('--log',
                        type=str,
                        dest="log",
                        metavar='<log path>',
                        default='stdout',
                        help='path to the log file. It will print to stdout by default.')

    args = parser.parse_args()
    return args

def load_trace(fdir):
    with open(fdir,'r') as f:
        tmp = f.readlines()
    t = pd.Series(tmp).str.slice(0,-1).str.split('\t',expand = True).astype('float')
    return np.array(t)

def dump(trace, fdir):
    with open(fdir, 'w') as fo:
        for packet in trace:
            fo.write("{}".format(packet[0]) +'\t' + "{}".format(int(packet[1]))\
                + '\n')
def normalize(fdir):
	global output_dir
	trace = load_trace(fdir)
	trace[:,1] /= abs(trace[:,1])
	
	name = fdir.split('/')[-1]
	addr = os.path.join(output_dir, name)	
	print("Dumped to {}".format(addr))
	dump(trace, addr)
	

def parallel(flist, n_jobs = 20):
    pool = mp.Pool(n_jobs)
    pool.map(normalize, flist)


if __name__ == '__main__':
	global output_dir 
	args = parse_arguments()
	flist  = glob.glob(os.path.join(args.p,'*'))
	folder = args.p[:-1] + '_norm'
	if not os.path.exists(folder):
		os.makedirs(folder)
	output_dir = folder
	parallel(flist)

