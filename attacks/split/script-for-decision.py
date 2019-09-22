import subprocess


name = "../../defense/results/ranpad2_0610_"
targets = [
name + "1951/",
name + "1952/",
name + "1953/",
name + "1954/",
name + "1955/",
name + "1956/",
name + "1958/",
name + "1959/",
name + "2001/",
name + "2004/",
name + "2006/",
name + "2008/",
name + "2010/",
name + "2013/",
name + "2016/",
] 

splitfolder = "../xgboost/scores/ranpad2_0610_"
splits = [
	splitfolder+'1951/splitresult.txt',
	splitfolder+'1952/splitresult.txt',
	splitfolder+'1953/splitresult.txt',
	splitfolder+'1954/splitresult.txt',
	splitfolder+'1955/splitresult.txt',
	splitfolder+'1956/splitresult.txt',
	splitfolder+'1958/splitresult.txt',
	splitfolder+'1959/splitresult.txt',
	splitfolder+'2001/splitresult.txt',
	splitfolder+'2004/splitresult.txt',
	splitfolder+'2006/splitresult.txt',
	splitfolder+'2008/splitresult.txt',
	splitfolder+'2010/splitresult.txt',
	splitfolder+'2013/splitresult.txt',
	splitfolder+'2016/splitresult.txt',
] 

for target,split in zip(targets, splits):
	cmd = "python3 split-random.py " + target + \
	" -split "+ split
	# print(cmd)
	# exit(0)
	subprocess.call(cmd, shell= True)
