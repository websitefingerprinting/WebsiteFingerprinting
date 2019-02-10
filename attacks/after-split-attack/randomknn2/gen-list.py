#generate ONLY trainlist, customized for mergepadding project

import subprocess, sys
from loaders import *
import os 
import glob 

try:
    # python gen.py option.txt traindata testdata
    d = load_options(sys.argv[1])
    train_data = sys.argv[2]
    test_data = sys.argv[3]
except Exception,e:
    print sys.argv[0], str(e)
    sys.exit(0)

traindata_list = glob.glob(os.path.join(train_data,'*'))
path = os.path.join(d["OUTPUT_LOC"] + train_data.split('/')[-2])
if not os.path.exists(path):
    os.makedirs(path)
with open(os.path.join(path,"trainlist"), "w") as f:
    [f.write(os.path.join(path,s.split('/')[-1]+'.cellkNN')+'\n') for s in traindata_list]



'''In order to generate new test data, customized for mergepadding project'''
'''instances are put into folder: input/merged trace number/1,2,3...'''
testdata_list = glob.glob(os.path.join(test_data,'head/*/*'))
if len(testdata_list) == 0:
    print('Path {} is incorrect!'.format(test_data))
    exit(1)
path = os.path.join(d["OUTPUT_LOC"] ,test_data.split('/')[-2])
if not os.path.exists(path):
    os.makedirs(path)
with open(os.path.join(path,"testlist-head"), "w") as f:
    # [f.write(os.path.join(path+'/head',s.split('/')[-2],s.split('/')[-1]+'.cellkNN')+'\n') for s in testdata_list]
    flist = glob.glob(os.path.join(path, 'head/*/*.cellkNN'))
    flist.sort()
    [f.write(s+'\n') for s in flist]
testdata_list = glob.glob(os.path.join(test_data,'other/*/*'))

if len(testdata_list) == 0:
    print('Path {} is incorrect!'.format(test_data))
    exit(1)
path = os.path.join(d["OUTPUT_LOC"] ,test_data.split('/')[-2])
if not os.path.exists(path):
    os.makedirs(path)
with open(os.path.join(path,"testlist-other"), "w") as f:
    # [f.write(os.path.join(path+'/other',s.split('/')[-2],s.split('/')[-1]+'.cellkNN')+'\n') for s in testdata_list]
    flist = glob.glob(os.path.join(path, 'other/*/*.cellkNN'))
    flist.sort()
    [f.write(s+'\n') for s in flist]