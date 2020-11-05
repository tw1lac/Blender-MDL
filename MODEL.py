from .BaseHandler import BaseHandler


# This handles the Model block
class MODEL(BaseHandler):
	def run(self, cargo):
		next, cargo = BaseHandler.run(self, cargo)
		# Store the model's name
		self.parent.model_info['name'] = cargo['last'].split()[1].strip('\"')
		# Count curled braces to stop loop when the block ends
		cargo['p'] = 1
		while cargo['p'] > 0:
			current = self.parent.infile.readline()
			if '{' in current: cargo['p'] += 1
			if '}' in current: cargo['p'] -= 1
			key = current.strip().split()[0]
			# Only two keys are interesting: 'BoundsRadius' & 'BlendTime'
			if key == 'BoundsRadius':
				self.parent.model_info[key] = float(current.strip().split()[1].strip(','))
			elif key == 'BlendTime':
				self.parent.model_info[key] = int(current.strip().split()[1].strip(','))
		return next, cargo
