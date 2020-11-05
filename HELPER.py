from .BaseHandler import BaseHandler


#This handles helpers which seem to be used as dummy/parent bones
class HELPER(BaseHandler):
	def run(self, cargo):
		next, cargo = BaseHandler.run(self, cargo)
		# Store helper name. Mainly reused from BONE handler.
		skel = self.parent.skel_info
		index = len(skel)
		skel.append({})
		skel[index]['bone_name'] = cargo['last'].split()[1].strip('\"')

		# Brace counting
		cargo['p'] = 1
		while cargo['p'] > 0:
			current = self.parent.infile.readline()
			current = current.strip()
			# Count the braces to find out when the Bone block ends.
			if '{' in current: cargo['p'] += 1
			if '}' in current: cargo['p'] -= 1

			key = current.strip().split()[0]
			# Definitely has an ID, can have a parent.
			if key == 'ObjectId':
				skel[index]['id'] = int(current.strip().split()[1].strip(','))
			elif key == 'Parent':
				skel[index]['parent'] = int(current.strip().split()[1].strip(','))
		return next, cargo
