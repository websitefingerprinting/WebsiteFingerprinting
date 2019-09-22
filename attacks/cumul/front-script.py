import subprocess
from os.path import join
name = "../../defense/results/"
targets = [
name + "ranpad2_0527_1046_norm/",
name + "ranpad2_0527_1047_norm/",
name + "ranpad2_0527_1048_norm/",
name + "ranpad2_0527_1049_norm/",
name + "ranpad2_0527_1050_norm/",
name + "ranpad2_0527_1051_norm/",
name + "ranpad2_0527_1052_norm/",
name + "ranpad2_0527_1053_norm/",
name + "ranpad2_0527_1054_norm/",
name + "ranpad2_0527_1055_norm/",
name + "ranpad2_0527_1056_norm/",
name + "ranpad2_0527_1057_norm/",
name + "ranpad2_0527_1058_norm/",
] 

# targets = [name+"ranpad2_0517_1606_norm/"]
for target in targets:
	fname = target.split('/')[-2]
	extract_cmd = "python3 extract.py " + target
	test_cmd = "python3 main.py ./results/"+ fname+".npy"
	# print(extract_cmd)
	subprocess.call(extract_cmd, shell =True)
	# print(test_cmd)
	subprocess.call(test_cmd, shell = True)
