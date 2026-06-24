import bpy
from .ExportTxo import *
from .ExportTxa import *
from ..modules.bpyHandler import registerClasses, registerMenus, unregisterClasses, unregisterMenus

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

	registerClasses(classes)

	registerMenus(menus, 'DZAT_MT_ExportMenu')

def unregister():
	unregisterMenus(menus, 'DZAT_MT_ExportMenu')
    
	unregisterClasses(classes)
		
	bpy.types.DZAT_MT_ToolbarMenu.remove(DZAT_ExportMenu)
	bpy.utils.unregister_class(DZAT_MT_ExportMenu)

if __name__ == "__main__":
	register()
