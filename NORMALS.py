from .BaseHandler import BaseHandler


# This handler imports the vertex normals.
class NORMALS(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		# Get the number of normals inside this Normals block.
		for i in range(int(cargo['last'].strip().split()[1])):
			current = self.parent.infile.readline().strip().strip('{},;')
			li = [float(n) for n in current.split(', ')]
			self.parent.mgr.extend(li, 'normals')
		return 'GEOSET', cargo
