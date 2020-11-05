# This is our abstract state machine
class StateMachine:

# @param handlers: Dictionary containing name => function pairs
# @param startState: The first state to call when starting
# @param endStates: State machine will end execution on these
	def __init__(self, parent, handlers={}, startState=None, endStates=[]):
		self.parent = parent
		self.handlers = handlers
		self.startState = startState
		self.endStates = endStates

# @param name: The name of the state to add
# @param handler: A function to handle the state
# @param endState: Bool whether this should be added to endStates
# @param startState: Bool whether this should be set as startState
	def add(self, name, handler, endState=False, startState=False):
		name = name.upper()
		if handler:
			self.handlers[name] = handler(self.parent)
		if endState:
			self.endStates.append(name)
			print(self.endStates)
		if startState:
			self.startState = name

# @param name: Name of the state which shall be set as startState
	def set_start(self, name):
		name = name.upper()
		if name in self.handlers:
			self.startState = name
		else:
			raise Exception("Error: set_start(): Unknown state: {}".format(name))

# @param cargo: Some kind of information to carry through the states
	def run(self, cargo={}):
		handler = self.handlers.get(self.startState)
		if not handler:
			raise Exception("InitError: Set startState before calling StateMachine.run()")
		if not self.endStates:
			raise Exception("InitError: There must be at least one endstate")

		while True:
			newState, cargo = handler.run(cargo)
			if newState.upper() in self.endStates:
				break
			else:
				handler = self.handlers[newState.upper()]