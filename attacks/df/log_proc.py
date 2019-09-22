#This is to read log
import os 
import argparse
import re
from pprint import pprint
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DF log process')
    parser.add_argument('log',
                        metavar='<logdir>',
                        help='Path to the log.')
    
    args = parser.parse_args()

    pattern = re.compile(r"INFO\s*(?P<tp>\d+)\s(?P<wp>\d+)\s(?P<fp>\d+)\s(?P<p>\d+)\s(?P<n>\d+)\s*")
    cnt = 0
    dic = []
    with open(args.log, 'r') as f:
        lines = f.readlines()
    for line in lines:
        m = re.search(pattern, line)
        if m: 
            tmp = []
            tmp.extend([int(m.group('tp')),int(m.group('wp')),int(m.group('fp')),int(m.group('p')),int(m.group('n')) ])
            cnt += 0.5
            dic.append(tmp)
    
    i = 0 
    tp, wp, fp, p, n = 0,0,0,0,0
    for each in dic:

        i +=1
        print("{} {} {} {} {}".format(each[0],each[1],each[2],each[3],each[4]))
        tp += each[0]
        wp += each[1]
        fp += each[2]
        p += each[3]
        n += each[4]
        if i%2 == 0:
            # print("{} {} {} {} {}".format(tp, wp, fp, p, n))
            tp, wp, np, p, n = 0,0,0,0,0
            for i in range(7):
                print("")


    print(cnt)