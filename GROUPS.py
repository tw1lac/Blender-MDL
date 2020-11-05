from BaseHandler import BaseHandler


# This is the handler for importing groups matrix data for armature rigging
class GROUPS(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		li = []
		# Run for as many GROUPs as the file claims there are.
		for i in range(int(cargo['last'].strip().split()[1])):
			current = self.parent.infile.readline().strip().strip('},;')
			li = [int(n) for n in current.split('{')[1].split(', ')]
			self.parent.mgr.append(li, 'groups')
		return 'GEOSET', cargo