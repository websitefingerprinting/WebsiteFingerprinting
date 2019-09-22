import subprocess
from os.path import join

names= [
"ranpad2_0527_1046_norm",
"ranpad2_0527_1047_norm",
"ranpad2_0527_1048_norm",
"ranpad2_0527_1049_norm",
"ranpad2_0527_1050_norm",
"ranpad2_0527_1051_norm",
"ranpad2_0527_1052_norm",
"ranpad2_0527_1053_norm",
"ranpad2_0527_1054_norm",
"ranpad2_0527_1055_norm",
"ranpad2_0527_1056_norm",
"ranpad2_0527_1057_norm",
"ranpad2_0527_1058_norm",
]


#eg: ./run_attack.sh ranpad2_0517_1435_norm ./log/ranpad2_0517_1435_norm.log
for target in names:
	cmd = "./run_attack.sh " + target + " ./log/"+ target + ".log"
	# print(cmd)
	subprocess.call(cmd, shell =True)
