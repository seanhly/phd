from abc import ABC, abstractmethod
from typing import Iterable, Tuple, Optional


class WorkerAction(ABC):
	@classmethod
	@abstractmethod
	def queue_name(cls) -> str:
		pass

	@classmethod
	def name(cls) -> str:
		first_part, *the_rest = cls.queue_name().split("-")
		return " ".join((first_part.title(), *the_rest))

	@classmethod
	@abstractmethod
	def description(cls) -> str:
		pass

	# Specific code for each action is placed within this method.
	@abstractmethod
	def execute(self) -> Iterable[Tuple["WorkerAction", Iterable[str]]]:
		pass

	@classmethod
	def to_string(cls) -> str:
		return f"{cls.name()} ({cls.description()})"

	@classmethod
	@abstractmethod
	def one_at_a_time(cls) -> bool:
		pass

	@abstractmethod
	def __init__(self, the_input: Optional[bytes]):
		pass
