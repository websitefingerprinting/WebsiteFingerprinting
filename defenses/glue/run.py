from subprocess import call
import subprocess
from os.path import join
import argparse
import logging
import sys
import constants as ct
import os

logger = logging.getLogger('Glue-script')

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

    parser = argparse.ArgumentParser(description='Mergepad')

    parser.add_argument('mode',
                        metavar='<st, se2, se11>',
                        default = 'se11',
                        help='This script helps to generate dataset')

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



# args = parse_arguments()
# if args.mode == 'st2':
#     logger.info(subprocess.call("python3 main-base-rate.py ../../data/tor2-5-1/ -n 4000 -m 2 -b 1 -noise True -mode fix",shell = True))
# elif args.mode == 'st11':
#     #do not use it
#     logger.info(subprocess.call("python3 main-base-rate.py ../../data/tor2-5-1/ -n 4000 -m 2 -b 10 -noise True -mode fix",shell = True))
# elif args.mode == "se2":
#     logger.info(subprocess.call("python3 main-base-rate.py ../../data/tor2-5-4/ -n 1000 -m 2 -b 1 -noise True -mode fix",shell = True))
# elif args.mode == "se11":
#     logger.info(subprocess.call("python3 main-base-rate.py ../../data/tor2-5-4/ -n 1000 -m 11 -b 10 -noise True -mode fix",shell = True))
# else:
#     logger.error("wrong mode")

for m in range(2,17):
    n = 9900 // m 
    # print("m :{}, n: {}".format(m, n))
    subprocess.call("python3 main-base-rate.py ../../data/evaluation/ -n "+ str(n)+" -m "+str(m)+ " -b 10 -noise True -mode fix", shell = True)


