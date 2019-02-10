from os.path import join, abspath, dirname, pardir
BASE_DIR = abspath(join(dirname(__file__), pardir))
confdir = join(BASE_DIR,'conf.ini')
outputdir = join(BASE_DIR, 'decision/results/')
modeldir = join(BASE_DIR, 'decision/models/')
featuredir = join(BASE_DIR, 'decision/features/')
confdir = join(BASE_DIR, 'decision/confs/')
LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"