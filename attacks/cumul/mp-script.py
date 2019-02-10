import subprocess
from os.path import join
name = "../split/results/mergepad_0131_"
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
	extract_cmd = "python3 mp-extract.py " + target
	test_cmd = "python3 evaluate.py -m clean-trained-SVM.pkl -o ./results/tor2-4.npy -p "+ join("./results", fname+'-head.npy') 

	subprocess.call(extract_cmd, shell =True)
	subprocess.call(test_cmd, shell = True)