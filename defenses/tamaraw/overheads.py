import numpy as np
import constants as ct 
import argparse
from os.path import join
import logging
import sys

logger = logging.getLogger('tamaraw')

'''params'''
MON_SITE_NUM = 100
MON_INST_NUM = 90
UNMON_SITE_NUM = 9000

def config_logger():
    # Set file
    log_file = sys.stdout
    ch = logging.StreamHandler(log_file)

    # Set logging format
    ch.setFormatter(logging.Formatter(ct.LOG_FORMAT))
    logger.addHandler(ch)

    # Set level format
    logger.setLevel(logging.INFO)

def parse_arguments():
    # Read configuration file
    # conf_parser = configparser.RawConfigParser()
    # conf_parser.read(ct.CONFIG_FILE)

    parser = argparse.ArgumentParser(description='It simulates tamaraw on a set of web traffic traces.')

    parser.add_argument('original_dir',
                        metavar='<traces path>',
                        help='Path to the directory with the traffic traces to be simulated.')
    parser.add_argument('defenced_dir',metavar='<traces path>',
                        help='Path to the directory with the defenced traces.')
   

    args = parser.parse_args()

    return args

def latency(trace):
    return trace[-1][0] - trace[0][0]

def totbytes(trace):
    return sum([abs(p[1]) for p in trace]) *1.0


def bandwidth(trace):
    return totbytes(trace)/latency(trace)



if __name__ == '__main__':
    latency_ratio= []
    size_ratio = []
    bandwidth_ratio = []
    args = parse_arguments()
    config_logger()
    # original = join(ct.BASE_DIR, args.original)
    # defenced = join(ct.RESULTS_DIR, args.defenced)

    for i in range(MON_SITE_NUM):
        for j in range(MON_INST_NUM):
            fname = str(i) +'-' + str(j)
            logger.info('Caculating %s'%fname)
            original = []
            defenced = []
            with open(join(args.original_dir, fname),'r') as f:
                lines = f.readlines()
                starttime = float(lines[0].split("\t")[0])
                for x in lines:
                    x = x.split("\t")
                    original.append([float(x[0]) - starttime, int(x[1])])       
            with open(join(args.defenced_dir, fname),'r') as f:
                lines = f.readlines()
                starttime = float(lines[0].split("\t")[0])
                for x in lines:
                    x = x.split("\t")
                    defenced.append([float(x[0]) - starttime, int(x[1])]) 
            old_latency, new_latency = latency(original), latency(defenced) 
            latency_ratio.append(new_latency/old_latency*1.0)
            old_size, new_size = totbytes(original), totbytes(defenced)
            size_ratio.append(new_size/old_size)
            bandwidth_ratio.append((new_size/new_latency)/(old_size/old_latency))

    for i in range(UNMON_SITE_NUM):
        fname = str(i)
        logger.info('Caculating %s'%fname)
        original = []
        defenced = []
        with open(join(args.original_dir, fname),'r') as f:
            lines = f.readlines()
            starttime = float(lines[0].split("\t")[0])
            for x in lines:
                x = x.split("\t")
                original.append([float(x[0]) - starttime, int(x[1])])       
        with open(join(args.defenced_dir, fname),'r') as f:
            lines = f.readlines()
            starttime = float(lines[0].split("\t")[0])
            for x in lines:
                x = x.split("\t")
                defenced.append([float(x[0]) - starttime, int(x[1])]) 
            old_latency, new_latency = latency(original), latency(defenced) 
            latency_ratio.append(new_latency/old_latency*1.0)
            old_size, new_size = totbytes(original), totbytes(defenced)
            size_ratio.append(new_size/old_size)
            bandwidth_ratio.append((new_size/new_latency)/(old_size/old_latency))


    print("Latency overhead: %.4f, size overhead: %.4f, bandwidth overhead:%.4f"%(np.median(latency_ratio),np.median(size_ratio),np.median(bandwidth_ratio)))