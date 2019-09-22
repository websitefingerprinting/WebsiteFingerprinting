import subprocess
from os.path import join
name = "../../defense/results/"
targets = [
name + "ranpad2_0709_1408_norm/",
name + "ranpad2_0709_1409_norm/",
name + "ranpad2_0709_1410_norm/",
name + "ranpad2_0709_1411_norm/",
name + "ranpad2_0709_1412_norm/",
name + "ranpad2_0709_1413_norm/",
name + "ranpad2_0709_1414_norm/",
name + "ranpad2_0709_1415_norm/",
] 


for target in targets:
	fname = target.split('/')[-2]
	# print(fname)
	extract_cmd = "python3 extract.py " + target
	test_cmd = "python3 new_main.py ./results/"+ fname+".npy"
	# print(extract_cmd)
	subprocess.call(extract_cmd, shell =True)
	# print(test_cmd)
	subprocess.call(test_cmd, shell = True)
