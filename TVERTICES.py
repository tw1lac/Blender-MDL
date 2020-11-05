from BaseHandler import BaseHandler


# This handler imports the texture vertices (aka the UV layout).
class TVERTICES(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		# Get the number of vertices inside this Normals block.
		for i in range(int(cargo['last'].strip().split()[1])):
			current = self.parent.infile.readline().strip().strip('{},:')
			li = [float(n) for n in current.split(', ')]
			self.parent.mgr.append(li, 'tvertices')
		return 'GEOSET', cargo