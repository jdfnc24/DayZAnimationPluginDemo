
bl_info = {
	'name': 'Dayz Animation Tools',
	'author': 'Mrtea101',
	'version': (1, 0, 0),
	'blender': (2, 80, 0),
	'location': 'File > Import',
	'description': 'Animation tools for handling DayZ human-readable assets.',
	'wiki_url': '',
	'tracker_url': '',
	'category': 'Import-Export'
}

import bpy

class DZAT_MT_ToolbarMenu(bpy.types.Menu):
	bl_label = 'DayZ Animation Tools'
	
	def draw(self, context):
		pass

def DZAT_ToolbarMenu(self, context):
	self.layout.menu('DZAT_MT_ToolbarMenu')
		
from . import Import
from . import Export
from . import Tools

modules = [Import, Export, Tools]

def register():
	bpy.utils.register_class(DZAT_MT_ToolbarMenu)
	bpy.types.VIEW3D_MT_editor_menus.append(DZAT_ToolbarMenu)

	for module in modules:
		module.register()

def unregister():
	for module in modules:
		module.unregister()

	bpy.types.VIEW3D_MT_editor_menus.remove(DZAT_ToolbarMenu)
	bpy.utils.unregister_class(DZAT_MT_ToolbarMenu)

	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()


