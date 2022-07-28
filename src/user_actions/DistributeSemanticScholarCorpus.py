from subprocess import Popen
from typing import Dict, List, Optional, Set, Tuple
from user_actions.UserAction import UserAction
from os.path import exists, realpath, getsize, basename, join, dirname
from sys import stderr, exit
from data.SemanticScholarArticle import SemanticScholarArticle
from os import chdir, makedirs, walk, stat, rmdir
import re
from cloud.vendors.Vultr import Vultr
from util.rsync import rsync_to
from util.scp import scp
from util.used_and_available_disk import used_and_available_disk
import gzip
import io
from constants import PHD_VAR
from util.ssh_do import ssh_do
from shutil import move

from worker_actions.SemanticScholarData import SemanticScholarData
from worker_actions.SemanticScholarMetadata import SemanticScholarMetadata

SS_DATA = SemanticScholarData.queue_name()
SS_METADATA = SemanticScholarMetadata.queue_name()

def get_gzip_decompressed_size(path):
	with gzip.open(path, 'rb') as file_obj:
		return file_obj.seek(0, io.SEEK_END)

class DistributeSemanticScholarCorpus(UserAction):
	@classmethod
	def command(cls) -> str:
		return "ss"

	@classmethod
	def description(cls):
		#return "Parse JSON data from semantic scholar's 'full paper' corpus."
		return "Distribute the Semantic Scholar corpus' files around the worker network"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		if not self.query:
			path = "."
		else:
			path = self.query.strip()
		if exists(path):
			path = realpath(path)
		else:
			stderr.write(f"directory does not exist: {path}\n")
			exit(1)
		chdir(path)
		# [[File size]], [[path]], [[is metadata?]]
		files: List[Tuple[int, str, bool]] = []
		total_decompressed_space_requirement = 0
		total_metadata_files = 0
		total_data_files = 0
		min_metadata_compression_ratio = 1
		min_data_compression_ratio = 1
		metadata_compression_ratio_found = False
		data_compression_ratio_found = False
		total_compressed_metadata_space = 0
		total_compressed_data_space = 0
		bytes_per_device: Dict[int, int] = {}
		device_roots: Dict[int, str] = {}
		detected_metadata_dir: Optional[str] = None
		detected_data_dir: Optional[str] = None
		for root, _, candidates in walk(".", topdown = False):
			for file in candidates:
				if file.endswith(".jsonl.gz"):
					file_path = realpath(join(root, file))
					m = re.match(
						".*/(pdf_parses|metadata)/(pdf_parses|metadata)_[0-9]+\.jsonl\.gz",
						file_path,
					)
					if m:
						compressed_size = getsize(file_path)
						device_id = stat(file_path).st_dev
						bytes_per_device[device_id] = bytes_per_device.get(device_id, 0) + compressed_size
						if device_id not in device_roots:
							device_id = stat(file_path).st_dev
							eventual_device_root = file_path
							while True:
								candidate_device_path = "/".join(eventual_device_root.split("/")[:-1])
								if not candidate_device_path:
									if stat("/").st_dev == device_id:
										device_roots[device_id] = "/"
									else:
										device_roots[device_id] = eventual_device_root
									break
								elif stat(candidate_device_path).st_dev == device_id:
									eventual_device_root = candidate_device_path
								else:
									device_roots[device_id] = eventual_device_root
									break
						if m[1] == "metadata":
							if not detected_metadata_dir:
								detected_metadata_dir = dirname(file_path)
							total_compressed_metadata_space += compressed_size
							total_metadata_files += 1
							files.append((compressed_size, file_path, True))
							if not metadata_compression_ratio_found:
								decompressed_space_requirement = get_gzip_decompressed_size(file_path)
								ratio = compressed_size / decompressed_space_requirement
								if ratio < min_metadata_compression_ratio:
									metadata_compression_ratio_found = min_metadata_compression_ratio - ratio < 0.001
									print("%.10f" % abs(ratio - min_metadata_compression_ratio))
									min_metadata_compression_ratio = ratio
								print(min_metadata_compression_ratio, file_path)
						elif m[1] == "pdf_parses":
							if not detected_data_dir:
								detected_data_dir = dirname(file_path)
							total_compressed_data_space += compressed_size
							total_data_files += 1
							files.append((compressed_size, file_path, False))
							if not data_compression_ratio_found:
								decompressed_space_requirement = get_gzip_decompressed_size(file_path)
								ratio = compressed_size / decompressed_space_requirement
								if ratio < min_data_compression_ratio:
									data_compression_ratio_found = min_data_compression_ratio - ratio < 0.001
									print("%.10f" % abs(ratio - min_data_compression_ratio))
									min_data_compression_ratio = ratio
								print(min_data_compression_ratio, file_path)
		total_decompressed_space_requirement = (
			total_compressed_metadata_space / min_metadata_compression_ratio
			+
			total_compressed_data_space / min_data_compression_ratio
		)
		total_compressed_space_requirement = (
			total_compressed_metadata_space
			+
			total_compressed_data_space
		)
		files.sort(key=lambda k: -k[0])
		instances = Vultr.list_instances()
		disk_per_ip = used_and_available_disk(i.main_ip for i in instances)
		available_disk_workers: List[Tuple[int, str]] = []
		for i in instances:
			used, available = disk_per_ip[i.main_ip]
			available_disk_workers.append((available, i.main_ip))
		available_disk_workers.sort(key=lambda k: -k[0])
		i = 0
		who_gets_what: Dict[str, List[Tuple[str, bool]]] = {}
		for size, file, is_metadata in files:
			available_disk, worker = available_disk_workers[0]
			who_gets_what[worker] = who_gets_what.get(worker, []) + [(file, is_metadata)]
			available_disk_workers[0] = (
				available_disk - size,
				worker,
			)
			available_disk_workers.sort(key=lambda k: -k[0])
		worker_bytes = {w: b for b, w in available_disk_workers}
		print(available_disk_workers)
		threads: List[Popen] = []
		for thread in threads:
			thread.wait()
		threads.clear()
		metadata_files_per_ip: Dict[str, List[str]] = {}
		data_files_per_ip: Dict[str, List[str]] = {}
		threads: List[Popen] = []
		best_location_for_rsync_src = device_roots[
			sorted(
				(b, device) for device, b in bytes_per_device.items()
			)[-1][1]
		]
		rsync_src_dir = join(best_location_for_rsync_src, "__PHD_TMP__")
		print(rsync_src_dir)
		# Move files to new locations, then rsync them to the workers.
		for ip, lst in who_gets_what.items():
			bytes_remaining_after_copy = worker_bytes[ip]
			print(ip, bytes_remaining_after_copy / ((2 ** 10) ** 3))
			data_files: List[str] = []
			metadata_files: List[str] = []
			for file, is_metadata in lst:
				#file_id = int(basename(file).split(".", 1)[0].split("_")[-1])
				if is_metadata:
					metadata_files.append(file)
				else:
					data_files.append(file)
			metadata_files_per_ip[ip] = metadata_files
			data_files_per_ip[ip] = data_files
			rsync_src_dir_for_ip = join(rsync_src_dir, ip, "queues")

			outgoing_ss_data_for_ip = join(rsync_src_dir_for_ip, SS_DATA)
			outgoing_ss_metadata_for_ip = join(rsync_src_dir_for_ip, SS_METADATA)
			if not exists(outgoing_ss_data_for_ip):
				makedirs(outgoing_ss_data_for_ip)
			if not exists(outgoing_ss_metadata_for_ip):
				makedirs(outgoing_ss_metadata_for_ip)
			for metadata_file in metadata_files:
				move(metadata_file, outgoing_ss_metadata_for_ip)
			for data_file in data_files:
				move(data_file, outgoing_ss_data_for_ip)
			# rsync rsync_src_dir to host: ip /var/phd/queues/
			rsync_to(rsync_src_dir_for_ip, ip, PHD_VAR, threads)
		for thread in threads:
			thread.wait()
		threads.clear()
		# Move files back to original locations.
		for ip, lst in who_gets_what.items():
			data_files: List[str] = []
			metadata_files: List[str] = []
			for file, is_metadata in lst:
				if is_metadata:
					metadata_files.append(file)
				else:
					data_files.append(file)
			metadata_files_per_ip[ip] = metadata_files
			data_files_per_ip[ip] = data_files
			rsync_src_dir_for_ip = join(rsync_src_dir, ip, "queues")
			outgoing_ss_data_for_ip = join(rsync_src_dir_for_ip, SS_DATA)
			outgoing_ss_metadata_for_ip = join(rsync_src_dir_for_ip, SS_METADATA)
			for metadata_file in metadata_files:
				move(join(outgoing_ss_metadata_for_ip, basename(metadata_file)), metadata_file)
			rmdir(outgoing_ss_metadata_for_ip)
			for data_file in data_files:
				move(join(outgoing_ss_data_for_ip, basename(data_file)), data_file)
			rmdir(outgoing_ss_data_for_ip)
			rmdir(rsync_src_dir_for_ip)
			rmdir(join(rsync_src_dir, ip))
			rmdir(rsync_src_dir)
		for size, file in available_disk_workers:
			print(size, file, sep="\t")
		print(
			"\t%.2f GB decompressed %.2f GB compressed (across %d files)" % (
				total_decompressed_space_requirement / ((2 ** 10) ** 3),
				total_compressed_space_requirement / ((2 ** 10) ** 3),
				total_data_files + total_metadata_files,
			)
		)
		#with open(path, "r") as f:
		#for line in f:
		#ssa = SemanticScholarArticle(line)
		#print(ssa)