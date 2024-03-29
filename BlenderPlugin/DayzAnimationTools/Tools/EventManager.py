import bpy
from bpy.props import *
from bpy.types import PropertyGroup, UIList, Operator, Panel

class EventManagerPg(PropertyGroup):
	Type: StringProperty(
		   name='Type',
		   description='Event type (Sound, Step, etc)',
		   default='Sound'
	)
	Frame: IntProperty(
		   name='Frame',
		   description='The frame this event should occur on',
		   min=0,
		   soft_min=0,
		   default=0
	)
	ID: IntProperty(
		   name='ID',
		   description='Event ID',
		   default=-1
	)
	Args: StringProperty(
		   name='Args',
		   description='Event Arguments',
		   default=''
	)

class LIST_UL_EventManager(UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			layout.label(text=f'Frame {item.Frame}: {item.Type} ({item.ID})', icon = 'TIME')

		elif self.layout_type in {'GRID'}:
			layout.alignment = 'CENTER'
			layout.label(text=f'{item.Frame}', icon = 'TIME')


class LIST_OT_EventManagerAddItem(Operator):
	bl_idname = 'eventmanager.additem'
	bl_label = 'Add a new event'

	@classmethod
	def poll(cls, context):
		return (
			context.scene.eventmanager != None and
			bpy.context.object and
			bpy.context.object.type == 'ARMATURE' and
			bpy.context.object.animation_data and
			bpy.context.object.animation_data.action
		)

	def execute(self, context):
		item = context.scene.eventmanager.add()
		item.Frame = context.scene.frame_current
		context.scene.eventmanager_index = len(context.scene.eventmanager) - 1
		return{'FINISHED'}


class LIST_OT_EventManagerRemoveItem(Operator):
	bl_idname = 'eventmanager.removeitem'
	bl_label = 'Remove an event'

	@classmethod
	def poll(cls, context):
		return (
			context.scene.eventmanager != None and
			bpy.context.object and
			bpy.context.object.type == 'ARMATURE' and
			bpy.context.object.animation_data and
			bpy.context.object.animation_data.action
		)

	def execute(self, context):
		eventmanager = context.scene.eventmanager
		index = context.scene.eventmanager_index

		eventmanager.remove(index)
		context.scene.eventmanager_index = min(max(0, index - 1), len(eventmanager) - 1)

		return{'FINISHED'}

class LIST_OT_EventManagerLoad(Operator):
	'''Make sure an armature is selected (or in pose mode), and there is an active animation action'''

	bl_idname = "eventmanager.load"
	bl_label = "Load Events"

	@classmethod
	def poll(cls, context):
		return (
			context.scene.eventmanager != None and
			bpy.context.object and
			bpy.context.object.type == 'ARMATURE' and
			bpy.context.object.animation_data and
			bpy.context.object.animation_data.action
		)
		
	def execute(self, context):
		context.scene.eventmanager.clear()
		ob = bpy.context.object
		
		eventMap:dict[int, list[tuple]] = {}
		for marker in ob.animation_data.action.pose_markers:
			print('\n' + marker.name + '\n')
			if '|' not in marker.name: continue
			frame = int(marker.frame)
			if frame not in eventMap: eventMap[frame] = []
			eventMap[frame].append(tuple(marker.name.split('|')))
		
		eventMap = dict(sorted(eventMap.items()))
		for frame, eventList in eventMap.items():
			for event in eventList:
				emItem = context.scene.eventmanager.add()
				emItem.Frame = frame
				emItem.Type = event[0]
				emItem.Args = event[1]
				emItem.ID = int(event[2])

		return{'FINISHED'}

class LIST_OT_EventManagerSave(Operator):
	'''Make sure an armature is selected (or in pose mode), and there is an active animation action\nNote: Saving an empty list will clear all events'''

	bl_idname = "eventmanager.save"
	bl_label = "Save Events"

	@classmethod
	def poll(cls, context):
		return (
			context.scene.eventmanager != None and
			bpy.context.object and
			bpy.context.object.type == 'ARMATURE' and
			bpy.context.object.animation_data and
			bpy.context.object.animation_data.action
		)

	def execute(self, context):
		ob = bpy.context.object
		
		for marker in ob.animation_data.action.pose_markers:
			ob.animation_data.action.pose_markers.remove(marker)
			
		for event in context.scene.eventmanager:
			notetrack = ob.animation_data.action.pose_markers.new(f'{event.Type}|{event.Args}|{event.ID}')
			notetrack.frame = event.Frame
		
		# reload to re-sort list
		bpy.ops.eventmanager.load()

		return{'FINISHED'}

class PANEL_PT_EventManager(Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Dayz Animation Tools"
	bl_label = "Events"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		
		row = layout.row()
		row.operator('eventmanager.load', text='Load', icon='IMPORT')
		
		if (
			context.scene.eventmanager != None and
			bpy.context.object and
			bpy.context.object.type == 'ARMATURE' and
			bpy.context.object.animation_data and
			bpy.context.object.animation_data.action
		):
			row.operator('eventmanager.save', text='Save', icon='EXPORT')

			row = layout.row()
			row.template_list("LIST_UL_EventManager", "EventManager", scene,
							  "eventmanager", scene, "eventmanager_index")
			
			row = layout.row()
			row.operator('eventmanager.additem', text='Add', icon='ADD')
			row.operator('eventmanager.removeitem', text='Remove', icon='REMOVE')

			if len(scene.eventmanager) > 0:
				if len(scene.eventmanager) > scene.eventmanager_index:
					item = scene.eventmanager[scene.eventmanager_index]
				else:
					item = scene.eventmanager[0]

				layout.separator()

				row = layout.row()
				row.prop(item, 'Frame')
				row.prop(item, 'ID')

				col = layout.column()
				col.prop(item, 'Type', icon='CON_TRANSFORM_CACHE')
				col.prop(item, 'Args', icon='CON_TRANSLIKE')