import random
import constants as ct

import sys
import os
import multiprocessing as mp
import subprocess
from os import mkdir
from os.path import join, isdir
from time import strftime
import numpy as np
import glob
import pandas as pd

import configparser
import argparse
import logging
import datetime

logger = logging.getLogger('mergepad')

# random.seed(1123)
# np.random.seed(1123)

OPEN_WORLD = 1
MON_SITE_NUM = 100
MON_INST_NUM = 100
UNMON_SITE_NUM = 10000


# BaseRate = 10


# '''used to save single traces'''
# global list_names

def load_trace(fname, t = 999, noise = False):
    '''load a trace from fpath/fname up to t time.'''
    '''return trace and its name: cls-inst'''
    label = '*' if noise else fname

        
    pkts = []
    with open(fname, 'r') as f:
        for line in f:
            try:    
                timestamp, length = line.strip().split(ct.TRACE_SEP)
                pkts.append([float(timestamp), int(length)])
                if float(timestamp) >= t+0.5:
                    break
            except ValueError:
                logger.warn("Could not split line: %s in %s", line, fname)
        return label, np.array(pkts)
        

def weibull(k = 0.75):
    return np.random.weibull(0.75)
def uniform():
    return np.random.uniform(1,10)

def dump(trace, fpath):
    '''Write trace packet into file `fpath`.'''
    with open(fpath, 'w') as fo:
        for packet in trace:
            fo.write("{}".format(packet[0]) +'\t' + "{}".format(int(packet[1])) + ct.NL)


 

def merge(this, other, start, cnt = 1):
    '''t = 999, pad all pkts, otherwise pad up to t seconds'''
    other[:,0] -= other[0][0]
    other[:,0] += start
    other[:,1] *= cnt
    if this is None:
        this = other
    else:
        this = np.concatenate((this,other), axis = 0)
    return this
    

def est_iat(trace):
    trace_1 = np.concatenate((trace[1:], trace[0:1]),axis=0)
    itas = trace_1[:-1,0] - trace[:-1,0]
    return np.random.uniform(np.percentile(itas,20), np.percentile(itas,80))


def choose_site():
    # global list_names
    # list_names = glob.glob(join(args.traces_path,'*-*'))
    # with open("goodfile.txt","r") as f:
    with open("nonsens.txt","r") as f:
        list_names = list(pd.Series(f.readlines()).str.slice(0,-1))
    noise_site = np.random.choice(list_names,1)[0]
    return noise_site
        
def MergePad2(output_dir, outputname ,noise, mergelist = None, waiting_time = 10):
    '''mergelist is a list of file names'''
    '''write in 2 files: the merged trace; the merged trace's name'''
    labels = ""
    this = None
    start = 0.0 
    
    for cnt,fname in enumerate(mergelist):
        label, trace = load_trace(fname)
        labels += label + '\t'
        this = merge(this, trace, start, cnt = cnt + 1)
        start = this[-1][0]
        '''pad noise or not'''
        if noise:
            noise_fname = choose_site()
            if cnt == len(mergelist)-1:
                ###This is a param in mergepadding###
                t = np.random.uniform(waiting_time, waiting_time+5)  
            else:
                t = uniform()
            small_time = est_iat(trace)
            logger.debug("Delta t is %.5f seconds"%(small_time))
            _, noise_site = load_trace(noise_fname, max(t - small_time, 0),True)
            this = merge(this, noise_site,start+small_time, cnt = 999)
            # logger.info("Dwell time is %.2f seconds"%(t))
            start = start + t
        else:
            t = uniform()
            start = start + t

    if noise:
        this = this[this[:,0].argsort(kind = "mergesort")]
    dump(this, join(output_dir, outputname+'.merge'))
    logger.debug("Merged trace is dumpped to %s.merge"%outputname)            
    return labels     

    
# def MergePad(output_dir, outputname ,noise, mergelist = None, waiting_time = 10):
#     '''mergelist is a list of file names'''
#     '''write in 2 files: the merged trace; the merged trace's name'''
#     labels = ""
#     this = None
#     start = 0.0 
    
#     for cnt,fname in enumerate(mergelist):
#         label, trace = load_trace(fname)
#         labels += label + '\t'
#         this = merge(this, trace, start, cnt = cnt + 1)
#         start = this[-1][0]
#         '''pad noise or not'''
#         if noise:
#             noise_fname = choose_site()
#             if cnt == len(mergelist)-1:
#                 ###This is a param in mergepadding###
#                 t = waiting_time  
#             else:
#                 t = uniform()
#                 # t = weibull()
#                 # while t < 0.5:
#                 #     t = weibull()
#             small_time = np.random.uniform(0,0.05)
#             _, noise_site = load_trace(noise_fname,min(t,waiting_time)-small_time,True)
#             this = merge(this, noise_site,start+small_time, cnt = 999)
#             logger.debug("Dwell time is %.2f seconds"%(t))
#             start = start + t
#         else:
#             t = uniform()
#             # t = weibull()
#             # while t < 0.5:
#             #     t = weibull()
#             logger.debug("Dwell time is %.2f seconds"%(t))
#             start = start + t
#     dump(this, join(output_dir, outputname+'.merge'))
#     logger.debug("Merged trace is dumpped to %s.merge"%outputname)            
#     return labels     

    
    
