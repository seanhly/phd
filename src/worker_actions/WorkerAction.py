from abc import ABC, abstractclassmethod, abstractmethod
from typing import Iterable, Tuple


class WorkerAction(ABC):
	@abstractclassmethod
	def queue_name(cls) -> str:
		pass

	@classmethod
	def name(cls) -> str:
		first_part, *the_rest = cls.command().split("-")
		return " ".join((first_part.title(), *the_rest))

	@abstractclassmethod
	def description(cls) -> str:
		pass

	# Specific code for each action is placed within this method.
	@abstractmethod
	def execute(self) -> Iterable[Tuple["WorkerAction", Iterable[str]]]:
		pass

	@classmethod
	def to_string(cls) -> str:
		return f"{cls.name()} ({cls.description()})"

	@abstractclassmethod
	def one_at_a_time(cls) -> bool:
		pass