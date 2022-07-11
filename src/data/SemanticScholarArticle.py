from typing import Dict, List, Optional, Tuple
from JSON import JSON
from textwrap import wrap, indent, fill
import re

INDENT = "     "


class Author:
	last: Optional[str]
	first: Optional[str]
	middle: List[str]
	suffix: Optional[str]

	def __init__(self, author):
		self.first = author["first"] if author["first"] else None
		self.last = author["last"] if author["last"] else None
		self.middle = author["middle"]
		self.suffix = (
			author["suffix"]
			if author["suffix"]
			else None
		)

	def __str__(self):
		if not self.last:
			return ""
		name_parts = (self.last, self.suffix, self.first, *self.middle)
		return ', '.join(n for n in name_parts if n)


class Citation:
	title: str
	link: Optional[int]
	venue: Optional[str]
	year: Optional[int]
	authors: List[Author]

	def __init__(self, citation):
		self.title = citation["title"]
		self.authors = [
			Author(a)
			for a in citation["authors"]
		]
		self.year = (
			int(citation["year"])
			if citation["year"]
			else None
		)
		self.venue = citation["venue"]
		self.link = (
			int(citation["link"])
			if citation["link"]
			else None
		)

	def __str__(self):
		if self.link:
			s = f"[[{self.link}]]"
		else:
			authors = ", ".join(str(a) for a in self.authors)
			if self.year:
				authors_and_year = f"{authors} ({self.year})"
			else:
				authors_and_year = authors
			authors_year_and_title = f"{authors_and_year}.  {self.title}."
			if self.venue:
				s = f"{authors_year_and_title}  {self.venue}."
			else:
				s = authors_year_and_title
			s = re.sub("^[ .]+", "", s).strip()
		return indent(fill(s), prefix=INDENT)


class ReferenceSpan:
	ref: int
	start: int
	end: int
	text: str
	citation: bool

	def __init__(self, span, ref_id_map, cite_id_map) -> None:
		self.text = span["text"]
		self.start = span["start"]
		self.end = span["end"]
		ref_id = span["ref_id"]
		self.citation = ref_id in cite_id_map
		if self.citation:
			self.ref = cite_id_map[ref_id]
		else:
			self.ref = ref_id_map[ref_id]


class Paragraph:
	cite_spans: List[ReferenceSpan]
	ref_spans: List[ReferenceSpan]
	text: str

	def __init__(self, paragraph, ref_id_map, cite_id_map):
		self.text = paragraph["text"]
		self.cite_spans = [
			ReferenceSpan(cs, ref_id_map, cite_id_map)
			for cs in paragraph["cite_spans"]
		]
		self.ref_spans = [
			ReferenceSpan(rs, ref_id_map, cite_id_map)
			for rs in paragraph["ref_spans"]
		]


class Section:
	title: str
	paragraphs: List[Paragraph]

	def __init__(self, paragraphs, ref_id_map, cite_id_map) -> None:
		self.paragraphs = [
			Paragraph(p, ref_id_map, cite_id_map)
			for p in paragraphs
		]
		self.title = paragraphs[0]["section"]


class SemanticScholarArticle:
	id: int
	pdf_hash: str
	abstract: Optional[Section]
	sections: List[Section]
	refs: Dict[int, Tuple[str, str]]
	citations: Dict[int, Citation]

	def __init__(self, line: str) -> None:
		j = JSON.loads(line)
		self.id = int(j["paper_id"])
		self.pdf_hash = j["_pdf_hash"]
		reference = 1
		self.refs = {}
		self.ref_types = {}
		ref_id_map: Dict[str, int] = {}
		for k, v in j["ref_entries"].items():
			self.refs[reference] = (v["text"], v["type"])
			ref_id_map[k] = reference
			reference += 1
		self.citations = {}
		cite_id_map: Dict[str, int] = {}
		citation = 1
		for k, v in j["bib_entries"].items():
			self.citations[citation] = Citation(v)
			cite_id_map[k] = citation
			citation += 1
		self.abstract = (
			Section(j["abstract"], ref_id_map, cite_id_map)
			if j["abstract"]
			else None
		)
		self.sections = []
		current_section: str = None
		for p in j["body_text"]:
			section = p["section"]
			if section == current_section:
				section = self.sections[-1]
				section.paragraphs.append(Paragraph(p, ref_id_map, cite_id_map))
			else:
				current_section = section
				self.sections.append(Section([p], ref_id_map, cite_id_map))
	
	def __str__(self) -> str:
		s = f"{self.pdf_hash} ({self.id})"
		if self.abstract:
			for p in self.abstract.paragraphs:
				snippet_lines = wrap(p.text)[:3]
				snippet = "\n".join(snippet_lines)
				ptext = indent(
					prefix=INDENT,
					text=snippet,
				)
				s = f"{s}\n\n{ptext} ..."
		if self.sections:
			s = f"{s}\n{INDENT}---"
			for section in self.sections:
				s = f"{s}\n\n{INDENT}## {section.title}"
				for p in section.paragraphs:
					snippet_lines = wrap(p.text)[:3]
					snippet = "\n".join(snippet_lines)
					ptext = indent(
						prefix=INDENT * 2,
						text=snippet,
					)
					s = f"{s}\n\n{ptext} ..."
		if self.citations:
			for i in sorted(self.citations.keys()):
				c = self.citations[i]
				n = f"[{i}] "
				s = f"{s}\n{n}{str(c)[len(n):]}"
		return s