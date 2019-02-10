#!/bin/bash

# This code scripts and parametrizes the k-NN attack.

#ABS_PATH=`cd "$1"; pwd`


#pushd `dirname $0` > /dev/null

# reset batch
# mkdir -p output
# rm -rf output/*

# extract features
# 1 train 2 test logfile
python fextractor.py ./options-kNN.txt $1
python fextractor.py ./options-kNN.txt $2

#genlist
for i in {0..0}
do
	python gen-list.py ./options-kNN.txt $1 $2
	# compile attack
	g++ flearner.cpp -o flearner

	# run attack
	./flearner ./options-kNN.txt $1 $2 >> $3
done

# print accuracy
# echo "Accuracy (plus/minus 1% variance):"
# cat accuracy
# popd > /dev/null
