# Copyright (c) 2011 Thomas Glamsch
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

import bpy
import string
import io
import pdb
import time
import math

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

dbg = False

bl_info = {
	"name": "Import WarCraft MDL (.mdl)",
	"description": "This addon allows you to import WarCraft MDL model files (.mdl).",
	"author": "Thomas 'CruzR' Glamsch, Mark Newbery",
	"version": (0, 2, 2),
	"blender": (2, 5, 7),
	#"api": ???,
	"location": "File > Import > WarCraft MDL (.mdl)",
	"warning": "Currently doesn't do animations, assumes max 1 camera, still work in progress.",
	"wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Import-Export/WarCraft_MDL",
	"tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=29552",
	"category": "Import-Export"}

# This is our abstract state machine
class StateMachine:

# @param handlers: Dictionary containing name => function pairs
# @param startState: The first state to call when starting
# @param endStates: State machine will end execution on these
	def __init__(self, parent, handlers={}, startState=None, endStates=[]):
		self.parent = parent
		self.handlers = handlers
		self.startState = startState
		self.endStates = endStates

# @param name: The name of the state to add
# @param handler: A function to handle the state
# @param endState: Bool whether this should be added to endStates
# @param startState: Bool whether this should be set as startState
	def add(self, name, handler, endState=False, startState=False):
		name = name.upper()
		if handler:
			self.handlers[name] = handler(self.parent)
		if endState:
			self.endStates.append(name)
			print(self.endStates)
		if startState:
			self.startState = name

# @param name: Name of the state which shall be set as startState
	def set_start(self, name):
		name = name.upper()
		if name in self.handlers:
			self.startState = name
		else:
			raise Exception("Error: set_start(): Unknown state: {}".format(name))

# @param cargo: Some kind of information to carry through the states
	def run(self, cargo={}):
		handler = self.handlers.get(self.startState)
		if not handler:
			raise Exception("InitError: Set startState before calling StateMachine.run()")
		if not self.endStates:
			raise Exception("InitError: There must be at least one endstate")
		
		while True:
			newState, cargo = handler.run(cargo)
			if newState.upper() in self.endStates:
				break
			else:
				handler = self.handlers[newState.upper()]

# All Handlers should be derived from BaseHandler.
# They all have to override the .run() function
# They should always call newState, cargo = BaseHandler.run(cargo)
# before doing anything else.
class BaseHandler:
	def __init__(self, parent):
		self.parent = parent
	
	def run(self, cargo):
		cargo['prev_handler'] = self.__class__.__name__
		print(cargo['prev_handler'])
		return 'SEARCH', cargo

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

# This is our main handler.
class SEARCH(BaseHandler):
	def run(self, cargo):
		newState, cargo = BaseHandler.run(self, cargo)
		
		while True:
			cargo['last'] = current = self.parent.infile.readline()
			# Stop when end of the file is reached.
			if current == '' :
				newState = 'EOF'
				break
			# Skip comments.
			elif current.strip().startswith('//'):
				continue
			# If the line starts with a keyword from DataImporter.globalkeys,
			# start the appropiate handler.
			elif current.strip().split()[0] in self.parent.globalkeys:
				newState = current.strip().split()[0].upper()
				break
		
		return newState, cargo

