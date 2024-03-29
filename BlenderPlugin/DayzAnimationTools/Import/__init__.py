import bpy
from mathutils import *
from .ImportTxo import *
from .ImportTxa import *

class DZAT_MT_ImportMenu(bpy.types.Menu):
	bl_label = 'Import'
	
	def draw(self, context):
		pass

def DZAT_ImportMenu(self, context):
	self.layout.menu('DZAT_MT_ImportMenu', icon='IMPORT')

classes = [
			TXO_PT_Import_Include,
			TXO_PT_Import_Transform,
			TXO_PT_Import_Armature,
			TXA_PT_Import_Include,
			TXA_PT_Import_Transform,
			ImportTxoOperator,
			ImportTxaOperator
		]

menus = [ImportTxoMenu, ImportTxaMenu]

def register():
	bpy.utils.register_class(DZAT_MT_ImportMenu)
	bpy.types.DZAT_MT_ToolbarMenu.append(DZAT_ImportMenu)

	for cls in classes:
		bpy.utils.register_class(cls)

	for menu in menus:
		bpy.types.DZAT_MT_ImportMenu.append(menu)
		
def unregister():
	for menu in menus:
		bpy.types.DZAT_MT_ImportMenu.remove(menu)

	for cls in classes:
		bpy.utils.unregister_class(cls)
		
	bpy.types.DZAT_MT_ToolbarMenu.remove(DZAT_ImportMenu)
	bpy.utils.unregister_class(DZAT_MT_ImportMenu)


if __name__ == "__main__":
	register()
