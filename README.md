# Website Fingerprinting attack and defense codes. 
## Folder structure
    .
    ├── attacks  #Wf attacks                     
        ├── kfingerprinting: kFP using Random Forest 
        ├── cumul : CUMUL using SVM
        ├── knn: kNN using k Nearest Neighbor  
        ├── decision: Split decision using Random Forest (Used for evaluating Glue) 
        ├── xgboost: Split finding using xgboost (Used for evaluating Glue) 
        ├── split: Cut l-traces according to result from split finding (Used for evaluating Glue) 
        ├── after-split-attack: customized kNN codes for evaluating Glue
        └── random_attack.py: analyze the result from split decision + finding + WF attack 
    ├── defenses  #WF defenses 
        ├── wtfpad: WTF-PAD defense
        ├── front: FRONT defense
        ├── glue: Glue defense
        └── results: a folder to generate datasets defended by one of the defenses      
    ├── utils    #some useful tools
        ├── overhead.py: calculate the mean data overhead of front or/and glue (glue noise use +-888 as direction; front noise +-999)
        ├── norm.py: generate a normalized dataset, turning +-888, +-999 to +-1. This is for further evaluation using WF attacks. The rule is that directions are +-1.
        └── rmnoise.py: get clean dataset from noisy dataset. (rm +-999, +-888 packets)         
    └── README.md

## Running examples

To run defenses, go to a defense folder.
To run attacks, go to an attack folder.

### Run FRONT

FRONT takes in a dataset folder, output a defended dataset into "defenses/results/" folder 
```
python3 main.py ../../data/tor/
```
This generates a dataset into results/ folder using FRONT defense.

```
python3 mp-main.py ../results/glued_trace/ -format ".merge"
```
This adds front noise to l-traces defended by Glue

### Run Glue
```
python3 main.py ../../data/tor2-5-1/ -n 4000 -b 1 -m 2 -noise True -mode fix
```
n: number of l-traces; m: l; b: base rate; noise: add noise or not; 
mode: fix -> all traces are m length; random -> length is randomly chosen from (2, m)

Generate 4000 noisy 2-traces with base rate 1   


## Run kFP or CUMUL attack
Go to an attack folder

To evaluate FRONT, 
First extract features
```
python3 extract.py ../../defense/results/xxx/
```
Then 
```
python3 new_main.py(or main.py) ./results/test.npy 
```
This will generate results of a 10 cross validation result. 

To evaluate Glue,
Use mp-extract.py to extract features, it will generate features for the first page and the other pages seperately (since they need to be evaluated using two WF models).
Then
```
python3 evaluate.py -m a-saved-model.pkl -o leaf.npy(needed for kFP)/training_data.npy(needed for cumul) -p ./results/test.npy
```

random-evaluate.py is used under split with decision scenario. used together with random_attack.py.

## Run kNN
```
./run_attack.sh data_folder log_dir
```

## Run kNN on glue
cd after-split-attack, mp-kNN contains customized kNN for split finding case; randomkNN2 contains customized kNN for split decision + finding case

For example, cd mp-kNN, run
```
./run_attack_head.sh train_folder test_folder log_dir
```
This evaluate the first split webpages.
```
./run_attack_other.sh train_folder test_folder log_dir
```
This evaluate the other split webpages.

## Split decision 
Go to "attacks/decision" 
```
python3 run_attack.py -train trainset -test testset -num l
```
This corresponds to split decision process.       
It will generate a ".npy" file telling the prediction of l of all l-traces in testset.       
"-num" indicates this testset contains traces of length l.       
trainset contains l-traces of different l; testset only contains traces of the same l.         




## Versioning

For most of the codes, they use Python3 as default. Except for kNN codes. 

## Authors
---


## Acknowledgments
Some of the codes are based on the following works. We thank respective authors for being kind to share their code:  
[1] Wang et al., "Effective Attacks and Provable Defenses for Website Fingerprinting": https://www.cse.ust.hk/~taow/wf/  
[2] Juarez et al., "Toward an Efficient Website Fingerprinting Defense": https://github.com/wtfpad/wtfpad       
[3] Hayes and Danezis, "k-fingerprinting: a Robust Scalable Website Fingerprinting Technique": https://github.com/jhayes14/k-FP      

