import logging
import argparse
import sys
from os.path import join
from os import makedirs
import os
import numpy as np
import constants as ct
import pandas as pd
import multiprocessing as mp
import time

logger = logging.getLogger('Split')
def parse_arguments():

    parser = argparse.ArgumentParser(description='Split merged trace.')

    parser.add_argument('p',
                        metavar='<merged trace path path>',
                        help='Path to the directory of the merged traces')
    parser.add_argument('-split',
                        metavar='<splitfile path>',
                        default= None,
                        help='empty: for one trace otherwise, normal')
    parser.add_argument('-list',
                        metavar='<listfile path>',
                        default= None,
                        help='Path to the file record the name of each merged trace')        
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
    
def readsplits(splitfile):
    '''input: a file: odd line true split; even line file name'''
    with open(splitfile,'r') as f:
        '''first row is comment'''
        tmp = f.readlines()[1:]
        splits_tmp = pd.Series(tmp[0::2])
        splits = splits_tmp.str.slice(0,-1).str.split('\t',expand = True).astype(int)     
    return np.array(splits)


def readfilename(fname):
    '''read file names in a merged trace'''
    with open(fname,'r') as f:
        tmp = f.readlines()
        filelist = pd.Series(tmp).str.slice(0,-2).str.split('\t',expand = True)
        for j in filelist.columns:
            tmp = filelist[j].str.split('/',expand = True)
            filelist[j] = tmp.iloc[:,-1]
    return np.array(filelist)

def readtrace(fname):
    with open(fname, 'r') as f:
        tmp = f.readlines()
        trace = pd.Series(tmp).str.slice(0,-1).str.split('\t',expand = True).astype(float)
        trace.columns = ['timestamp','direction']
        trace.iloc[:,1] /= abs(trace.iloc[:,1])
    return trace 



def makesplitdir(fpath):
    if not os.path.exists(fpath):
        makedirs(fpath)
    return fpath

def dump(trace, fname):
    with open(fname,'w') as f:
        for i in range(len(trace)):
            f.write('{}\t{}\n'.format(trace.iloc[i,0],int(trace.iloc[i,1])))
    
def parallel(filelist, spilts, path, n_jobs = 10):
    cnts = range(len(splits))
    paths = [path]*len(splits)
    param_dict = zip(cnts,filelist,splits,paths)
    pool = mp.Pool(n_jobs)
    pool.map(cut, param_dict)

def cut(params):
    cnt, ff, s, p = params[0], params[1], params[2],params[3]
    fHeadDir = join(outputdir,'head',str(cnt))
    fOtherDir = join(outputdir, 'other',str(cnt))
    fHeadDir = makesplitdir(fHeadDir)
    fOtherDir = makesplitdir(fOtherDir)


    # logger.info('Processing {}.merge'.format(cnt))
    fname = join(p, str(cnt)+'.merge')
    trace = readtrace(fname)
    
    precut = 0
    for i,cut in enumerate(s):
        # print("precut = {}, cut = {}".format(precut, cut))
        trace1 = trace[precut:cut].copy()
        trace1.timestamp = trace1.timestamp - trace1.iloc[0,0]
        precut = cut
#            trace2 = trace[cut:].copy()
#            trace2.timestamp = trace2.timestamp - trace2.iloc[0,0]
#            trace = trace2
        label = ff[i]
        if i == 0:
            dump(trace1, join(fHeadDir, label))
        else:
            dump(trace1, join(fOtherDir, label))
    # print("precut = {}, cut = {}".format(precut, -1))
    trace1 = trace[precut:].copy()
    trace1.timestamp = trace1.timestamp - trace1.iloc[0,0]
    dump(trace1, join(fOtherDir, ff[i+1] ))    

# def init_directories(path):
#     output_dir = path[:-1]+'-clean'
#     logger.info("Creating output directory: %s" % output_dir)

#     # make the output directory
#     if not os.path.isdir(output_dir):
#         os.mkdir(output_dir)
#     return output_dir

def single_cut(params):
    fHeadDir,label, p, cnt = params[0], params[1], params[2], params[3]
    # logger.info('Processing {}.merge'.format(cnt))
    filepath = os.path.join(fHeadDir, str(cnt))
    filepath = makesplitdir(filepath)
    fname = join(p, str(cnt)+'.merge')
    trace = readtrace(fname)
    dump(trace, join(filepath, label[0]))   

def parallel2(outputdir, filelist, p, n_jobs = 20):
    fHeadDir = join(outputdir,'head')
    fHeadDirs =[fHeadDir]*len(filelist)
    cnts = range(len(filelist))
    paths = [p]*len(filelist)
    param_dict = zip(fHeadDirs ,filelist,paths,cnts)
    pool = mp.Pool(n_jobs)
    pool.map(single_cut, param_dict)     

if __name__ == '__main__':
    args = parse_arguments()

    if args.split == "empty":
        '''basically this is when there is only one trace in a merged trace'''
        fpath = args.p.split('/')[-2]
        fpath = join(ct.outputdir, fpath)
        outputdir = makesplitdir(fpath)
        filelistpath = join(args.p,"list") if args.list == None else args.list
        filelist = readfilename(filelistpath)
        parallel2(outputdir, filelist, args.p)

    else:
        splitfile = join(args.p, "splitresult.txt") if args.split == None else args.split
        filelistpath = join(args.p,"list") if args.list == None else args.list
        filelist = readfilename(filelistpath)
        splits = readsplits(splitfile)
        
        fpath = args.p.split('/')[-2]
        fpath = join(ct.outputdir, fpath)
        outputdir = makesplitdir(fpath)
        t = time.time()
        parallel(filelist, splits, args.p,30)
        logger.info("Total processing time: {:.4f}s".format(time.time()-t))

    #     cnt = -1
    #     for ff, s in zip(filelist,splits):
    #         cnt +=1
    #         fdir = join(outputdir, str(cnt))
    #         fdir = makesplitdir(fdir)
    #         # print(fdir)
    # #        if cnt >= 1:
    # #            break
    # #        cnt += 1
    # #        if cnt <934 :
    # #            continue
    # #        if cnt >9:
    # #            break
    # #        print(t,s)
    # #        if s[0] != s[1]:
    # #            print(s)
    # #            cnt += 1
    # #            continue
    #         logger.info('Processing {}.merge'.format(cnt))
    #         fname = join(args.p, str(cnt)+'.merge')
    #         trace = readtrace(fname)
            
    #         precut = 0
    #         for i,cut in enumerate(s):
    #             # print("precut = {}, cut = {}".format(precut, cut))
    #             trace1 = trace[precut:cut].copy()
    #             trace1.timestamp = trace1.timestamp - trace1.iloc[0,0]
    #             precut = cut
    # #            trace2 = trace[cut:].copy()
    # #            trace2.timestamp = trace2.timestamp - trace2.iloc[0,0]
    # #            trace = trace2
    #             label = ff[i]
    #             dump(trace1, join(fdir, label))
    #         # print("precut = {}, cut = {}".format(precut, -1))
    #         dump(trace[precut:], join(fdir, ff[i+1] ))
               
            
        
        
