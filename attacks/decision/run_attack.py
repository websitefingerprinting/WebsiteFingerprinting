from subprocess import call
from os.path import join
import argparse
import logging
import sys
import const as ct
import os

logger = logging.getLogger('decision')

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
    parser.add_argument('-num',
                        default = None,
                        metavar='<num of the traces in a l-trace>',
                        help='..')     
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
    trainfeaturepath = join(ct.featuredir,trainname+'.npy')
    testfeaturepath = join(ct.featuredir, testname+'.npy')
    modelpath = join(ct.modeldir,trainname+'.pkl')


    if os.path.exists(trainfeaturepath):
        logger.debug("skip train set extraction")
    else:
        logger.debug(call("python3 extract.py "+args.train, shell = True))
    if os.path.exists(testfeaturepath):
        logger.debug("skip test set extraction")
    else:
        logger.debug(call("python3 extract.py "+args.test +" -num "+ args.num, shell = True))


    if os.path.exists(modelpath):
        logger.debug("skip train model")
    else:
        logger.debug(call("python3 train.py " +trainfeaturepath, shell = True))

    logger.info(call("python3 evaluate.py "+testfeaturepath + " -m "+modelpath, shell = True))

