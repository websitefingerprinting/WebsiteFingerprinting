import subprocess
from os.path import join
prefix = "../split/results/"
targets = [
"ranpad2_0610_1951/",
"ranpad2_0610_1952/",
"ranpad2_0610_1953/",
"ranpad2_0610_1954/",
"ranpad2_0610_1955/",
"ranpad2_0610_1956/",
"ranpad2_0610_1958/",
"ranpad2_0610_1959/",
"ranpad2_0610_2001/",
"ranpad2_0610_2004/",
"ranpad2_0610_2006/",
"ranpad2_0610_2008/",
"ranpad2_0610_2010/",
"ranpad2_0610_2013/",
"ranpad2_0610_2016/",
] 

# print("Making datasets...")

# for target in targets:
	
# 	extract_cmd = "python3 makedata.py -mode test " + target
# 	subprocess.call(extract_cmd, shell =True)


for target in targets:
	target = join(prefix, target)
	print("Evaluating {}".format(target))
	fname = target.split('/')[-2]
	ex_cmd  = "python3 makedata.py "+ target + " -mode test"
	head_cmd  = "python3 evaluate.py -m ./models/ranpad2_0610_2057_norm.h5 -p ./results/"+ fname + "_head.npy"
	# head_cmd  = "python3 evaluate.py -m ./models/attacktrain.h5 -p ./results/"+ fname + "_head.npy"
	other_cmd  = "python3 evaluate.py -m ./models/attacktrain.h5 -p ./results/"+ fname + "_other.npy"
	subprocess.call(ex_cmd, shell =True)
	subprocess.call(head_cmd, shell =True)
	subprocess.call(other_cmd, shell =True)
	print("\n")