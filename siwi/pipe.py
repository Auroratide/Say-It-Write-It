from typing import TypeVar, Generic, Any
import threading

TIn = TypeVar("TIn")
TOut = TypeVar("TOut")

class Pipe(Generic[TIn, TOut]):
	def __init__(self):
		self._pipes: list[Pipe[TOut, Any]] = []

	def pipe(self, receiver: "Pipe[TOut, Any]"):
		self._pipes.append(receiver)
		return receiver
	
	def send(self, data: TOut):
		threads = [threading.Thread(target=r.receive, args=(data,)) for r in self._pipes]
		for t in threads:
			t.start()

	def receive(self, data: TIn):
		pass
