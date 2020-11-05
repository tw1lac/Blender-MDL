import pdb

from .BaseHandler import BaseHandler
from .__init__ import dbg


# This handler deals with the content inside a Geoset block.
class GEOSET(BaseHandler):
	def run(self, cargo):
		if dbg: pdb.set_trace()
		if cargo['prev_handler'] == 'SEARCH':
			if self.parent.mgr.add_new:
				self.parent.mgr.new_geoset()
			cargo['p'] = 1

		newState, cargo = BaseHandler.run(self, cargo)

		while cargo['p'] > 0:
			cargo['last'] = current = self.parent.infile.readline()
			current = current.strip()
			# We count the braces to find out when a Geoset block ends.
			if '{' in current: cargo['p'] += 1
			if '}' in current: cargo['p'] -= 1
			# If a line starts with an keyword from DataImporter.geosetkeys,
			# start the appropiate handler.
			if current.split()[0] in self.parent.geosetkeys:
				newState = current.split()[0].upper()
				break

		return newState, cargo
