from subprocess import call
from os.path import join
import argparse
import logging
import sys
import constants as ct
import os

logger = logging.getLogger('xgboost')

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

    parser = argparse.ArgumentParser(description='XGboost split algorithm.')

    parser.add_argument('-train',
                        metavar='<train set>',
                        help='Train set path')
    parser.add_argument('-test',
                        metavar='<test set>',
                        help='Test set path')
    parser.add_argument('-mode',
                        metavar='<Whether run decision before finding>',
                        default = 'finding',
                        help='decision or finding')
    parser.add_argument('-kdir',
                        metavar='<num of splits>',
                        default = None,
                        help='dir of num of splits')
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
if __name__ == '__main__':
    args = parse_arguments()

    trainname = args.train.split('/')[-2]
    testname = args.test.split('/')[-2]
    trainfeaturepath = join('./features/',trainname+'.npy')
    testfeaturepath = join('./features/', testname+'/')
    modelpath = join('./models/',trainname+'.pkl')
    scorepath = join('./scores/', testname+'/')

    if os.path.exists(trainfeaturepath):
        logger.debug("skip train set extraction")
    else:
        call("python3 extract.py -mode train "+args.train, shell = True)
    call("python3 extract.py -mode test "+args.test, shell = True)


    if os.path.exists(modelpath):
        logger.debug("skip train model")
    else:
        call("python3 main.py -mode train " +trainfeaturepath, shell = True)
    call("python3 main.py -mode test -model "+modelpath +" "+testfeaturepath, shell = True)

    if args.mode == 'finding':
        call("python3 getsplit-base-rate.py "+ scorepath, shell = True)
    elif args.mode == 'decision':
        kdir = args.kdir
        call("python3 getsplit-base-rate.py "+ scorepath +" -k "+ kdir , shell = True)

    else:
        logger.warn("Wrong mode {}!!".format(args.mode))
