from worker_actions.WorkerAction import WorkerAction


class DummyWork(WorkerAction):
	page: int

	def __init__(self, the_input: bytes):
		self.page = int(the_input.decode().strip())

	@classmethod
	def queue_name(cls) -> str:
		return "dummy"

	@classmethod
	def description(cls) -> str:
		return "Do some dummy work (for testing)."

	def execute(self):
		return ()

	@classmethod
	def one_at_a_time(cls) -> bool:
		return True
