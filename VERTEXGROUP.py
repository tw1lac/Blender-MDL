from .BaseHandler import BaseHandler


# This handler imports the vertex group assignment for each vertex.
class VERTEXGROUP(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		li = []
		while True:
			current = self.parent.infile.readline()
			if '}' in current: break
			current = current.strip().strip(',')
			li = int(current)
			self.parent.mgr.append(li, 'vgroup')
		return 'GEOSET', cargo
