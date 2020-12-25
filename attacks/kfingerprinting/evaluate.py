import joblib
import pickle
import const as ct
import logging
import argparse
import configparser
import numpy as np
import multiprocessing

logger = logging.getLogger('kf')

#def init_logger():
#    logger = logging.getLogger('kf')
#    logger.setLevel(logging.DEBUG)
#    # create console handler and set level to debug
#    ch = logging.StreamHandler()
#    # create formatter
#    formatter = logging.Formatter(const.LOG_FORMAT)
#    # add formatter to ch
#    ch.setFormatter(formatter)
#    # add ch to logger
#    logger.addHandler(ch)
#    return logger



def parse_arguments():

    parser = argparse.ArgumentParser(description='Evaluate.')

    parser.add_argument('-m',
                        metavar='<model path>',
                        help='Path to the directory of the model')
    parser.add_argument('-p',
                        metavar='<feature path>',
                        help='Path to the directory of the extracted features')
    parser.add_argument('-o',
                        metavar='<original training leaf path>',
                        help='Path to the directory of the extracted features')
    parser.add_argument('--log',
                        type=str,
                        dest="log",
                        metavar='<log path>',
                        default='stdout',
                        help='path to the log file. It will print to stdout by default.')
    # Parse arguments
    args = parser.parse_args()
    return args


def init_logger():
    logger = logging.getLogger('kf')
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter(ct.LOG_FORMAT)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger


### Parameters ###
r = 1000  #N/P

def read_conf(file):
    cf = configparser.ConfigParser()
    cf.read(file)  
    return dict(cf['default'])


# def hdist(leaf1,leaf2):
#     if len(leaf1) != len(leaf2):
#         raise Exception("hdist called with wrong lengths {} {}".format(len(leaf1), len(leaf2)))
#     d = 0
#     for i in range(0,len(leaf1)):
#         d += hamming_dist(leaf1[i],leaf2[i])
#     return d

# def hamming_dist(x,y):
#     return 1 - int(x==y)


def get_single_neighbor(testleaf):
    global trainleaves, K
    
    # print(trainleaves[:2])
    trainleaf, trainlabel = list(zip(*trainleaves))[0], list(zip(*trainleaves))[1]
    trainleaf = np.array(trainleaf)
    trainlabel = np.array(trainlabel)
    atile = np.tile(testleaf[0], (trainleaf.shape[0],1))
    dists = np.sum(atile != trainleaf, axis = 1)
    k_neighbors = trainlabel[np.argsort(dists)[:K]]
    return [testleaf[1], k_neighbors]
    # if len(set(k_neighbors)) == 1:
    #     return k_neighbors[0]
    # else:
    #     return 100

# def get_single_neighbor(testleaf):
#     # logger.info('Getting neighbor of class %d', testleaf[1])
#     global trainleaves, K
#     dists  = []
#     for j, trainleaf in enumerate(trainleaves):
#         dists.append(hdist(testleaf[0],trainleaf[0]))
#     guessclasses_ind = heapq.nsmallest(K, enumerate(dists), key=lambda x: x[1]) 
#     guessclasses = []
#     for i in guessclasses_ind:
#         guessclasses.append(trainleaves[i[0]][1])
#     return [testleaf[1],guessclasses]

def parallel_get_neighbors(traindata, testdata, MAX_K, n_jobs = 15):
    global trainleaves, K
    K = MAX_K
    trainleaves = list(traindata)
    testleaves = list(testdata)

    pool = multiprocessing.Pool(n_jobs)
    neighbors = pool.map(get_single_neighbor, testleaves)
    return neighbors

# def get_neighbors(traindata, testdata, MAX_K):
#     neighbors = [] 
#     traindata = list(traindata)
#     testdata = list(testdata)
   
#     neighbors = []
#     for testleaf in testdata:
#         logger.info('Find the closest k neighbors for %s'%testleaf[1])
#         dists = []
#         for j,trainleaf in enumerate(traindata):
#             dists.append(hdist(testleaf[0],trainleaf[0]))
#             #print('index:',j,'class:',trainleaf[1],'dist:',hdist(testleaf[0],trainleaf[0]))
#         guessclasses_ind = heapq.nsmallest(MAX_K, enumerate(dists), key=lambda x: x[1]) 
#         guessclasses = []
#         for i in guessclasses_ind:
#             guessclasses.append(traindata[i[0]][1])
# #        print('guessclasses:', guessclasses)
#         neighbors.append([testleaf[1],guessclasses])
# #        print('my neighbors:\n', neighbors)
#     return neighbors



def open_world_acc(neighbors, MON_SITE_NUM):
    # logger.info('Calculate the precision...')
    tp, wp, fp, p, n = 0, 0, 0, 0 ,0
    for i,neighbor in enumerate(neighbors):
        trueclass = neighbor[0]
        if trueclass < MON_SITE_NUM:
            p += 1
        else:
            n += 1
            
        if len(set(neighbor[1])) == 1:
            guessclass = neighbor[1][0]
            if guessclass != MON_SITE_NUM:
                if guessclass == trueclass:
                    tp += 1
                else:
                    if trueclass != MON_SITE_NUM: #is monitored site
                        wp += 1
                        # logger.info('Test %d, Wrong positive:%s'%(i,neighbor))
                    else:
                        fp += 1
                        # logger.info('Test %d, False positive:%s'%(i,neighbor))

    return tp,wp,fp,p,n


if __name__ == '__main__':   
    init_logger()
    args = parse_arguments()
    # logger.info("Arguments: %s" % (args))
    cf = read_conf(ct.confdir)
    MON_SITE_NUM = int(cf['monitored_site_num'])
    # logger.info('loading model...')
    model =  joblib.load(args.m)
    train_leaf = np.load(args.o, allow_pickle=True).item()
    
    # logger.info('loading data...')
    dic = np.load(args.p, allow_pickle=True).item()   
    X_test = np.array(dic['feature'])
    y_test = np.array(dic['label'])
    y_test = np.array([label[0] for label in y_test])

    # logger.info('getting test_leaf...')
    test_leaf= zip(model.apply(X_test), y_test)
    reports = []
    neighbors = parallel_get_neighbors(train_leaf, test_leaf,3, 20)
    tp,wp,fp,p,n = open_world_acc(neighbors,MON_SITE_NUM)
    reports.append(( tp,wp,fp,p,n))
    for report in reports:
        r = ' '.join(['%d']*len(report))%tuple(report)
        print(r.lstrip())