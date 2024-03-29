import bpy
from .EventManager import *
from .GenerateModelCfg import *
from .AddSurvivorIK import *

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

	for cls in classes:
		bpy.utils.register_class(cls)

	for menu in menus:
		bpy.types.DZAT_MT_ToolsMenu.append(menu)

	bpy.types.Scene.eventmanager = CollectionProperty(type = EventManagerPg)
	bpy.types.Scene.eventmanager_index = IntProperty(name = 'Select Event')

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

if __name__ == "__main__":
	register()
