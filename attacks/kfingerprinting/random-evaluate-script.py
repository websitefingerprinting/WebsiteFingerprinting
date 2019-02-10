import subprocess


name = "../split/randomresults/mergepad_0131_"
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
	cmd1 = "python3 random-evaluate.py -m clean-trained-kf.pkl -o tor_leaf.npy -mode head -p "+ target
	# cmd2 = "python3 random-evaluate.py -m clean-trained-kf.pkl -o tor_leaf.npy -mode other -p "+ target
	subprocess.call(cmd1, shell= True)
	# subprocess.call(cmd2, shell= True)
	# print("\n\n\n\n\n\n\n")
