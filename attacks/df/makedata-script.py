import subprocess
from os.path import join
f= "/home/homes/jgongac/websiteFingerprinting/defense/results/"
g= "/home/data/jgongac/websiteFingerprinting/defense/results/"

server = f

ls = [
"mergepad_0603_1717/",
"mergepad_0603_1718/",
"mergepad_0603_1719/",
"mergepad_0603_1720/",
"mergepad_0603_1721/",
"mergepad_0603_1722/",
"mergepad_0603_1723/",
"mergepad_0603_1724/",
"mergepad_0603_1725/",
"mergepad_0603_1726/",
"mergepad_0603_1727/",
"mergepad_0603_1728/",
"mergepad_0603_1729/",
"mergepad_0603_1730/",
"mergepad_0603_1731/",
] 

targets = []
for l in ls:
	# targets.append(join(server, l))
	targets.append(join("../split/results/", l))

for target in targets:
	print("Evaluating {}".format(target))
	cmd  = "python3 makedata.py "+ target + " -mode test"
	subprocess.call(cmd, shell =True)