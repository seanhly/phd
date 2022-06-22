#!/usr/bin/python3
from actions import Action
from cloud.server.Pool import Pool
from cloud.vendors.Vultr import Vultr
from constants import INPUT_DIR
from os import environ, listdir, makedirs
from os.path import join, exists
from parse_dynamic_argument import parse_dynamic_argument
from typing import Optional, Type
from urllib import request as request
import grobid_tei_xml
import subprocess
import sys

WINDOW_TITLE = "Docmuch search…"

action = sys.argv[1]
args = sys.argv[2:]
arguments = [
	parse_dynamic_argument(arg, action)
	for arg in args
]
FoundAction: Optional[Type[Action]] = None
for T in Action.__subclasses__():
	if action == T.command():
		FoundAction = T
		break
if FoundAction:
	FoundAction(arguments).execute()
	exit_code = 0
else:
	sys.stderr.write(f"unknown sub-command: {action}\n")
	exit_code = 1
sys.exit(exit_code)


files = listdir(INPUT_DIR)
sys.exit(0)
print(files)
for file in files:
	path = join(INPUT_DIR, file)
	tei_str = subprocess.check_output(
		[
			"/usr/bin/curl", "-s", "--form", f"input=@\"{path}\"", "-X", "POST",
			"http://127.0.0.1:8070/api/processFulltextDocument"
		],
		stderr=subprocess.DEVNULL
	).decode()
	tei = grobid_tei_xml.parse_document_xml(tei_str).to_dict()
	print(tei)

for instance in Vultr.list_instances(label="phd"):
	instance.destroy()
instances = [
	Vultr.create_instance()
	for i in range(20)
]
a = Vultr.create_instance()
b = Vultr.create_instance()
print([a, b])
print(str(a))
print(str(b))
