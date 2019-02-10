import subprocess
from os.path import join

name = "scores/mergepad_0131_"
targets = [
	name+'1728_clean/',
	name+'1840_clean/',
	name+'1843_clean/',
	name+'1858_clean/',
	name+'1859_clean/',
	name+'1901_clean/',
	name+'1902_clean/',
	name+'1903_clean/',
	name+'1904_clean/',
	name+'1905_clean/',
	name+'1906_clean/',
	name+'1907_clean/',
	name+'1908_clean/',
	name+'1909_clean/',
	name+'1910_clean/',
] 


for target in targets:
	kdir = join("../decision/results/", target.split('/')[-2]+ ".npy")
	cmd = "python3 getsplit-base-rate.py "+ target + " -k "+ kdir
	subprocess.call(cmd, shell= True)
