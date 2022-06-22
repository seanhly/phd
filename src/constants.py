from os.path import join
from os import environ

GIT_SOURCE = "https://github.com/seanhly/phd"

GROBID_GIT_SOURCE = "https://github.com/kermitt2/grobid"
GROBID_DIR_NAME = "grobid"
WORKING_DIR = "/tmp"

GROBID_DIR_PATH = join(WORKING_DIR, GROBID_DIR_NAME)
GROBID_EXEC_PATH = join(GROBID_DIR_PATH, "gradlew")

HOME = environ['HOME']
INPUT_DIR = join(HOME, "Code", "phd", "input")
PHD_POOL = join(HOME, ".phd_pool.json")

POOL_LABEL = "phd"
EXECUTABLE = "/usr/bin/phd"