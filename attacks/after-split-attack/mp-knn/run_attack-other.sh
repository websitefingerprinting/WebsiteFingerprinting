
# extract features
# 1 train 2 test 3logfile
python2.7 fextractor.py $1 -mode train
python2.7 fextractor.py $2 -mode test

#genlist
python gen-list.py ./options-kNN.txt $1 $2
# compile attack
g++ flearner-other.cpp -o flearner-other

# run attack
./flearner-other ./options-kNN.txt $1 $2 >> $3


