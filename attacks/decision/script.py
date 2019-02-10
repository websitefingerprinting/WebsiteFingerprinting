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


for i,target in enumerate(targets):
	i = i+2 
	cmd = "python3 run_attack.py -train ../../defense/results/mergepad_0201_1427/ -test "\
	+ target +" -num "+ str(i)
	# print(cmd)
	subprocess.call(cmd, shell= True)
