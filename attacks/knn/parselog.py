import re
import argparse
from collections import defaultdict
import logging
from os.path import join, abspath, dirname, pardir
import os
from pprint import pprint
# BASE_DIR = join(abspath(join(dirname(__file__), pardir)),'randomknn2/randomresults')
pattern = re.compile(r"\s*(?P<tp>\d+)\s+(?P<wp>\d+)\s+(?P<fp>\d+)\s+900\s+900\s*")
dic = defaultdict(list)

def init_logger():
    logger = logging.getLogger('knn-parser')
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # create formatter
    LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
    formatter = logging.Formatter(LOG_FORMAT)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger

def parse_arguments():

    parser = argparse.ArgumentParser(description='parser of log file.')

    parser.add_argument('dir',
                        metavar='<log path>',
                        help='Path to the directory of log')    

    parser.add_argument('--log',
                        type=str,
                        dest="log",
                        metavar='<log path>',
                        default='stdout',
                        help='path to the log file. It will print to stdout by default.')
    # Parse arguments
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_arguments()
    logger = init_logger()
    with open(args.dir,'r') as f:
        lines = f.readlines()
    cnt = 0
    for line in lines:
        m = re.search(pattern, line)
        if m: 
            cnt += 1
            tp,wp,fp = int(m.group('tp')) ,int(m.group('wp')) ,int(m.group('fp')) 
            dic["tp"].append(tp)
            dic["wp"].append(wp)
            dic["fp"].append(fp)
        else:
            logging.info("No match")
    if cnt != 10:
        raise Error('Bad parser!')
    print(sum(dic["tp"]), sum(dic["wp"]), sum(dic["fp"]), 9000 , 9000)