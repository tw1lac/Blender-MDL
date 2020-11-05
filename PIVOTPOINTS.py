from .BaseHandler import BaseHandler


# Pivot point handler, which 'might' be the bone positions/origins?
class PIVOTPOINTS(BaseHandler):
	def run(self, cargo):
		next, cargo = BaseHandler.run(self, cargo)
		li = []
		# We're assuming the pivot point order and read in bone order is the same. Hum.
		for i in range(int(cargo['last'].strip().split()[1])):
			current = self.parent.infile.readline().strip().strip('{},;')
			li = [float(n)/20 for n in current.split(', ')]
			try:
				self.parent.skel_info[i]['pivot_point'] = li
			except:
				print("Whoops that's a pivot point past the bones and helpers, I'm not dealing with this yet!")
		return next, cargo
