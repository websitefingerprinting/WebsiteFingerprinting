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
	extract_cmd = "python3 mp-extract.py " + target
	test_cmd1 = "python3 evaluate.py -m ranpad2_0610_2057_norm.pkl -o ranpad2_0610_2057_norm.npy -p "+ join("./results", fname+'-head.npy') 
	# test_cmd1 = "python3 evaluate.py -m clean.pkl -o clean.npy -p "+ join("./results", fname+'-head.npy') 
	test_cmd2 = "python3 evaluate.py -m clean.pkl -o clean.npy -p "+ join("./results", fname+'-other.npy') 

	subprocess.call(extract_cmd, shell =True)
	subprocess.call(test_cmd1, shell = True)
	subprocess.call(test_cmd2, shell = True)
	print("\n")
