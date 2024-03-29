import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import *
import time

def GenerateModelCfgMenu(self, context):
	self.layout.operator(GenerateModelCfgOperator.bl_idname, text='Generate DayZ Model Config (model.cfg)', icon='FILE_CACHE')

class GenerateModelCfgOperator(bpy.types.Operator, ExportHelper):
	bl_idname = 'export_scene.modelcfg'
	bl_label = 'Generate'
	bl_description = 'Generate a CfgSkeletons entry for this skeleton'
	bl_options = {'PRESET'}

	filename_ext = '.cfg'
	filename: bpy.props.StringProperty(subtype='FILE_NAME')
	filter_glob: StringProperty(default='*.cfg', options={'HIDDEN'})

	def invoke(self, context, event):
		self.filename = 'model.cfg'
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def execute(self, context):
		start_time = time.process_time()

		result = save(self, context)

		if not result:
			self.report({'INFO'}, 'model.cfg generated in %.2f sec.' % (time.process_time() - start_time))
		else:
			self.report({'ERROR'}, result)

		return {'FINISHED'}

	@classmethod
	def poll(self, context):
		return True
	
def ShouldSkipBone(bone:bpy.types.PoseBone) -> bool:
	names = \
	[
		'scene_root',
		'entityposition',
		'righthandorigin',
		'righthand_dummy',
		'rightforearmdirection',
		'lefthandorigin',
		'lefthand_dummy',
		'leftforearmdirection'
	]

	if bone != None and bone.name.lower() in names:
		return True

	return False

def save(self, context):
	ob = bpy.context.object
	if ob.type != 'ARMATURE':
		return 'An armature must be selected!'

	# Generate CfgSkeletons entry
	modelcfg = '\
\
class CfgSkeletons\n\
{\n\
	class %s\n\
	{\n\
		isDiscrete=0;\n\
		skeletonInherit="";\n\
		skeletonBones[]=\n\
		{\n\
' % ob.name.replace(' ', '_')

	for idxBone, bone in enumerate(ob.pose.bones):
		if ShouldSkipBone(bone): continue

		name = bone.name.replace(' ', '_')
		parentName = '' if not bone.parent or ShouldSkipBone(bone) else bone.parent.name.replace(' ', '_')

		modelcfg += f'\t\t\t"{name}", "{parentName}"'

		if idxBone < len(ob.pose.bones) - 1:
			modelcfg += ','

		modelcfg += '\n'

	modelcfg = modelcfg[:-2] + '\n'

	modelcfg += '\
		};\n\
	};\n\
};\
'
	
	# Generate CfgModels entry
	modelcfg += '\
\n\n\
class CfgModels\n\
{\n\
	class P3dFilenameNoExtension // Change this to be the exact filename of the respective p3d, without the file extension\n\
	{\n\
		skeletonName=%s;\n\
		sectionsInherit="";\n\
		sections[]={}\n\
		class Animations\n\
		{\n\
		};\n\
	};\n\
};\
' % ob.name.replace(' ', '_')

	with open(self.filepath, 'w') as file:
		file.write(modelcfg)
