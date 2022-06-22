from os.path import join
from os import environ

GITHUB_REPOSITORY = "seanhly/phd"
GIT_SOURCE = f"https://github.com/{GITHUB_REPOSITORY}"

GROBID_GIT_SOURCE = "https://github.com/kermitt2/grobid"
GROBID_DIR_NAME = "grobid"
WORKING_DIR = "/tmp"

GROBID_DIR_PATH = join(WORKING_DIR, GROBID_DIR_NAME)
GROBID_EXEC_PATH = join(GROBID_DIR_PATH, "gradlew")

HOME = environ['HOME']
INPUT_DIR = join(HOME, "Code", "phd", "input")
PHD_POOL = join(HOME, ".phd_pool.json")
PHD_TOKEN_PATH = join(HOME, ".phd_token")
PHD_TOKEN = ""
with open(PHD_TOKEN_PATH, "r") as f:
	PHD_TOKEN = f.read().strip()

POOL_LABEL = "phd"
EXECUTABLE = "/usr/bin/phd"

INSTALL_SCRIPT_URL = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/master/install.sh"