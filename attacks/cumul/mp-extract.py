import numpy as np
import sys
import os
from os import mkdir, listdir
from os.path import join, isdir, dirname
from time import strftime

import constants as ct

import configparser
import argparse
import logging
import glob
import multiprocessing as mp

logger = logging.getLogger('cumul')

def read_conf(file):
    cf = configparser.ConfigParser()
    cf.read(file)  
    return dict(cf['default'])


def parse_arguments():

    parser = argparse.ArgumentParser(description='It simulates adaptive padding on a set of web traffic traces.')

    parser.add_argument('t',
                        metavar='<traces path>',
                        help='Path to the directory with the traffic traces to be simulated.')

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



def parse(fpath):
    '''Parse a file assuming Tao's format.'''
    t = []
    for line in open(fpath):
        try:    
            timestamp, length = line.strip().split(ct.TRACE_SEP)
            t.append(-int(length))
        except ValueError:
            logger.warn("Could not split line: %s in %s", line, fpath)      
            continue    
    return t

def extract(sinste):
    #sinste: list of packet sizes

    #first 4 features

    insize = 0
    outsize = 0
    inpacket = 0
    outpacket = 0

    for i in range(0, len(sinste)):
        if sinste[i] > 0:
            outsize += sinste[i]
            outpacket += 1
        else:
            insize += abs(sinste[i])
            inpacket += 1
    features = [insize, outsize, inpacket, outpacket]

    #100 interpolants
    
    n = 100 #number of linear interpolants

    x = 0 #sum of packet sizes
    y = 0 #sum of absolute packet sizes
    graph = []
    
    for si in range(0, len(sinste)):
        x += abs(sinste[si])
        y += sinste[si]
        graph.append([x, y])

    #derive interpolants
    max_x = graph[-1][0] 
    gap = float(max_x)/n
    cur_x = 0
    cur_y = 0
    graph_ptr = 0

    for i in range(0, n):
        #take linear line between cur_x and cur_x + gap
        next_x = cur_x + gap
        while (graph[graph_ptr][0] < next_x):
            graph_ptr += 1
            if (graph_ptr >= len(graph) - 1):
                graph_ptr = len(graph) - 1
                #wouldn't be necessary if floats were floats
                break
##        print "graph_ptr=", graph_ptr
        next_pt_y = graph[graph_ptr][1] #not next_y 
        next_pt_x = graph[graph_ptr][0]
        cur_pt_y = graph[graph_ptr-1][1]
        cur_pt_x = graph[graph_ptr-1][0]
##        print "lines are", cur_pt_x, cur_pt_y, next_pt_x, next_pt_y

        if (next_pt_x - cur_pt_x != 0):
            slope = (next_pt_y - cur_pt_y)/(next_pt_x - cur_pt_x)
        else:
            slope = 1000
        next_y = slope * (next_x - cur_pt_x) + cur_pt_y

##        print "xy are", cur_x, cur_y, next_x, next_y, max_x
        interpolant = (next_y - cur_y)/(next_x - cur_x)
        # features.append(interpolant)
        features.append(next_y)
        cur_x = next_x
        cur_y = next_y

    return features
def parallel(flist,n_jobs = 20): 
    pool = mp.Pool(n_jobs)
    data_dict = pool.map(extractfeature, flist)
    return data_dict


def extractfeature(f):
    fname = f.split('/')[-1].split(".")[0]
    # logger.info('Processing %s...'%f)
    try:
        features = extract(parse(f))
    except:
        print("nonono")
        print(f)
    if '-' in fname:
        label = int(fname.split('-')[0])
    else:
        label = int(MON_SITE_NUM)
    
    return (features,label)

if __name__ == '__main__':
	# parser config and arguments
    args = parse_arguments()
    # logger.info("Arguments: %s" % (args))

    cf = read_conf(ct.confdir)
    MON_SITE_NUM = int(cf['monitored_site_num'])
    MON_INST_NUM = int(cf['monitored_inst_num'])
    if cf['open_world'] == '1':
        UNMON_SITE_NUM = int(cf['unmonitored_site_num'])
        OPEN_WORLD = 1
    else:
        OPEN_WORLD = 0

    # logger.info('Extracting features...')
    
    
    headfpath = os.path.join(args.t, 'head/*/*')
    otherfpath = os.path.join(args.t, 'other/*/*')
    headflist = glob.glob(headfpath)
    otherflist = glob.glob(otherfpath)

    #extract for head pages
    data_dict = {'feature':[],'label':[]}
    raw_data_dict = parallel(headflist,n_jobs = 20)
    data_dict['feature'], data_dict['label'] = zip(*raw_data_dict)
    outputdir = ct.outputdir+args.t.split('/')[-2]+'-head'
    np.save(outputdir,data_dict) 
    # logger.info('Save to %s.npy'%outputdir)

    #extract for other pages
    if len(otherflist) > 1:
        data_dict = {'feature':[],'label':[]}
        raw_data_dict = parallel(otherflist,n_jobs = 20)
        data_dict['feature'], data_dict['label'] = zip(*raw_data_dict)
        outputdir = ct.outputdir+args.t.split('/')[-2]+'-other'
        np.save(outputdir,data_dict) 
        # logger.info('Save to %s.npy'%outputdir)