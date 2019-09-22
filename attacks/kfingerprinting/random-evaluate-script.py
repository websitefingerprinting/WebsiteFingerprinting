import subprocess
from os.path import join

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


# targets = [
# "ranpad2_0603_194535/",
# "ranpad2_0603_194602/",
# "ranpad2_0603_194639/",
# "ranpad2_0603_194724/",
# "ranpad2_0603_194824/",
# "ranpad2_0603_194930/",
# "ranpad2_0603_195046/",
# "ranpad2_0603_195215/",
# "ranpad2_0603_195355/",
# "ranpad2_0603_195536/",
# "ranpad2_0603_195733/",
# "ranpad2_0603_195940/",
# "ranpad2_0603_200155/",
# "ranpad2_0603_200422/",
# "ranpad2_0603_200652/",
# ]

for target in targets:
	target = join(prefix, target)
	# cmd1 = "python3 random-evaluate.py -m clean.pkl -o clean.npy -mode head -p "+ target
	cmd1 = "python3 random-evaluate.py -m ranpad2_0610_2057_norm.pkl -o ranpad2_0610_2057_norm.npy -mode head -p "+ target
	cmd2 = "python3 random-evaluate.py -m clean.pkl -o clean.npy -mode other -p "+ target
	subprocess.call(cmd1, shell= True)
	subprocess.call(cmd2, shell= True)
	# print("\n\n\n\n\n\n\n")
