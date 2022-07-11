from os.path import join, exists
from os import environ
from os import makedirs

GITHUB_REPOSITORY = "seanhly/phd"
GIT_SOURCE = f"https://github.com/{GITHUB_REPOSITORY}"

GROBID_VERSION = "0.7.1"
GROBID_SOURCE = f"https://github.com/kermitt2/grobid/archive/refs/tags/{GROBID_VERSION}.zip"
GROBID_DIR_NAME = f"grobid-{GROBID_VERSION}"
WORKING_DIR = "/root"

GROBID_DIR_PATH = join(WORKING_DIR, GROBID_DIR_NAME)
GROBID_EXEC_PATH = join(GROBID_DIR_PATH, "gradlew")

HOME = environ['HOME']
USER = environ['USER']
INPUT_DIR = join(HOME, "Code", "phd", "input")
PHD_POOL = join(HOME, ".phd_pool.json")
PHD_NEAREST_SERVER = join(HOME, ".phd_nearest")
PHD_TOKEN_PATH = join(HOME, ".phd_token")
PHD_PRIVATE_RSA_KEY = join(HOME, ".phd_rsa")
PHD_QUEUE_DIR = join(HOME, ".phd_queue")
if not exists(PHD_QUEUE_DIR):
	makedirs(PHD_QUEUE_DIR)
PHD_PUBLIC_RSA_KEY = f"{PHD_PRIVATE_RSA_KEY}.pub"
PHD_TOKEN = ""
if exists(PHD_TOKEN_PATH):
	with open(PHD_TOKEN_PATH, "r") as f:
		PHD_TOKEN = f.read().strip()

PHD_LABEL = "phd"
EXECUTABLE = f"/usr/bin/{PHD_LABEL}"

REDIS_WORKER_NETWORK_DB = 0
REDIS_WORK_QUEUES_DB = 1

INSTALL_SCRIPT_URL = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/master/install13.sh"
INSTALL_SCRIPT = f"sh -c \"$(wget {INSTALL_SCRIPT_URL} -O -)\""