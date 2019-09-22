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
]



for target in names:
	target  = "results/"+target+".npy"
	cmd = "python3.6 main.py " + target
	# print(cmd)
	subprocess.call(cmd, shell =True)
