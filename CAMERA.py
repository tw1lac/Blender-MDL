from BaseHandler import BaseHandler


# This handles any Camera block (assume one max for now but this should change)
class CAMERA(BaseHandler):
	def run(self, cargo):
		next, cargo = BaseHandler.run(self, cargo)
		# Store camera name
		self.parent.camera_info['name'] = cargo['last'].split()[1].strip('\"')
		# Brace counting
		cargo['p'] = 1
		while cargo['p'] > 0:
			current = self.parent.infile.readline()
			if '{' in current: cargo['p'] += 1
			if '}' in current: cargo['p'] -= 1
			key = current.strip().split()[0]
			if key == 'Position':
				pos_array = []
				for i in range(3):
					pos_array.append(float(current.strip().split()[i+2].strip(','))/20)
				self.parent.camera_info[key] = pos_array
			elif key == 'Target':
				# Advance a line so we can get target data and skip another position read, kind of hacky. This Target is a single-case worker. Needs a fix.
				current = self.parent.infile.readline()
				targ_array = []
				for i in range(3):
					targ_array.append(float(current.strip().split()[i+2].strip(','))/20)
				self.parent.camera_info[key] = targ_array
			elif key == 'Rotation':
				# Advance a line so we can get target data and skip another position read, kind of hacky. Needs a fix.
				current = self.parent.infile.readline()
				rot_array = []
				for i in range(3):
					rot_array.append(float(current.strip().split()[i+2].strip(','))/20)
				self.parent.camera_info[key] = rot_array
			elif key == 'FieldOfView':
				self.parent.camera_info[key] = float(current.strip().split()[1].strip(','))
			elif key == 'FarClip':
				self.parent.camera_info[key] = float(current.strip().split()[1].strip(','))/20
			elif key == 'NearClip':
				self.parent.camera_info[key] = float(current.strip().split()[1].strip(','))/20
		return next, cargo