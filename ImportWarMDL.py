import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

from .DataImporter import DataImporter


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
