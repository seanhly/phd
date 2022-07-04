from user_actions.UserAction import UserAction
from constants import GROBID_DIR_PATH, GROBID_EXEC_PATH, GROBID_SOURCE, WORKING_DIR
from os import makedirs, walk, chmod
from os.path import exists, join
import subprocess
import zipfile
import io
import requests


class LocalGrobid(UserAction):
	@classmethod
	def command(cls) -> str:
		return "local-grobid"

	@classmethod
	def description(cls):
		return "Run the GROBID server locally"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		if not exists(WORKING_DIR):
			makedirs(WORKING_DIR)
		print("Unzipping GROBID...")
		if not exists(GROBID_EXEC_PATH):
			zipfile.ZipFile(io.BytesIO(requests.get(GROBID_SOURCE).content)).extractall(WORKING_DIR)
		for path, _, files in walk(GROBID_DIR_PATH):
			for file in files:
				file_path = join(path, file)
				chmod(file_path, 0o700)
		print("Running GROBID in tmux...")
		tmux = subprocess.Popen(
			[
				"/usr/bin/tmux",
				"new-session",
				"-d",
				"-s",
				"phd",
				f"/usr/bin/sh {GROBID_EXEC_PATH} run",
			],
			cwd=GROBID_DIR_PATH,
		)
		tmux.wait()