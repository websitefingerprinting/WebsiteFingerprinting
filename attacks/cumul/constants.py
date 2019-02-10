from os.path import join, abspath, dirname, pardir

# Directories
BASE_DIR = abspath(join(dirname(__file__), pardir))
outputdir = join(BASE_DIR, 'cumul/results/')
randomdir = join(BASE_DIR, 'cumul/randomresults/')
logdir = join(BASE_DIR,'cumul/')
# Files
confdir = join(BASE_DIR, 'conf.ini')

# Logging format
LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"

# Characters
CSV_SEP = ';'
TRACE_SEP = '\t'
NL = '\n'  # new line

# MPU
TOR_CELL_SIZE           = 512
MTU                     = 1

