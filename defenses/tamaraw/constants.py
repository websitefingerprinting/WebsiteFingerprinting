from os.path import join, abspath, dirname, pardir

# Directories
BASE_DIR = abspath(join(dirname(__file__), pardir))
RESULTS_DIR = join(BASE_DIR, "results")

# Files
CONFIG_FILE = join(BASE_DIR+'/tamaraw', 'config.ini')

# Logging format
LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"

