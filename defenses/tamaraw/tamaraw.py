#Anoa consists of two components:
#1. Send packets at some packet rate until data is done.
#2. Pad to cover total transmission size.
#The main logic decides how to send the next packet. 
#Resultant anonymity is measured in ambiguity sizes.
#Resultant overhead is in size and time.
#Maximizing anonymity while minimizing overhead is what we want. 
import math
import random
import constants as ct
from time import strftime
import argparse
import logging
import numpy as np
import overheads


logger = logging.getLogger('tamaraw')

'''params'''
DATASIZE = 1
DUMMYCODE = 1
PadL = 50

MON_SITE_NUM = 1
MON_INST_NUM = 1
UNMON_SITE_NUM = 1


#MON_SITE_NUM = 1
#MON_INST_NUM = 2
#UNMON_SITE_NUM = 0


tardist = [[], []]
defpackets = []
##    parameters = [100] #padL
##    AnoaPad(list2, lengths, times, parameters)

import sys
import os
# for x in sys.argv[2:]:
#    parameters.append(float(x))
#    print(parameters)

def fsign(num):
    if num > 0:
        return 0
    else:
        return 1

def rsign(num):
    if num == 0:
        return 1
    else:
        return abs(num)/num

def AnoaTime(parameters):
    direction = parameters[0] #0 out, 1 in
    method = parameters[1]
    if (method == 0):
        if direction == 0:
            return 0.04
        if direction == 1:
            return 0.012  




        

