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



for target in targets:
	target  = join(prefix, target)
	fname = target.split('/')[-2]
	fname = join("./results/", fname)
	cmd0 = "python3 mp-extract.py " + target
	cmd1 = "python3 evaluate.py -m ranpad2_0610_2057_norm.pkl -o ./results/ranpad2_0610_2057_norm.npy -p " +\
	fname+"-head.npy"
	# cmd1 = "python3 evaluate.py -m clean.pkl -o ./results/attacktrain.npy -p " +\
	# fname+"-head.npy"	
	cmd2 = "python3 evaluate.py -m clean.pkl -o ./results/attacktrain.npy -p " +\
	fname+"-other.npy"
	# print(cmd0)
	# print(cmd1)
	# print(cmd2)
	# exit(0)
	subprocess.call(cmd0, shell= True)
	subprocess.call(cmd1, shell= True)
	subprocess.call(cmd2, shell= True)
	print("\n")
