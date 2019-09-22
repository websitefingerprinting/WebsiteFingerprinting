#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 20:15:16 2018

@author: aaron
"""


import glob  
import numpy as np

if __name__ == '__main__':
    path = '../../defense/results/mergepad_1220_1431/*.merge'
    flist = glob.glob(path)
    flist.sort(key = lambda x: int(x.split('/')[-1].split('.')[0]))
    l = []
    for f in flist:
        with open(f,'r') as ff:
            l.append( len(ff.readlines()) )
    l = np.array(l)
        