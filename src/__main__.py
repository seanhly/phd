#!/usr/bin/python3
import subprocess
import sys
from urllib import request as request
from os.path import join, exists
from os import environ, listdir, makedirs
from cloud.server.Pool import Pool
import grobid_tei_xml

from cloud.vendors.Vultr import Vultr
from constants import INPUT_DIR

pool = Pool.load(Vultr)
pool.run_grobid()
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