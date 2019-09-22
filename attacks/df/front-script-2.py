import subprocess
from os.path import join

names= [
"ranpad2_0527_1053_norm",
"ranpad2_0527_1054_norm",
"ranpad2_0527_1055_norm",
"ranpad2_0527_1056_norm",
"ranpad2_0527_1057_norm",
"ranpad2_0527_1058_norm",
]



for target in names:
	target  = "results/"+target+".npy"
	cmd = "python3.6 2-main.py " + target
	# print(cmd)
	subprocess.call(cmd, shell =True)
