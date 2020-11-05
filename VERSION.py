from BaseHandler import BaseHandler


# This handler just makes sure that our file has the correct MDL version.
class VERSION(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		if int(self.parent.infile.readline().strip().strip(',').split()[1]) != 800:
			raise Exception("This MDL Version is not supported!")
		return 'SEARCH', cargo