# This handler just makes sure that our file has the correct MDL version.
class VERSION(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		if int(self.parent.infile.readline().strip().strip(',').split()[1]) != 800:
			raise Exception("This MDL Version is not supported!")
		return 'SEARCH', cargo

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

# This handler imports the vertices inside a Geoset block.
class VERTICES(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		# Get the number of vertices inside this Vertices block.
		for i in range(int(cargo['last'].strip().split()[1])):
			current = self.parent.infile.readline().strip().strip('{},;')
			# Divide with 20 to scale the model down.
			li = [(float(n)/20) for n in current.split(', ')] # I need to review these brackets, they may be unneeded mN
			self.parent.mgr.append(li, 'vertices') # I changed this to append since extend was causing troubles at the time? mN
		return 'GEOSET', cargo

# This handler imports the vertex normals.
class NORMALS(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		# Get the number of normals inside this Normals block.
		for i in range(int(cargo['last'].strip().split()[1])):
			current = self.parent.infile.readline().strip().strip('{},;')
			li = [float(n) for n in current.split(', ')]
			self.parent.mgr.extend(li, 'normals')
		return 'GEOSET', cargo

# This handler imports the texture vertices (aka the UV layout).
class TVERTICES(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		# Get the number of vertices inside this Normals block.
		for i in range(int(cargo['last'].strip().split()[1])):
			current = self.parent.infile.readline().strip().strip('{},:')
			li = [float(n) for n in current.split(', ')]
			self.parent.mgr.append(li, 'tvertices')
		return 'GEOSET', cargo

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


# This class initiates and starts the state machine and uses the gathered data
# to construct the model in Blender.
class DataImporter:
	infile = None
	globalkeys = ['Version', 'Model', 'Geoset', 'Bone', 'Helper', 'PivotPoints', 'Camera']
	geosetkeys = ['Vertices', 'Normals', 'TVertices', 'Faces', 'VertexGroup', 'Groups']
	mgr = GeosetManager()
	skel_info = []
	model_info = {}
	camera_info = {}
	
	def run(self, filepath, context):
		start_time = time.time()
		print("Opening {}...".format(filepath))
		self.infile = open(filepath, 'r')
		
		# Purge the geoset manager so we don't retain any contents from previous imports this session.
		mgr = GeosetManager()
		skel_info = []
		model_info = {}
		camera_info = {}
		
		m = StateMachine(parent=self)
		m.add('SEARCH', SEARCH, startState=True)
		m.add('VERSION', VERSION)
		m.add('MODEL', MODEL)
		m.add('GEOSET', GEOSET)
		m.add('VERTICES', VERTICES)
		m.add('NORMALS', NORMALS)
		m.add('TVERTICES', TVERTICES)
		m.add('GROUPS', GROUPS)
		m.add('VERTEXGROUP', VERTEXGROUP)
		m.add('FACES', FACES)
		m.add('BONE', BONE)
		m.add('HELPER', HELPER)
		m.add('PIVOTPOINTS', PIVOTPOINTS)
		m.add('CAMERA', CAMERA)
		m.add('EOF', None, endState=True)
		m.run()
		
		if dbg: pdb.set_trace()
		# Construct an own object for each geoset.
		for i in range(self.mgr.cnt + 1):
			# Create an object and link it to the scene.
			mesh = bpy.data.meshes.new("{name}{i}Mesh".format(name=self.model_info['name'], i=i))
			obj = bpy.data.objects.new("{name}{i}".format(name=self.model_info['name'], i=i), mesh)
			obj.location = (0.0, 0.0, 0.0)
			bpy.context.scene.objects.link(obj)
			# Construct the mesh from the gathered vertex and face data.
			VertLength = len(self.mgr.vertices[i])
			FaceLength = len(self.mgr.faces[i])
			mesh.vertices.add(VertLength+1)
			mesh.tessfaces.add(FaceLength)
			for j in range(VertLength):
				mesh.vertices[j].co=self.mgr.vertices[i][j]
				mesh.vertices[VertLength].co=self.mgr.vertices[i][0]
				# Set the normals
				mesh.vertices[j].normal=(self.mgr.normals[i][0],self.mgr.normals[i][1],self.mgr.normals[i][2])
			for j in range(FaceLength):
				NewFace = (self.mgr.faces[i][j][0],self.mgr.faces[i][j][1],self.mgr.faces[i][j][2],0)
				mesh.tessfaces[j].vertices_raw=NewFace
				
			# Create vertex groups
			for j in range(len(self.mgr.groups[i])):
				matr_str = ""
				for s in self.mgr.groups[i][j]:
					matr_str = "%s %s" % (matr_str, self.skel_info[s]['bone_name'])
				vg = obj.vertex_groups.new(matr_str)
				verts = []
				for k in range(len(self.mgr.vgroups[i])):
					if j == int(self.mgr.vgroups[i][k]):
						verts.append(k)
				vg.add(verts, 1.0 / len(self.mgr.groups[i][j]), 'ADD')
				
				
			# Create the UV layout.
			uvtex = mesh.tessface_uv_textures.new(name="uvtex{}".format(i))
			for n, face in enumerate(self.mgr.faces[i]):
				texface = uvtex.data[n]
				texface.uv1 = (self.mgr.tvertices[i][face[0]][0], 1 - self.mgr.tvertices[i][face[0]][1])
				texface.uv2 = (self.mgr.tvertices[i][face[1]][0], 1 - self.mgr.tvertices[i][face[1]][1])
				texface.uv3 = (self.mgr.tvertices[i][face[2]][0], 1 - self.mgr.tvertices[i][face[2]][1])
			# I think there used to be setting of normals here, it might need to be re-included.
			#Update the mesh
			mesh.update()
			
			if dbg: pdb.set_trace()
			# Delete the mesh and obj pointer to make sure we don't override
			# the just created object.
			del mesh
			del obj
			
		#Dem bones
		
		#Make an armature
		armat = bpy.data.armatures.new('skeleton')
		armat_obj = bpy.data.objects.new('skeleton', armat)
		armat_obj.show_x_ray = True
		armat_obj.draw_type = 'WIRE'
		armat.show_names = True
		bpy.context.scene.objects.link(armat_obj)
		bpy.context.scene.objects.active = armat_obj
		#armat_obj.select = True
		
		bpy.ops.object.mode_set(mode='EDIT')
		
		#Create our bones
		for d in self.skel_info:
			bone = armat.edit_bones.new(d['bone_name'])
			bone.head = (d['pivot_point'][0],d['pivot_point'][1],d['pivot_point'][2])
			#if 'parent' in d:
				#bone.tail = (d['pivot_point'][0],d['pivot_point'][1],d['pivot_point'][2])
				#bone.use_connect = True;
			#else:
			bone.tail = (d['pivot_point'][0],d['pivot_point'][1],d['pivot_point'][2] + 0.25)
		
		#Parent them based on id info
		for i in range(len(self.skel_info)):
			for j in range(len(self.skel_info)):
				if i == j: continue
				if 'parent' in self.skel_info[i]:
					if self.skel_info[j]['id'] == self.skel_info[i]['parent']:
							armat.edit_bones[i].parent = armat.edit_bones[j]
					
		
		bpy.ops.object.mode_set(mode='OBJECT')
		
						
		# Create hook modifiers to link armature posing to the mesh/vertex groups.
		for o in bpy.data.objects:
			if o.type == 'MESH':
				geo_index = int(o.name[len(self.model_info['name']):])
				for vg in o.vertex_groups:
					for g in self.mgr.groups[geo_index][vg.index]:
						hook = o.modifiers.new(name="h %s" % (self.mgr.groups[geo_index][vg.index]), type='HOOK')
						hook.object = armat_obj
						hook.subtarget = self.skel_info[g]['bone_name']
						
						bpy.context.scene.objects.active = o
						
						hook.vertex_group = vg.name
						
						bpy.ops.object.mode_set(mode='EDIT')
						
						bpy.ops.mesh.select_all(action='DESELECT')
						bpy.ops.object.vertex_group_set_active(group=vg.name)
						bpy.ops.object.vertex_group_select()
						
						bpy.ops.object.hook_assign(modifier=hook.name)
						bpy.ops.object.hook_reset(modifier=hook.name)
						
						bpy.ops.object.mode_set(mode='OBJECT')
		
		
		
		#Camera creation
		if self.camera_info:
			cam_data = bpy.data.cameras.new(self.camera_info['name'])
			cam_obj = bpy.data.objects.new(self.camera_info['name'], cam_data)
			bpy.context.scene.objects.link(cam_obj)
			cam_obj.location = self.camera_info['Position']
			bpy.context.scene.objects.active = cam_obj
			bpy.context.scene.camera = cam_obj
			
			cam_data.angle = self.camera_info['FieldOfView']
			cam_data.clip_end = self.camera_info['FarClip']
			cam_data.clip_start = self.camera_info['NearClip']
			
			targ_obj = bpy.data.objects.new(self.camera_info['name'] + "Target", object_data=None)
			bpy.context.scene.objects.link(targ_obj)
			targ_obj.location = self.camera_info['Target']
			
			cam_obj.constraints.new("TRACK_TO")
			cam_obj.constraints["Track To"].target=targ_obj
			cam_obj.constraints["Track To"].up_axis='UP_Y'
			cam_obj.constraints["Track To"].track_axis='TRACK_NEGATIVE_Z'
				
			if 'Rotation' in self.camera_info:
				cam_obj.rotation = self.camera_info['Rotation']
				
		
		print("Script finished after {} seconds".format(time.time() - start_time))
		return {'FINISHED'}

# This is the import operator.
class ImportWarMDL(bpy.types.Operator, ImportHelper):
	'''Import from WarCraft MDL model format (.mdl)'''
	bl_idname = "import_mesh.warmdl"
	bl_label = "WarCraft MDL (.mdl)"
	
	filename_ext = ".mdl"
	
	filter_glob = StringProperty(
			default="*.mdl",
			options={'HIDDEN'}
			)
	
	@classmethod
	def poll(cls, context):
		return True
	
	def execute(self, context):
		di = DataImporter()
		return di.run(self.filepath, context)

def menu_func_export(self, context):
	self.layout.operator(ImportWarMDL.bl_idname, text="WarCraft MDL (.mdl)")

def register():
	bpy.utils.register_class(ImportWarMDL)
	bpy.types.INFO_MT_file_import.append(menu_func_export)

def unregister():
	bpy.utils.unregister_class(ImportWarMDL)
	bpy.types.INFO_MT_file_import.remove(menu_func_export)

if __name__ == "__main__":
	register()

	# test call
	bpy.ops.import_mesh.warmdl('INVOKE_DEFAULT')

