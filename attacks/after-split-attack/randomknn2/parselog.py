import re
import argparse
from collections import defaultdict
import logging
from os.path import join, abspath, dirname, pardir
import os
from pprint import pprint
BASE_DIR = join(abspath(join(dirname(__file__), pardir)),'randomknn2/randomresults')
pattern = re.compile(r"testid:\s*(?P<testid>\d+)\s+guess:\s*(?P<y_pred>-?\d+)\d*")
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
            y_pred = int(m.group('y_pred')) if int(m.group('y_pred')) != -1 else 100
            dic[m.group('testid')].append(y_pred)
        else:
            logging.info("No match")
    tmp = args.dir.split('/')[-1].split('.')[0]
    folder,subfolder = tmp.split('-')[0],tmp.split('-')[1] 
    outputdir = join(BASE_DIR,folder,subfolder)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    for k in dic:
        file = join(outputdir,k+'-predresult.txt')
        with open(file,'w') as f:
            [f.write(str(y)+'\n') for y in dic[k]]

    # pprint(dic)