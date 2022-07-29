from worker_actions.WorkerAction import WorkerAction


class SemanticScholarData(WorkerAction):
	page: int

	def __init__(self, the_input: bytes):
		self.page = int(the_input.decode().strip())

	@classmethod
	def queue_name(cls) -> str:
		return "semantic-scholar-data"

	@classmethod
	def description(cls) -> str:
		return "Store some semantic scholar data."

	def execute(self):
		return ()

	@classmethod
	def one_at_a_time(cls) -> bool:
		return False
