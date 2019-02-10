
# extract features
# 1 train 2 test 3logfile
python2.7 fextractor.py $1 -mode train
python2.7 fextractor.py $2 -mode test

#genlist
python2.7 gen-list.py ./options-kNN.txt $1 $2
# compile attack
g++ flearner-head.cpp -o flearner-head

# run attack
./flearner-head ./options-kNN.txt $1 $2 >> $3