def AnoaPad(list1, list2, padL, method):
    lengths = [0, 0]
    times = [0, 0]
    for x in list1:
        if (x[1] > 0):
            lengths[0] += 1
            times[0] = x[0]
        else:
            lengths[1] += 1
            times[1] = x[0]
        list2.append(x)

    paddings = []

    for j in range(0, 2):
        curtime = times[j]
        topad = -int(math.log(random.uniform(0.00001, 1), 2) - 1) #1/2 1, 1/4 2, 1/8 3, ... #check this
        if (method == 0):
            if padL == 0:
                topad = 0
            else:
                topad = (lengths[j]//padL + topad) * padL
            
        logger.info("Need to pad to %d packets."%topad)
        while (lengths[j] < topad):
            curtime += AnoaTime([j, 0])
            if j == 0:
                paddings.append([curtime, DUMMYCODE * DATASIZE])
            else:
                paddings.append([curtime, -DUMMYCODE* DATASIZE])
            lengths[j] += 1
    paddings = sorted(paddings, key = lambda x: x[0])
    list2.extend(paddings)

def Anoa(list1, list2, parameters): #inputpacket, outputpacket, parameters
    #Does NOT do padding, because ambiguity set analysis. 
    #list1 WILL be modified! if necessary rewrite to tempify list1.
    starttime = list1[0][0]
    times = [starttime, starttime] #lastpostime, lastnegtime
    curtime = starttime
    lengths = [0, 0]
    datasize = DATASIZE
    method = 0
    if (method == 0):
        parameters[0] = "Constant packet rate: " + str(AnoaTime([0, 0])) + ", " + str(AnoaTime([1, 0])) + ". "
        parameters[0] += "Data size: " + str(datasize) + ". "
    if (method == 1):
        parameters[0] = "Time-split varying bandwidth, split by 0.1 seconds. "
        parameters[0] += "Tolerance: 2x."
    listind = 1 #marks the next packet to send
    while (listind < len(list1)):
        #decide which packet to send
        if times[0] + AnoaTime([0, method, times[0]-starttime]) < times[1] + AnoaTime([1, method, times[1]-starttime]):
            cursign = 0
        else:
            cursign = 1
        times[cursign] += AnoaTime([cursign, method, times[cursign]-starttime])
        curtime = times[cursign]
        
        tosend = datasize
        while (list1[listind][0] <= curtime and fsign(list1[listind][1]) == cursign and tosend > 0):
            if (tosend >= abs(list1[listind][1])):
                tosend -= abs(list1[listind][1])
                listind += 1
            else:
                list1[listind][1] = (abs(list1[listind][1]) - tosend) * rsign(list1[listind][1])
                tosend = 0
            if (listind >= len(list1)):
                break
        if cursign == 0:
            list2.append([curtime, datasize])
        else:
            list2.append([curtime, -datasize])
        lengths[cursign] += 1
        



def init_directories():
    # Create a results dir if it doesn't exist yet
    if not os.path.isdir(ct.RESULTS_DIR):
        os.mkdir(ct.RESULTS_DIR)

    # Define output directory
    timestamp = strftime('%m%d_%H%M')
    output_dir = os.path.join(ct.RESULTS_DIR, 'tamaraw_'+timestamp)
    #logger.info("Creating output directory: %s" % output_dir)

    # make the output directory
    os.mkdir(output_dir)

    return output_dir


def parse_arguments():
    # Read configuration file
    # conf_parser = configparser.RawConfigParser()
    # conf_parser.read(ct.CONFIG_FILE)

    parser = argparse.ArgumentParser(description='It simulates tamaraw on a set of web traffic traces.')

    parser.add_argument('traces_path',
                        metavar='<traces path>',
                        help='Path to the directory with the traffic traces to be simulated.')
    

    # parser.add_argument('-c', '--config',
    #                     dest="section",
    #                     metavar='<config name>',
    #                     help="Adaptive padding configuration.",
    #                     choices= conf_parser.sections(),
    #                     default="default")



    parser.add_argument('--log',
                        type=str,
                        dest="log",
                        metavar='<log path>',
                        default='stdout',
                        help='path to the log file. It will print to stdout by default.')

    args = parser.parse_args()
    #config = dict(conf_parser._sections[args.section])
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

if __name__ == '__main__':
    args = parse_arguments()
    logger.info("Arguments: %s" % (args))
    foldout = init_directories()
    
    packets = []
    desc = ""
    anoad = []
    anoadpad = []
    latencies = []
    sizes = []
    bandwidths = []

    tot_new_size = 0.0
    tot_new_latency = 0.0
    tot_old_size = 0.0
    tot_old_latency = 0.0


    for site in range(0, MON_SITE_NUM):
        for inst in range(0, MON_INST_NUM):
            fname = str(site) + "-" + str(inst)+".cell"
            logger.info('Simulating %s...'%fname)
            packets = []
            with open(os.path.join(args.traces_path, fname), "r") as f:
                lines = f.readlines()
                starttime = float(lines[0].split("\t")[0])
                for x in lines:
                    x = x.split("\t")
                    packets.append([float(x[0]) - starttime, int(x[1])])
            list2 = [packets[0]]
            parameters = [""]
            
            Anoa(packets, list2, parameters)
            list2 = sorted(list2, key = lambda list2: list2[0])
            anoad.append(list2)

            list3 = []
            
            AnoaPad(list2, list3, PadL, 0)

            fout = open(os.path.join(foldout,fname), "w")
            for x in list3:
                fout.write("{:.4f}\t{:d}\n".format(x[0],x[1]))
            fout.close()

            #latency:
            old = packets[-1][0] - packets[0][0]
            #new definition of time latency:
            new = list2[-1][0] -list2[0][0]
            #new = list3[-1][0] -list3[0][0]

            #in case there is precision loss
            if new < old:
                new = old

            latency = 1.0*new/old
            latencies.append(latency)
            tot_new_latency += new
            tot_old_latency += old

            #sizes:
            old = sum([abs(p[1]) for p in packets])
            mid = sum([abs(p[1]) for p in list2])
            new = sum([abs(p[1]) for p in list3])
            logger.info("old size:%d,mid size:%d, new size:%d"%(old,mid, new))
            size = 1.0*new/old 
            sizes.append(size)
            tot_new_size += new
            tot_old_size += old
            #bandwidth
            # bandwidth = size/latency * 1.0
            # bandwidths.append(bandwidth)
            logger.info("Latency overhead: %.4f,size overhead:%.4f"%(latency,size))

    for site in range(0, UNMON_SITE_NUM):
        fname = str(site)+".cell"
        logger.info('Simulating %s..'%fname)
        packets = []
        with open(os.path.join(args.traces_path,fname), "r") as f:
            lines = f.readlines()
            starttime = float(lines[0].split("\t")[0])
            for x in lines:
                x = x.split("\t")
                packets.append([float(x[0]) - starttime, int(x[1])])
        list2 = [packets[0]]
        parameters = [""]
        
        Anoa(packets, list2, parameters)
        list2 = sorted(list2, key = lambda list2: list2[0])
        anoad.append(list2)

        list3 = []
        
        AnoaPad(list2, list3, PadL, 0)

        fout = open(os.path.join(foldout, fname), "w")
        for x in list3:
            fout.write("{:.4f}\t{:d}\n".format(x[0],x[1]))
        fout.close()
        #latency:
        old = packets[-1][0] - packets[0][0]
       #new definition of time latency:
        new = list2[-1][0] -list2[0][0]
        # new = list3[-1][0] -list3[0][0]

        #in case there is precision loss
        if new < old:
            new = old

        tot_new_latency += new
        tot_old_latency += old
        latency = 1.0*new/old 
        latencies.append(latency)

        #sizes:
        old = sum([abs(p[1]) for p in packets])
        mid = sum([abs(p[1]) for p in list2])
        new = sum([abs(p[1]) for p in list3])
        logger.info("old size:%d,mid size:%d, new size:%d"%(old,mid, new))
        size = 1.0*new/old 
        sizes.append(size)

        tot_new_size += new
        tot_old_size += old
        #bandwidth
        # bandwidth = size/latency * 1.0
        # bandwidths.append(bandwidth)
        logger.info("Latency overhead: %.4f,size overhead:%.4f"%(latency,size))




    foldout = foldout.split('/')[-1]
    logger.info('Average latency overhead: %.4f'% (1.0*tot_new_latency/tot_old_latency-1))
    logger.info('Average size overhead:%.4f'%(1.0*tot_new_size/tot_old_size -1))
    logger.info('%s'%foldout)
    # logger.info("Median latency overhead: %.4f"%np.median(latencies))
    # logger.info("Median size overhead:%.4f"%np.median(sizes))
    

