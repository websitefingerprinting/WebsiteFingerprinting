import subprocess


name = "../../defense/results/mergepad_0131_"
targets = [
	name+'1728/',
	name+'1840/',
	name+'1843/',
	name+'1858/',
	name+'1859/',
	name+'1901/',
	name+'1902/',
	name+'1903/',
	name+'1904/',
	name+'1905/',
	name+'1906/',
	name+'1907/',
	name+'1908/',
	name+'1909/',
	name+'1910/',
] 

splitfolder = "../xgboost/scores/mergepad_0131_"
splits = [
	splitfolder+'1728/splitresult.txt',
	splitfolder+'1840/splitresult.txt',
	splitfolder+'1843/splitresult.txt',
	splitfolder+'1858/splitresult.txt',
	splitfolder+'1859/splitresult.txt',
	splitfolder+'1901/splitresult.txt',
	splitfolder+'1902/splitresult.txt',
	splitfolder+'1903/splitresult.txt',
	splitfolder+'1904/splitresult.txt',
	splitfolder+'1905/splitresult.txt',
	splitfolder+'1906/splitresult.txt',
	splitfolder+'1907/splitresult.txt',
	splitfolder+'1908/splitresult.txt',
	splitfolder+'1909/splitresult.txt',
	splitfolder+'1910/splitresult.txt',
] 

for target,split in zip(targets, splits):
	cmd = "python3 split-random.py " + target + \
	" -split "+ split
	# print(cmd)
	# exit(0)
	subprocess.call(cmd, shell= True)
