from os.path import join, exists
from os import environ

GITHUB_REPOSITORY = "seanhly/phd"
GIT_SOURCE = f"https://github.com/{GITHUB_REPOSITORY}"

GROBID_VERSION = "0.7.1"
GROBID_SOURCE = f"https://github.com/kermitt2/grobid/archive/refs/tags/{GROBID_VERSION}.zip"
GROBID_DIR_NAME = f"grobid-{GROBID_VERSION}"
WORKING_DIR = "/tmp"

GROBID_DIR_PATH = join(WORKING_DIR, GROBID_DIR_NAME)
GROBID_EXEC_PATH = join(GROBID_DIR_PATH, "gradlew")

HOME = environ['HOME']
INPUT_DIR = join(HOME, "Code", "phd", "input")
PHD_POOL = join(HOME, ".phd_pool.json")
PHD_TOKEN_PATH = join(HOME, ".phd_token")
PHD_TOKEN = ""
if exists(PHD_TOKEN_PATH):
	with open(PHD_TOKEN_PATH, "r") as f:
		PHD_TOKEN = f.read().strip()

POOL_LABEL = "phd"
EXECUTABLE = "/usr/bin/phd"

INSTALL_SCRIPT_URL = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/master/install.sh"