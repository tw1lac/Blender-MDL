from .BaseHandler import BaseHandler


# This is our main handler.
class SEARCH(BaseHandler):
	def run(self, cargo):
		newState, cargo = BaseHandler.run(self, cargo)

		while True:
			cargo['last'] = current = self.parent.infile.readline()
			# Stop when end of the file is reached.
			if current == '' :
				newState = 'EOF'
				break
			# Skip comments.
			elif current.strip().startswith('//'):
				continue
			# If the line starts with a keyword from DataImporter.globalkeys,
			# start the appropiate handler.
			elif current.strip().split()[0] in self.parent.globalkeys:
				newState = current.strip().split()[0].upper()
				break

		return newState, cargo
