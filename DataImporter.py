import pdb
import time

import bpy

from .BONE import BONE
from .CAMERA import CAMERA
from .FACES import FACES
from .GEOSET import GEOSET
from .GROUPS import GROUPS
from .GeosetManager import GeosetManager
from .HELPER import HELPER
from .MODEL import MODEL
from .NORMALS import NORMALS
from .PIVOTPOINTS import PIVOTPOINTS
from .SEARCH import SEARCH
from .StateMachine import StateMachine
from .TVERTICES import TVERTICES
from .VERSION import VERSION
from .VERTEXGROUP import VERTEXGROUP
from .VERTICES import VERTICES
from .__init__ import dbg


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
