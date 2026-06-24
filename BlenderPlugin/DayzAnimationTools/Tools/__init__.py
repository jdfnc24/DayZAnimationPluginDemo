import bpy
from .EventManager import *
from .GenerateModelCfg import *
from .AddSurvivorIK import *
from ..modules.bpyHandler import registerClasses, registerMenus, unregisterClasses, unregisterMenus

class DZAT_MT_ToolsMenu(bpy.types.Menu):
    bl_label = 'Tools'
    
    def draw(self, context):
        pass

def DZAT_ToolsMenu(self, context):
    self.layout.menu('DZAT_MT_ToolsMenu', icon='MODIFIER')

classes = [
			EventManagerPg,
			LIST_UL_EventManager,
			LIST_OT_EventManagerAddItem,
			LIST_OT_EventManagerRemoveItem,
			LIST_OT_EventManagerLoad,
			LIST_OT_EventManagerSave,
			PANEL_PT_EventManager,
			GenerateModelCfgOperator,
			AddSurvivorIKOperator
		]

menus = [
			GenerateModelCfgMenu,
			AddSurvivorIKMenu
		]

def register():
	bpy.utils.register_class(DZAT_MT_ToolsMenu)
	bpy.types.DZAT_MT_ToolbarMenu.append(DZAT_ToolsMenu)

	registerClasses(classes)

	registerMenus(menus, 'DZAT_MT_ToolsMenu')

	bpy.types.Scene.eventmanager = CollectionProperty(type = EventManagerPg)
	bpy.types.Scene.eventmanager_index = IntProperty(name = 'Select Event')

def unregister():
	unregisterMenus(menus, 'DZAT_MT_ToolsMenu')
	unregisterClasses(classes)

	bpy.types.DZAT_MT_ToolbarMenu.remove(DZAT_ToolsMenu)
	bpy.utils.unregister_class(DZAT_MT_ToolsMenu)

if __name__ == "__main__":
	register()
