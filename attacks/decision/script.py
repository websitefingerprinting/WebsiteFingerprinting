import subprocess
from os.path import join


train = "../../defense/results/mergepad_0610_1510/"
# train = "../../defense/results/ranpad2_0611_1051/"
prefix = "../../defense/results/"
targets = [
"mergepad_0603_1717_clean/",
"mergepad_0603_1718_clean/",
"mergepad_0603_1719_clean/",
"mergepad_0603_1720_clean/",
"mergepad_0603_1721_clean/",
"mergepad_0603_1722_clean/",
"mergepad_0603_1723_clean/",
"mergepad_0603_1724_clean/",
"mergepad_0603_1725_clean/",
"mergepad_0603_1726_clean/",
"mergepad_0603_1727_clean/",
"mergepad_0603_1728_clean/",
"mergepad_0603_1729_clean/",
"mergepad_0603_1730_clean/",
"mergepad_0603_1731_clean/",
]
# targets = [
# "ranpad2_0610_1951/",
# "ranpad2_0610_1952/",
# "ranpad2_0610_1953/",
# "ranpad2_0610_1954/",
# "ranpad2_0610_1955/",
# "ranpad2_0610_1956/",
# "ranpad2_0610_1958/",
# "ranpad2_0610_1959/",
# "ranpad2_0610_2001/",
# "ranpad2_0610_2004/",
# "ranpad2_0610_2006/",
# "ranpad2_0610_2008/",
# "ranpad2_0610_2010/",
# "ranpad2_0610_2013/",
# "ranpad2_0610_2016/",
# ]

for i,target in enumerate(targets):
	target = join(prefix, target)
	i = i+2 
	cmd = "python3 run_attack.py -train "+ train + " -test "\
	+ target +" -num "+ str(i)
	# print(cmd)
	subprocess.call(cmd, shell= True)
