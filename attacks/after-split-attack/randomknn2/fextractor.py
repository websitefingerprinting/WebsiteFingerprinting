import sys
import subprocess
import numpy
import os
from loaders import *
import glob 
import argparse
import logging


def init_logger():
    logger = logging.getLogger('knn')
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


def extract(times, sizes, features):

    #Transmission size features
    features.append(len(sizes))

    count = 0
    for x in sizes:
        if x > 0:
            count += 1
    features.append(count)
    features.append(len(times)-count)

    features.append(times[-1] - times[0])

    #Unique packet lengths
##    for i in range(-1500, 1501):
##        if i in sizes:
##            features.append(1)
##        else:
##            features.append(0)

    #Transpositions (similar to good distance scheme)
    count = 0
    for i in range(0, len(sizes)):
        if sizes[i] > 0:
            count += 1
            features.append(i)
        if count == 500:
            break
    for i in range(count, 500):
        features.append("X")
        
    count = 0
    prevloc = 0
    for i in range(0, len(sizes)):
        if sizes[i] > 0:
            count += 1
            features.append(i - prevloc)
            prevloc = i
        if count == 500:
            break
    for i in range(count, 500):
        features.append("X")


    #Packet distributions (where are the outgoing packets concentrated)
    count = 0
    for i in range(0, min(len(sizes), 3000)):
        if i % 30 != 29:
            if sizes[i] > 0:
                count += 1
        else:
            features.append(count)
            count = 0
    for i in range(len(sizes)/30, 100):
        features.append(0)

    #Bursts
    bursts = []
    curburst = 0
    consnegs = 0
    stopped = 0
    for x in sizes:
        if x < 0:
            consnegs += 1
            if (consnegs == 2):
                bursts.append(curburst)
                curburst = 0
                consnegs = 0
        if x > 0:
            consnegs = 0
            curburst += x
    if curburst > 0:
        bursts.append(curburst)
    if (len(bursts) > 0):
        features.append(max(bursts))
        features.append(numpy.mean(bursts))
        features.append(len(bursts))
    else:
        features.append("X")
        features.append("X")
        features.append("X")
##    print bursts
    counts = [0, 0, 0, 0, 0, 0]
    for x in bursts:
        if x > 2:
            counts[0] += 1
        if x > 5:
            counts[1] += 1
        if x > 10:
            counts[2] += 1
        if x > 15:
            counts[3] += 1
        if x > 20:
            counts[4] += 1
        if x > 50:
            counts[5] += 1
    features.append(counts[0])
    features.append(counts[1])
    features.append(counts[2])
    features.append(counts[3])
    features.append(counts[4])
    features.append(counts[5])
    for i in range(0, 100):
        try:
            features.append(bursts[i])
        except:
            features.append("X")

    for i in range(0, 10):
        try:
            features.append(sizes[i] + 1500)
        except:
            features.append("X")

    itimes = [0]*(len(sizes)-1)
    for i in range(1, len(sizes)):
        itimes[i-1] = times[i] - times[i-1]
    if len(itimes) > 0:
        features.append(numpy.mean(itimes))
        features.append(numpy.std(itimes))
    else:
        features.append("X")
        features.append("X")


if __name__ == '__main__':
    '''initialize logger'''
    logger = init_logger()
    '''read in arg'''
    parser = argparse.ArgumentParser(description='knn feature extraction')
    parser.add_argument('t',
                        metavar='<traces path>',
                        help='Path to the directory with the traffic traces to be simulated.')
    parser.add_argument('-option',
                        metavar='<option file>',
                        default = './options-kNN.txt',
                        help='option file dir.')
    parser.add_argument('-mode',
                        metavar='<train or test>',
                        help='extract features for training data or test data')
    args = parser.parse_args()


    optfname = args.option
    d = load_options(optfname)
    data_name = args.t


    '''check whether feature already extracted'''
    path = d['OUTPUT_LOC']+ data_name.split('/')[-2] + '/'
    if args.mode == 'train':
        tmp = glob.glob(os.path.join(path,'*'))
    elif args.mode == 'test':
        tmp = glob.glob(os.path.join(path,'*/*/*'))
    else:
        logger.warn("Wrong mode")
        exit(1)
    if len(tmp) > 2:
        '''sometimes in mac os there will be a .DS store file, so use >1'''
        print('Feature already extracted, skip.')
        exit(0)

    flist = []
    fold = data_name
    
    if(not os.path.isdir(d['OUTPUT_LOC'])):
        os.mkdir(d['OUTPUT_LOC'])

    
    #for training data: folder/inst1, 2 ...
    #for testing data: folder/head/0/inst1... folder/other/0/inst1,2..
    if args.mode == 'test':
        headfpath = os.path.join(fold, 'head/*/*')
        otherfpath = os.path.join(fold, 'other/*/*')
        headflist = glob.glob(headfpath)
        otherflist = glob.glob(otherfpath)

        headflist.extend(otherflist)
        flist = headflist
        for fname in flist:
            # if "-0.cell" in fname:

            #load up times, sizes
            # logger.info("Processing file {}".format(fname))
            times = []
            sizes = []

            tname = fname.split('/')[-1] + ".cellkNN"
            with open(fname, "r") as file:
                f = file.readlines()
            for x in f:
                x = x.split("\t")
                times.append(float(x[0]))
                sizes.append(int(x[1]))


            #Extract features. All features are non-negative numbers or X. 
            features = []
            try: 
                extract(times, sizes, features)
                writestr = ""
                for x in features:
                    if x == 'X':
                        x = -1
                    writestr += (repr(x) + "\n")
                
                tmp = fname.split('/')
                folder = tmp[-4]
                HeadorOther = tmp[-3]
                subfolder = tmp[-2]
                inst = tmp[-1]
                path = os.path.join(d['OUTPUT_LOC'],folder,HeadorOther,subfolder)
                if not os.path.exists(path):
                    os.makedirs(path)
                '''customized for random knn'''
                tname = subfolder+'-'+tname
                fout = open(os.path.join(path,tname), "w")
                fout.write(writestr[:-1])
                fout.close()
            except Exception as e:
                print(e)


    elif args.mode == 'train':
        fpath = os.path.join(fold,'*')
        flist = glob.glob(fpath)



        for fname in flist:
            logger.info("Processing file {}".format(fname))
            # if "-0.cell" in fname:

            #load up times, sizes
            times = []
            sizes = []

            tname = fname.split('/')[-1] + ".cellkNN"
            with open(fname, "r") as file:
                f = file.readlines()
            for x in f:
                x = x.split("\t")
                times.append(float(x[0]))
                sizes.append(int(x[1]))


            #Extract features. All features are non-negative numbers or X. 
            features = []
            try: 
                extract(times, sizes, features)
                writestr = ""
                for x in features:
                    if x == 'X':
                        x = -1
                    writestr += (repr(x) + "\n")
                
                path = d['OUTPUT_LOC']+ data_name.split('/')[-2] + '/'
                if not os.path.exists(path):
                    os.makedirs(path)
                fout = open(path+ tname, "w")
                fout.write(writestr[:-1])
                fout.close()
            except Exception as e:
                print(e)
