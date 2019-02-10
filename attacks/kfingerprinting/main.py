import numpy as np 
import argparse
import logging
import heapq
import configparser
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.externals import joblib 
import const
import multiprocessing
import random

random.seed(1123)
np.random.seed(1123)

def init_logger():
    logger = logging.getLogger('kf')
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter(const.LOG_FORMAT)
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


def hdist(leaf1,leaf2):
    if len(leaf1) != len(leaf2):
        raise Exception("hdist called with wrong lengths {} {}".format(len(leaf1), len(leaf2)))
    d = 0
    for i in range(0,len(leaf1)):
        d += hamming_dist(leaf1[i],leaf2[i])
    return d

def hamming_dist(x,y):
    return 1 - int(x==y)

def get_single_neighbor(testleaf):
    # logger.info('Getting neighbor of class %d', testleaf[1])
    global trainleaves, K
    dists  = []
    for j, trainleaf in enumerate(trainleaves):
        dists.append(hdist(testleaf[0],trainleaf[0]))
    guessclasses_ind = heapq.nsmallest(K, enumerate(dists), key=lambda x: x[1]) 
    guessclasses = []
    for i in guessclasses_ind:
        guessclasses.append(trainleaves[i[0]][1])
    return [testleaf[1],guessclasses]

def parallel_get_neighbors(traindata,testdata, MAX_K,n_jobs = 15):
    global trainleaves, K
    K = MAX_K
    trainleaves = list(traindata)
    testleaves = list(testdata)

    pool = multiprocessing.Pool(n_jobs)
    neighbors = pool.map(get_single_neighbor, testleaves)
    return neighbors

def get_neighbors(traindata, testdata, MAX_K):
    neighbors = [] 
    traindata = list(traindata)
    testdata = list(testdata)

    neighbors = []
    for testleaf in testdata:
        logger.info('Find the closest k neighbors for %s'%testleaf[1])
        dists = []
        for j,trainleaf in enumerate(traindata):
            dists.append(hdist(testleaf[0],trainleaf[0]))
            #print('index:',j,'class:',trainleaf[1],'dist:',hdist(testleaf[0],trainleaf[0]))
        guessclasses_ind = heapq.nsmallest(MAX_K, enumerate(dists), key=lambda x: x[1]) 
        guessclasses = []
        for i in guessclasses_ind:
            guessclasses.append(traindata[i[0]][1])
        neighbors.append([testleaf[1],guessclasses])
        print('my neighbors:\n', neighbors)
    return neighbors


def closed_world_acc(neighbors):
    logger.info('Calculate the accuracy...')
    tp, p = 0, len(neighbors)

    for neighbor in neighbors:
        if len(set(neighbor[1])) == 1:
            guessclass = neighbor[1][0]
            if guessclass == neighbor[0]:
                tp += 1
    return tp/p

def open_world_acc(neighbors, MON_SITE_NUM):
    logger.info('Calculate the precision...')
    tp, wp, fp, p, n = 0, 0, 0, 0 ,0
    for neighbor in neighbors:
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
                        logger.info('Wrong positive:%s', neighbor)
                    else:
                        fp += 1
                        logger.info('False positive:%s', neighbor)

    return tp,wp,fp,p,n
    
def kfingerprinting(X_train,X_test,y_train,y_test):
    logger.info('training...')
    model = RandomForestClassifier(n_jobs=-1, n_estimators=1000, oob_score=True)
    model.fit(X_train, y_train)
#    M = model.predict(X_test)
    # for i in range(0,len(M)):
    #     x = M[i]
    #     label = str(Y_test[i][0])+'-'+str(Y_test[i][1])
    #     logger.info('%s: %s'%(str(label), str(x)))
    acc = model.score(X_test, y_test)
    logger.info('Accuracy = %.4f'%acc)
    train_leaf = zip(model.apply(X_train), y_train)
    test_leaf = zip(model.apply(X_test), y_test)
    joblib.dump(model, 'ranpad2_0131_1719.pkl')
    return train_leaf, test_leaf

if __name__ == '__main__':
    '''initialize logger'''
    logger = init_logger()
    '''read config'''
    parser = argparse.ArgumentParser(description='k-FP attack')
    parser.add_argument('feature_path',
                        metavar='<feature path>',
                        help='Path to the directory of the extracted features')
    args = parser.parse_args()
    
    '''read config file'''
    cf = read_conf(const.confdir)
    MON_SITE_NUM = int(cf['monitored_site_num'])
    MON_INST_NUM = int(cf['monitored_inst_num'])
    if cf['open_world'] == '1':
        UNMON_SITE_NUM = int(cf['unmonitored_site_num'])
        OPEN_WORLD = 1
    else:
        OPEN_WORLD = 0
    
    logger.info('loading data...')
    dic = np.load(args.feature_path).item()   
    
    X = np.array(dic['feature'])
    Y = np.array(dic['label'])
    y = np.array([label[0] for label in Y])
    
    # here just want to save the model 
    train_leaf, test_leaf = kfingerprinting(X,X[:1],y, y[:1])
    np.save('leaf_ranpad2_0131_1719.npy',train_leaf)
    


   #  sss = StratifiedShuffleSplit(n_splits=10, test_size=0.1, random_state=0)
   #  reports = []

   #  folder_num = 1
   #  for train_index, test_index in sss.split(X,y):
   #     logger.info('Testing fold %d'%folder_num)
   #     folder_num += 1 
   #     X_train, X_test = X[train_index], X[test_index]
   #     y_train, y_test = y[train_index], y[test_index]
   #     Y_train, Y_test = Y[train_index], Y[test_index]  

   #     train_leaf, test_leaf = kfingerprinting(X_train,X_test,y_train, y_test)
   #     # neighbors = get_neighbors(train_leaf, test_leaf, 1)
   #     neighbors = parallel_get_neighbors(train_leaf, test_leaf,3, 25)
   #     if OPEN_WORLD:
   #         tp,wp,fp,p,n = open_world_acc(neighbors,MON_SITE_NUM)
   #         reports.append(( tp,wp,fp,p,n))
   #     else:
   #         result = closed_world_acc(neighbors)
   # #    print(neighbors)
   #     logger.info('tp:%d, wp:%d, fp:%d, p:%d, n:%d'%(tp, wp, fp, p, n))
   #     try:
   #         r_precision = tp*n / (tp*n+wp*n+r*p*fp)
   #     except:
   #         r_precision = 0.0
   #     logger.info('%d-Precision is %.4f'%(r, r_precision))
   
   #  for report in reports:
   #     r = ', '.join(['%3d']*len(report))%tuple(report)
   #     print(r)
   #  tps ,wps, fps, ps, ns = 0, 0, 0, 0, 0
   #  for report in reports:
   #      tps += report[0]
   #      wps += report[1]
   #      fps += report[2]
   #      ps  += report[3]
   #      ns  += report[4]
   #  print("{:3d} {:3d} {:3d} {:3d} {:3d}".format(tps, wps, fps, ps, ns))
    
