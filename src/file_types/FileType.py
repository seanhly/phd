from abc import ABC, abstractclassmethod
from typing import Set, Dict, Any

class FileType(ABC):
	@classmethod
	def key(cls) -> str:
		return "file"

	@classmethod
	def view_path(cls, fa: "FileLikeArgument") -> str:
		return fa.as_full_typed_file_path(cls)

	@classmethod
	def view_cmd(cls) -> str:
		return "/usr/bin/xdg-open"

	@classmethod
	def suffixes(cls) -> Set[str]:
		return set()

	@classmethod
	def applies_to_suffix(cls, suffix: str):
		return cls.applies_to_any_suffix({suffix})

	@classmethod
	def applies_to_any_suffix(cls, suffixes: Set[str]):
		return not cls.suffixes() or not suffixes.isdisjoint(cls.suffixes())


	@classmethod
	def applies_to_fa(cls, fa: "FileLikeArgument"):
		return cls.applies_to_any_suffix(fa.as_filetypes())

	@abstractclassmethod
	def get_info(cls, fa: "FileLikeArgument") -> Dict[str, Any]:
		return {}

	@classmethod
	def to_text(cls, fa: "FileLikeArgument") -> str:
		raise ValueError("unimplemented function: FileType.to_text(file)")

	@classmethod
	def required_exif_mappings(cls) -> Dict[str, str]:
		return {
			"File:FileSize": "size",
			"File:FileType": "type",
		}

	@classmethod
	def required_fields(cls):
		return {
			"size",
			"type",
		}

	@classmethod
	def required_info_keys(cls) -> Set[str]:
		return set(cls.required_exif_mappings().values())

	@classmethod
	def non_keys(cls) -> Set[str]:
		return {
			"tei"
		}
	
	@classmethod
	def actions(cls):
		from actions.Open import Open
		from actions.Tag import Tag
		from actions.EditNote import EditNote
		from actions.Print import Print
		from actions.Annotate import Annotate
		from actions.CopyID import CopyID
		from actions.CopyTitle import CopyTitle
		from actions.CopyAuthors import CopyAuthors
		from actions.GoogleScholar import GoogleScholar
		from actions.Untag import Untag
		from actions.Index import Index
		from actions.Parse import Parse
		return [
			Open,
			Tag,
			EditNote,
			Print,
			Annotate,
			CopyID,
			CopyTitle,
			CopyAuthors,
			GoogleScholar,
			Untag,
			Index,
			Parse,
		]
	
	@classmethod
	def for_suffix(cls, suffix: str):
		for ft in FileType.__subclasses__():
			for suffix in ft.suffixes():
				if suffix == suffix:
					return ft

		return None

	@classmethod
	def valid_suffix_pattern(cls):
		from file_types.BIB import BIB
		from file_types.EBook import EBook
		from file_types.Image import Image
		from file_types.ODT import ODT
		from file_types.PDF import PDF
		from file_types.Plaintext import Plaintext
		from file_types.Recipe import Recipe
		from file_types.Song import Song
		from file_types.TEX import TEX
		from file_types.HTML import HTML
		return "\.(?=(?=" + "$|".join([
			suffix
			for ft in FileType.__subclasses__()
			for suffix in ft.suffixes()
		]) + "$))"
