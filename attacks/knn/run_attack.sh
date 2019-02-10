#!/bin/bash

# This code scripts and parametrizes the k-NN attack.

#ABS_PATH=`cd "$1"; pwd`


#pushd `dirname $0` > /dev/null

# reset batch
# mkdir -p output
# rm -rf output/*

# extract features
python2.7 fextractor.py ./options-kNN.txt $1

#genlist
for i in {0..9}
do
	python2.7 gen-list.py ./options-kNN.txt $i $1>> $2

	# compile attack
	g++ flearner.cpp -o flearner

	# run attack
	./flearner ./options-kNN.txt $1>> $2
done

# print accuracy
# echo "Accuracy (plus/minus 1% variance):"
# cat accuracy
# popd > /dev/null