def init_directories():
    # Create a results dir if it doesn't exist yet
    if not isdir(ct.RESULTS_DIR):
        mkdir(ct.RESULTS_DIR)

    # Define output directory
    timestamp = strftime('%m%d_%H%M')
    output_dir = join(ct.RESULTS_DIR, 'mergepad_'+timestamp)
    while os.path.exists(output_dir):
        timestamp = strftime('%m%d_%H%M')
        output_dir = join(ct.RESULTS_DIR, 'mergepad_'+timestamp)

    logger.info("Creating output directory: %s" % output_dir)

    # make the output directory
    mkdir(output_dir)
    return output_dir

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
    # Read configuration file
    conf_parser = configparser.RawConfigParser()
    conf_parser.read(ct.CONFIG_FILE)

    parser = argparse.ArgumentParser(description='It simulates adaptive padding on a set of web traffic traces.')

    parser.add_argument('traces_path',
                        metavar='<traces path>',
                        help='Path to the directory with the traffic traces to be simulated.')
    

    parser.add_argument('-c', '--config',
                        dest="section",
                        metavar='<config name>',
                        help="Adaptive padding configuration.",
                        choices= conf_parser.sections(),
                        default="default")

    parser.add_argument('-noise',
                        type=str,
                        metavar='<pad noise>',
                        default= 'False',
                        help='Simulate whether pad noise or not')

    parser.add_argument('-n',
                        type=int,
                        metavar='<Instance Number>',
                        help='generate n instances')
    parser.add_argument('-m',
                        type=int,
                        metavar='<Merged Number>',
                        help='generate n instances of m merged traces')                            
    parser.add_argument('-b',
                        type=int,
                        metavar='<baserate>',
                        default = 10,
                        help='baserate') 
    parser.add_argument('-mode',
                        type=str,
                        metavar='<mode>',
                        default = 'fix',
                        help='To generate random-length or fixed-length trace')                          
    parser.add_argument('--log',
                        type=str,
                        dest="log",
                        metavar='<log path>',
                        default='stdout',
                        help='path to the log file. It will print to stdout by default.')

    args = parser.parse_args()
    config = dict(conf_parser._sections[args.section])
    config_logger(args)

    return args,config

 

def CreateMergedTrace(traces_path, list_names, N, M, BaseRate):
    '''generate length-N merged trace'''
    '''with prob baserate/(baserate+1) a nonsensitive trace is chosen'''
    '''with prob 1/(baserate+1) a sensitive trace is chosen'''
    list_sensitive = glob.glob(join(traces_path, '*-*'))
    list_nonsensitive = list(set(list_names) - set(list_sensitive))
    
    s1 = len(list_sensitive)
    s2 = len(list_nonsensitive)
    
    mergedTrace = np.array([])
    for i in range(N):
        mergedTrace = np.append(mergedTrace,np.random.choice(list_sensitive+list_nonsensitive, M, replace = False,\
                                  p = [1.0/(s1*(BaseRate+1))]*s1 + [BaseRate /(s2*(BaseRate+1))]*s2))
    mergedTrace = mergedTrace.reshape((N,M))

    return mergedTrace


def CreateRandomMergedTrace(traces_path, list_names, N, M,BaseRate):
    '''generate random-length merged trace'''
    '''with prob baserate/(baserate+1) a nonsensitive trace is chosen'''
    '''with prob 1/(baserate+1) a sensitive trace is chosen'''
    list_sensitive = glob.glob(join(traces_path, '*-*'))
    list_nonsensitive = list(set(list_names) - set(list_sensitive))
    
    s1 = len(list_sensitive)
    s2 = len(list_nonsensitive)
    
    mergedTrace = []
    nums = np.random.choice(range(2,M+1),N)
    for i,num in enumerate(nums):
        mergedTrace.append(np.random.choice(list_sensitive+list_nonsensitive, num, replace = False,\
                                  p = [1.0/(s1*(BaseRate+1))]*s1 + [BaseRate /(s2*(BaseRate+1))]*s2))
    return mergedTrace, nums


def parallel(output_dir, noise, mergedTrace,n_jobs = 20): 
    cnt = range(len(mergedTrace))
    l = len(cnt)
    param_dict = zip([output_dir]*l, cnt, [noise]*l, mergedTrace)
    pool = mp.Pool(n_jobs)
    l  = pool.map(work, param_dict)
    return l


def work(param):
    np.random.seed(datetime.datetime.now().microsecond)
    output_dir, cnt, noise, T = param[0],param[1], param[2], param[3]
    return MergePad2(output_dir,  str(cnt) , noise, T)

if __name__ == '__main__':
    # global list_names
    # parser config and arguments
    args,config = parse_arguments()
    logger.info("Arguments: %s" % (args))

    
    list_names = glob.glob(join(args.traces_path,'*'))
    if args.mode == 'fix':
        mergedTrace = CreateMergedTrace(args.traces_path, list_names, args.n, args.m,args.b)
    elif args.mode == 'random':
        mergedTrace, nums = CreateRandomMergedTrace(args.traces_path, list_names, args.n, args.m, args.b)
    else:
        logger.error("Wrong mode :{}".format(args.mode))

     #Init run directories
    output_dir = init_directories()
    if args.mode == 'random':
        np.save(join(output_dir,'num.npy'),nums)

    l = parallel(output_dir, eval(args.noise), mergedTrace, 20)
    # l = []
    # cnt = 0
    # for T in mergedTrace:
    #     l.append(MergePad2(output_dir,  str(cnt) , eval(args.noise), T))
    #     cnt += 1
    
    with open(join(output_dir, 'list'),'w') as f:
        [f.write(label+'\n') for label in l]
    print(output_dir)
    
    # subprocess.check_call("python3 overhead.py "+output_dir,shell = True)

