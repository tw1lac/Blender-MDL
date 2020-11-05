from .BaseHandler import BaseHandler


#This handles the bones, probably
class BONE(BaseHandler):
	def run(self, cargo):
		next, cargo = BaseHandler.run(self, cargo)
		# Store bone name
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
			# For now I just want to be able to import bones. We'll worry about animations later.
			if key == 'ObjectId':
				skel[index]['id'] = int(current.strip().split()[1].strip(','))
			elif key == 'Parent':
				skel[index]['parent'] = int(current.strip().split()[1].strip(','))
			elif key == 'GeosetId':
				try:
					skel[index]['gid'] = int(current.strip().split()[1].strip(','))
				except:
					skel[index]['gid'] = -1

		return next, cargo
