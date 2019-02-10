#generate trainlist and testlist for other files
import subprocess, sys
from loaders import *
import os 

try:
    d = load_options(sys.argv[1])
    FOLD_NUM = int(sys.argv[2])
    data_name = sys.argv[3]
    print FOLD_NUM
except Exception,e:
    print sys.argv[0], str(e)
    sys.exit(0)

#three different modes:
#MODE 1: trainlist = testlist, and they both contain all data in folder (attacks need to remove duplicates)
#MODE 2: trainlist = testlist, and they both contain a given number of data (CLOSED_SITENUM, CLOSED_INSTNUM, OPEN_INSTNUM)
#MODE 3: trainlist != testlist: they contain a given number of data using 10-fold classification
#DATA_LOC is where the files are
#OUTPUT_LOC is the name to write
#ignore everything that doesn't end with DATA_TYPE
path = d["OUTPUT_LOC"] + data_name + '/'
if not os.path.exists(path):
    os.makedirs(path)
trainout = open(path + "trainlist", "w")
testout = open(path + "testlist", "w")
if (d["FOLD_MODE"] == 1):
    cmd = "ls " + d["DATA_LOC"]
    s = subprocess.check_output(cmd, shell=True)
    s = s.split("\n")
    for sname in s:
        if sname[-len(d["DATA_TYPE"]):] == d["DATA_TYPE"]:
            trainout.write(sname + "\n")
            testout.write(sname + "\n")

if (d["FOLD_MODE"] == 2):
    for s in range(0, d["CLOSED_SITENUM"]):
        for i in range(0, d["CLOSED_INSTNUM"]):
            sname = d["DATA_LOC"] + str(s) + "-" + str(i) + ".cellkNN"
            trainout.write(sname + "\n")
            testout.write(sname + "\n")
    for s in range(0, d["OPEN_INSTNUM"]):
        sname = d["DATA_LOC"] + str(s) + ".cellkNN"
        trainout.write(sname + "\n")
        testout.write(sname + "\n")

if (d["FOLD_MODE"] == 3):
    for s in range(0, d["CLOSED_SITENUM"]):
        for i in range(0, d["CLOSED_INSTNUM"]):
            sname = path + str(s) + "-" + str(i) + ".cellkNN"
            if (i >= int(d["CLOSED_INSTNUM"]/10) * FOLD_NUM and
                i < int(d["CLOSED_INSTNUM"]/10) * (FOLD_NUM+1)):
                testout.write(sname + "\n")
            else:
                trainout.write(sname + "\n")
    for s in range(0, d["OPEN_INSTNUM"]):
        sname = path + str(s) + ".cellkNN"
        if (s >= int(d["OPEN_INSTNUM"]/10) * FOLD_NUM and
            s < int(d["OPEN_INSTNUM"]/10) * (FOLD_NUM+1)):
            testout.write(sname + "\n")
        else:
            trainout.write(sname + "\n")

trainout.close()
testout.close()

wout = open(path + "weightlist", "w")
cmd = "ls " + d["DATA_LOC"] + data_name + '/'
s = subprocess.check_output(cmd, shell=True)
s = s.split("\n")
for sname in s:
    if sname[-len(d["DATA_TYPE"]):] == d["DATA_TYPE"]:
        wout.write(d["DATA_LOC"] + data_name + '/'+sname + "\n")
wout.close()