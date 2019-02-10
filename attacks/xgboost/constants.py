from os.path import join, abspath, dirname, pardir

# Directories
BASE_DIR = abspath(join(dirname(__file__), pardir))
outputdir = join(BASE_DIR, 'xgboost/features/')
scoredir = join(BASE_DIR, 'xgboost/scores/')
modeldir = join(BASE_DIR, 'xgboost/models/')
logdir = join(BASE_DIR,'xgboost/')
# Files
confdir = join(BASE_DIR, 'conf.ini')

# Logging format
LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"


