import subprocess
from os.path import join

for i in range(10):
	cmd = "python3.6 evaluate.py -m ../../defense/one-packet-attack/models/tor3600-"\
	+str(i)+".h5" +" -p ../../defense/one-packet-attack/data/tor3600-"+str(i)+".npy"
	subprocess.call(cmd, shell=True)

# for target in targets:
# 	print("Evaluating {}".format(target))
# 	fname = target.split('/')[-2]
# 	# head_cmd  = "python3 evaluate.py -m ./models/ranpad2_0131_1719_norm.h5 -p ./results/"+ fname + "_head.npy"
# 	head_cmd  = "python3 evaluate.py -m ./models/tor2-4.h5 -p ./results/"+ fname + "_head.npy"
# 	subprocess.call(head_cmd, shell =True)
