from actions.Action import Action
from constants import GROBID_DIR_PATH, GROBID_EXEC_PATH, GROBID_GIT_SOURCE
from os import makedirs
from os.path import exists
import subprocess


class LocalGrobid(Action):
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
		pipeline = []
		if not exists(GROBID_DIR_PATH):
			makedirs(GROBID_DIR_PATH)
		if not exists(GROBID_EXEC_PATH):
			pipeline.append(f"git clone {GROBID_GIT_SOURCE} .")
		pipeline.append(f"{GROBID_EXEC_PATH} run")
		tmux = subprocess.Popen(
			[
				"/usr/bin/tmux",
				"new-session",
				"-d",
				"-s",
				"phd",
				" && ".join(pipeline)
			],
			cwd=GROBID_DIR_PATH,
		)
		tmux.wait()