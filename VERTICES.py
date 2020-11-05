from BaseHandler import BaseHandler


# This handler imports the vertices inside a Geoset block.
class VERTICES(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		# Get the number of vertices inside this Vertices block.
		for i in range(int(cargo['last'].strip().split()[1])):
			current = self.parent.infile.readline().strip().strip('{},;')
			# Divide with 20 to scale the model down.
			li = [(float(n)/20) for n in current.split(', ')] # I need to review these brackets, they may be unneeded mN
			self.parent.mgr.append(li, 'vertices') # I changed this to append since extend was causing troubles at the time? mN
		return 'GEOSET', cargo