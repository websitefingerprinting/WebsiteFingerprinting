import subprocess
import multiprocessing as mp

name = "./log/mergepad_0131_"
targets = [
	name+'1728_clean',
	name+'1840_clean',
	name+'1843_clean',
	name+'1858_clean',
	name+'1859_clean',
	name+'1901_clean',
	name+'1902_clean',
	name+'1903_clean',
	name+'1904_clean',
	name+'1905_clean',
	name+'1906_clean',
	name+'1907_clean',
	name+'1908_clean',
	name+'1909_clean',
	name+'1910_clean',
] 




def work(target):
	log1= target+'-head.log'
	log2= target+'-other.log'
	cmd1 = "python3 parselog.py " + log1
	cmd2 = "python3 parselog.py " + log2
	subprocess.call(cmd1, shell= True)
	subprocess.call(cmd2, shell= True)

pool = mp.Pool(5)
pool.map(work, targets)
