import subprocess
from os.path import join

# name = "../split/randomresults/mergepad_0131_"
# targets = [
	# name+'1728_clean/',
# 	name+'1840_clean/',
# 	name+'1843_clean/',
# 	name+'1858_clean/',
# 	name+'1859_clean/',
# 	name+'1901_clean/',
# 	name+'1902_clean/',
# 	name+'1903_clean/',
# 	name+'1904_clean/',
# 	name+'1905_clean/',
# 	name+'1906_clean/',
# 	name+'1907_clean/',
# 	name+'1908_clean/',
# 	name+'1909_clean/',
# 	name+'1910_clean/',
# ] 
prefix = "../split/randomresults/"
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
	print("process {}".format(target))
	cmd1 = "python3 random-evaluate.py -m models/ranpad2_0610_2057_norm.h5 -mode head -p "+ target
	# cmd1 = "python3 random-evaluate.py -m models/attacktrain.h5 -mode head -p "+ target
	cmd2 = "python3 random-evaluate.py -m models/attacktrain.h5 -mode other -p "+ target
	# cmd2 = "python3 random-evaluate.py -m clean-trained-kf.pkl -o tor_leaf.npy -mode other -p "+ target
	subprocess.call(cmd1, shell= True)
	subprocess.call(cmd2, shell= True)
	# print("\n\n\n\n\n\n\n")
