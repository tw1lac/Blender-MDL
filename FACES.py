from .BaseHandler import BaseHandler
from .__init__ import dbg


# This handler imports the faces inside a Geoset block.
class FACES(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		# Faces is a strange construction. grps is the number of data blocks,
		# cnt the total amount of vertex indices.
		grps, cnt = [int(n) for n in cargo['last'].strip().split()[1:3]]
		li = []
		while len(li) < cnt:
			cargo['last'] = current = self.parent.infile.readline()
			if current.strip().startswith('Triangles'):
				for i in range(grps):
					li += [int(n) for n in self.parent.infile.readline().strip().strip('{},;').split(', ')]
		if dbg: print(len(li))
		for i in range(cnt//3): # from what I remember this was previously adding a face for every vertex, plus an extra every 4th time.
			self.parent.mgr.append([li[3*i], li[3*i+1], li[3*i+2]], 'faces')
		return 'GEOSET', cargo
