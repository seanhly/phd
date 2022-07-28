from os.path import join, exists
from os import environ, makedirs

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
PHD_VAR = "/var/phd"
if not exists(PHD_VAR):
	makedirs(PHD_VAR)
PHD_POOL = join(HOME, ".phd_pool.json")
PHD_NEAREST_SERVER = join(HOME, ".phd_nearest")
PHD_TOKEN_PATH = join(HOME, ".phd_token")
PHD_PRIVATE_RSA_KEY = join(HOME, ".phd_rsa")
PHD_PUBLIC_RSA_KEY = f"{PHD_PRIVATE_RSA_KEY}.pub"
PHD_TOKEN = ""
if exists(PHD_TOKEN_PATH):
	with open(PHD_TOKEN_PATH, "r") as f:
		PHD_TOKEN = f.read().strip()

PHD_LABEL = "phd"
EXECUTABLE = f"/usr/bin/{PHD_LABEL}"

REDIS_WORKER_NETWORK_DB = 0
REDIS_WORK_QUEUES_DB = 1
GIT_BINARY = "/usr/bin/git"
INSTALL_SCRIPT = "install.sh"
INSTALL_SCRIPT_URL = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/master/{INSTALL_SCRIPT}"
BOOTSTRAP_SCRIPT = f"sh -c \"$(wget {INSTALL_SCRIPT_URL} -O -)\""

COCKROACH_INSTALL_URL = "https://binaries.cockroachdb.com/cockroach-v22.1.4.linux-amd64.tgz"
COCKROACH_BINARY_NAME = "cockroach"
COCKROACH_BINARY = join("/usr/local/bin", COCKROACH_BINARY_NAME)
COCKROACH_PORT = 26257
COCKROACH_WEB_PORT = 8080

GARAGE_INSTALL_URL = "https://garagehq.deuxfleurs.fr/_releases/v0.7.2.1/x86_64-unknown-linux-musl/garage"
GARAGE_BINARY_NAME = "garage"
GARAGE_BINARY = join("/usr/local/bin", GARAGE_BINARY_NAME)

TMP_DIR = "/tmp"

TMUX_BINARY = "/usr/bin/tmux"
UFW_BINARY = "/usr/sbin/ufw"
RSYNC_BINARY = "/usr/bin/rsync"
APT_GET_BINARY = "/usr/bin/apt-get"
PACMAN_BINARY = "/usr/bin/pacman"
SYSTEMCTL_BINARY = "/usr/bin/systemctl"
SERVICE_BINARY = "/usr/sbin/service"
REDIS_CLI_BINARY = "/usr/bin/redis-cli"

SSH_CLIENT = environ.get("SSH_CLIENT", "127.0.0.1").strip().split()[0]