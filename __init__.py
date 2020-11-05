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

from .ImportWarMDL import ImportWarMDL

dbg = False

bl_info = {
	"name": "Import WarCraft MDL (.mdl)",
	"description": "This addon allows you to import WarCraft MDL model files (.mdl).",
	"author": "Thomas 'CruzR' Glamsch, Mark Newbery, twilac",
	"version": (0, 2, 2),
	"blender": (2, 5, 7),
	#"api": ???,
	"location": "File > Import > WarCraft MDL (.mdl)",
	"warning": "Currently doesn't do animations, assumes max 1 camera, still work in progress.",
	"wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Import-Export/WarCraft_MDL",
	"tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=29552",
	"category": "Import-Export"}


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

