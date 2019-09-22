import subprocess
from os.path import join

original = "../../defense/results/"
split = "../xgboost/scores/"

targets = [
"mergepad_0609_1221_clean/",
"mergepad_0609_1222_clean/",
"mergepad_0609_1223_clean/",
"mergepad_0609_1224_clean/",
"mergepad_0609_1225_clean/",
"mergepad_0609_1226_clean/",
"mergepad_0609_1227_clean/",
"mergepad_0609_1228_clean/",
"mergepad_0609_1229_clean/",
"mergepad_0609_1230_clean/",
"mergepad_0609_1231_clean/",
"mergepad_0609_1232_clean/",
"mergepad_0609_1233_clean/",
"mergepad_0609_1234_clean/",
"mergepad_0609_1235_clean/",
] 






for target in targets:
	a = join(original, target)
	b = join(split, target, "splitresult.txt")

	cmd = "python3 split-base-rate.py " + a + " -split "+ b
	# print(cmd)
	# exit(0)
	subprocess.call(cmd, shell= True)
