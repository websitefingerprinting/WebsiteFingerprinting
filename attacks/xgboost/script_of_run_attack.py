import subprocess
from os.path import join

tests = [
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

prefix = "../../defense/results/"



train = "../../defense/results/mergepad_0603_1908/"

for test in tests:
	test = join(prefix, test)
	cmd = "python3 run_attack.py -train "+train + " -test "+ test
	subprocess.call(cmd, shell= True)