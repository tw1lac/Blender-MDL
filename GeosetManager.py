# Our geosets are managed by this class
class GeosetManager:
	def __init__(self):
		self.vertices = [[]]
		self.normals = [[]]
		self.tvertices = [[]]
		self.faces = [[]]
		self.groups = [[]]
		self.vgroups = [[]]
		self.cnt = 0
		self.add_new = False

	def new_geoset(self):
		self.vertices.append([])
		self.normals.append([])
		self.tvertices.append([])
		self.faces.append([])
		self.groups.append([])
		self.vgroups.append([])
		self.cnt += 1
		self.add_new = False

	# @param li: List of data to be added to our geoset.
	# @param cont: Type of the data to be added. One of 'vertices', 'normals',
	# 'tvertices' and 'faces'.
	def append(self, li, cont):
		if cont == 'vertices':
			self.vertices[self.cnt].append(li)
		elif cont == 'normals':
			self.normals[self.cnt].append(li)
		elif cont == 'tvertices':
			self.tvertices[self.cnt].append(li)
		elif cont == 'groups':
			self.groups[self.cnt].append(li)
		elif cont == 'vgroup':
			self.vgroups[self.cnt].append(li)
		elif cont == 'faces':
			self.faces[self.cnt].append(li)
			self.add_new = True

	# @param li: List of data to be added to our geoset.
	# @param cont: Type of the data to be added. One of 'vertices', 'normals',
	# 'tvertices' and 'faces'.
	def extend(self, li, cont):
		if cont == 'vertices':
			self.vertices[self.cnt].extend(li)
		elif cont == 'normals':
			self.normals[self.cnt].extend(li)
		elif cont == 'tvertices':
			self.tvertices[self.cnt].extend(li)
		elif cont == 'groups':
			self.groups[self.cnt].extend(li)
		elif cont == 'vgroup':
			self.vgroups[self.cnt].extend(li)
		elif cont == 'faces':
			self.faces[self.cnt].extend(li)
			self.add_new = True