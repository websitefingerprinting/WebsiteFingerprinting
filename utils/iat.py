import logging
import argparse
import pandas as pd
import numpy as np
import glob
import os
import sys
import multiprocessing as mp

logger = logging.getLogger('ita')
def config_logger(args):
    # Set file
    log_file = sys.stdout
    if args.log != 'stdout':
        log_file = open(args.log, 'w')
    ch = logging.StreamHandler(log_file)

    # Set logging format
    LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
    ch.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(ch)

    # Set level format
    logger.setLevel(logging.INFO)

def parse_arguments():

    parser = argparse.ArgumentParser(description='Calculate overhead for a trace folder.')

    parser.add_argument('dir',
                        metavar='<traces path>',
                        help='Path to the directory with the traffic traces to be simulated.')

    parser.add_argument('-format',
                        metavar='<format>',
                        default = '.merge',
                        help='file format, default: "xx.merge" ')

    parser.add_argument('-mode',
                        metavar='<mode>',
                        default = 'dirty',
                        help='clean or dirty')

    parser.add_argument('--log',
                        type=str,
                        dest="log",
                        metavar='<log path>',
                        default='stdout',
                        help='path to the log file. It will print to stdout by default.')

    args = parser.parse_args()
    config_logger(args)

    return args

def calc_single_ita(param):
    t = param[0]
    mode = param[1]
    # logger.info('Processing file {}'.format(t))
    with open(t,'r') as f:
        trace = pd.Series(f.readlines()).str.slice(0,-1)
        trace = np.array(trace.str.split('\t',expand = True).astype("float"))

    
    ita1 = []
    ita2 = []
    for i in range(1, len(trace)):
        pre, cur = trace[i-1], trace[i]
        if mode == "clean":
            if pre[1] < 0 and cur[1] > 0:
                ita1.append(cur[0]-pre[0])
            elif pre[1]>0 and cur[1] <0:
                ita2.append(cur[0]-pre[0])
            if cur[0] - pre[0] > 3 or trace[-1][0] < 10:
                if "-" in t.split('/')[-1]:
                    with open("tor2-5-1.txt","a") as f:
                        # f.write(t+"\t"+str(cur[0])+"\n")
                        f.write(t+"\n")
                break

        else:
            if (abs(cur[1]) >998 or abs(pre[1]) > 998) and cur[0] - pre[0] > 8:
                print(t)
                print(pd.DataFrame(trace[i-3:i+2]))

            if abs(pre[1]) < 888 and abs(cur[1]) > 998:
                #1, 999
                ita1.append(cur[0] - pre[0])
            elif abs(pre[1]) > 998 and abs(cur[1]) < 888:
                # 999, 1
                ita2.append(cur[0] - pre[0])


    return (ita1, ita2)




def parallel(flist,mode,n_jobs = 25):
    pool = mp.Pool(n_jobs)
    modes = [mode]*len(flist)
    params = zip(flist,modes)
    ita  = pool.map(calc_single_ita, params)    
    return ita

if __name__ == '__main__':
    args = parse_arguments()
    flist = glob.glob(os.path.join(args.dir,'*'+args.format))
    flist.sort(key = lambda x: x.split('/')[-1])
    # ita = []
    # for f in flist:
    #     iii = calc_single_ita(f)
    #     ita.append(iii)
    ita = parallel(flist, args.mode)
    ita = list(zip(*ita))
    ita1 = ita[0]
    ita2 = ita[1]
    new_ita1 = []
    new_ita2 = []
    [new_ita1.extend(i) for i in ita1]
    [new_ita2.extend(i) for i in ita2]
    ita1 = np.array(new_ita1)
    ita2 = np.array(new_ita2)

    logger.info('ita1:  {:.4f} +- {:.4f} '.format(ita1.mean(), ita1.std()))
    logger.info('percentile: {:4f}, {:4f}, {:4f}, {:4f}, {:4f}.'.format(np.percentile(ita1, 100),np.percentile(ita1, 90),np.percentile(ita1, 75),np.percentile(ita1, 50),np.percentile(ita1, 25)))
    logger.info('ita2:  {:.4f} +- {:.4f} '.format(ita2.mean(), ita2.std()))

    logger.info('percentile: {:4f}, {:4f}, {:4f}, {:4f}, {:4f}.'.format(np.percentile(ita2, 100),np.percentile(ita2, 90),np.percentile(ita2, 75),np.percentile(ita2, 50),np.percentile(ita2, 25)))

    





