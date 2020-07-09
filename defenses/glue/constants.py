from os.path import join, abspath, dirname, pardir

# Directories
BASE_DIR = abspath(join(dirname(__file__), pardir))
RESULTS_DIR = join(BASE_DIR, "results")

# Files
CONFIG_FILE = join(BASE_DIR+'/glue', 'config.ini')

# Logging format
LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"

# Characters
CLASS_SEP = '-'
CSV_SEP = ';'
TRACE_SEP = '\t'
NL = '\n'  # new line

# MPU
TOR_CELL_SIZE           = 512
MTU                     = 1

# Directions
IN  = -1
OUT =  1
DIR_NAMES = {IN: "in", OUT: "out"}
DIRECTIONS = [OUT, IN]


