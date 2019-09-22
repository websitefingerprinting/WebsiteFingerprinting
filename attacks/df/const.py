from os.path import join, abspath, dirname, pardir
BASE_DIR = abspath(join(dirname(__file__), pardir))
confdir = join(BASE_DIR,'conf.ini')
outputdir = join(BASE_DIR, 'df/results/')
modeldir = join(BASE_DIR, 'df/models/')
randomdir = join(BASE_DIR, 'df/randomresults/')
LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"