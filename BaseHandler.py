# All Handlers should be derived from BaseHandler.
# They all have to override the .run() function
# They should always call newState, cargo = BaseHandler.run(cargo)
# before doing anything else.
dbg = False


class BaseHandler:
	def __init__(self, parent):
		self.parent = parent

	def run(self, cargo):
		cargo['prev_handler'] = self.__class__.__name__
		print(cargo['prev_handler'])
		return 'SEARCH', cargo
