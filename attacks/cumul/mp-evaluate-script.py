import subprocess


name = "./results/mergepad_0131_"
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


for target in targets:
	cmd1 = "python3 evaluate.py -m clean-trained-SVM.pkl -o ./results/tor2-4.npy -p " +\
	target+"-head.npy"
	cmd2 = "python3 evaluate.py -m clean-trained-SVM.pkl -o ./results/tor2-4.npy -p " +\
	target+"-other.npy"
	subprocess.call(cmd1, shell= True)
	subprocess.call(cmd2, shell= True)
	print("\n\n\n\n\n\n\n")
