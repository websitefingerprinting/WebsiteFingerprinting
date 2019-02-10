import subprocess


name = "../../split/results/mergepad_0131_"
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


for target in targets:
	fname = target.split('/')[-2]
	cmd1 = "./run_attack-head.sh ../../../data/tor2-4/ "+ target+\
	" ./log/"+fname+'-head.log' 
	cmd2 = "./run_attack-other.sh ../../../data/tor2-4/ "+ target+\
	" ./log/"+fname+'-other.log' 
	subprocess.call(cmd1, shell= True)
	# subprocess.call(cmd2, shell= True)
	# 