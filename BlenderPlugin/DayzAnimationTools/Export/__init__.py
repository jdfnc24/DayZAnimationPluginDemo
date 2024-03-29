import bpy
from .ExportTxo import *
from .ExportTxa import *

class DZAT_MT_ExportMenu(bpy.types.Menu):
    bl_label = 'Export'
    
    def draw(self, context):
        pass

def DZAT_ExportMenu(self, context):
    self.layout.menu('DZAT_MT_ExportMenu', icon='EXPORT')

classes = [
			TXO_PT_Export_Include,
			TXO_PT_Export_Transform,
			TXO_PT_Export_Armature,
			TXA_PT_Export_Include,
			TXA_PT_Export_Transform,
			TXA_PT_Export_Animation,
			ExportTxoOperator,
			ExportTxaOperator
		]

menus = [ExportTxoMenu, ExportTxaMenu]

def register():
	bpy.utils.register_class(DZAT_MT_ExportMenu)
	bpy.types.DZAT_MT_ToolbarMenu.append(DZAT_ExportMenu)

	for cls in classes:
		bpy.utils.register_class(cls)

	for menu in menus:
		bpy.types.DZAT_MT_ExportMenu.append(menu)

def unregister():
	for menu in menus:
		bpy.types.DZAT_MT_ExportMenu.remove(menu)

	for cls in classes:
		bpy.utils.unregister_class(cls)
		
	bpy.types.DZAT_MT_ToolbarMenu.remove(DZAT_ExportMenu)
	bpy.utils.unregister_class(DZAT_MT_ExportMenu)

if __name__ == "__main__":
	register()
