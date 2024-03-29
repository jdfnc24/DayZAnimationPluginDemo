import bpy
from mathutils import *
from bpy.props import *
import time

def AddSurvivorIKMenu(self, context):
	self.layout.operator(AddSurvivorIKOperator.bl_idname, text='Add Survivor IK Bones', icon='CONSTRAINT_BONE')

class AddSurvivorIKOperator(bpy.types.Operator):
	bl_idname = 'import_scene.addsurvivorik'
	bl_label = 'Add Survivor IK Bones'
	bl_description = 'Add IK bones to survivor skeleton.\nNote: Only keyframe (or even add) these bones when you want to create hand ik animations specifically'

	def execute(self, context):
		start_time = time.process_time()

		result = load(self, context)

		if not result:
			self.report({'INFO'}, 'model.cfg generated in %.2f sec.' % (time.process_time() - start_time))
		else:
			self.report({'ERROR'}, result)

		return {'FINISHED'}

	@classmethod
	def poll(self, context):
		return True
	
def load(self, context):
	ob = bpy.context.object
	if ob.type != 'ARMATURE':
		return 'Select an armature first!'
	
	oldMode = ob.mode
	
	bpy.ops.object.mode_set(mode='POSE')

	# Save active animation as nla strip if necessary
	if ob.animation_data is not None and ob.animation_data.action is not None:
		action = ob.animation_data.action
		track = ob.animation_data.nla_tracks.new()
		track.strips.new(action.name, round(action.frame_range[0]), action)
		ob.animation_data.action = None
	
	# Clear leftover pose transforms
	bpy.ops.pose.transforms_clear()
	
	# Create extra bones for constraints
	bpy.ops.object.mode_set(mode='EDIT')

	bone = ob.data.edit_bones.get('LeftHand')

	if bone:
		ikBone = ob.data.edit_bones.get('LeftHandOrigin')

		if not ikBone:
			ikBone = ob.data.edit_bones.new('LeftHandOrigin')
			ikBone.parent = ob.data.edit_bones['RightHand_Dummy']

		ikBone.length = bone.length
		ikBone.matrix = bone.matrix.copy() @ Matrix.Translation((0,bone.length,0))

	bone = ob.data.edit_bones.get('RightHand')
	
	if bone:
		ikBone = ob.data.edit_bones.get('RightHandOrigin')

		if not ikBone:
			ikBone = ob.data.edit_bones.new('RightHandOrigin')
			ikBone.parent = ob.data.edit_bones['RightShoulder']

		ikBone.length = bone.length
		ikBone.matrix = bone.matrix.copy()

	bone = ob.data.edit_bones.get('RightForeArm')
	
	if bone:
		ikBone = ob.data.edit_bones.get('RightForeArmDirection')

		if not ikBone:
			ikBone = ob.data.edit_bones.new('RightForeArmDirection')
			ikBone.parent = ob.data.edit_bones['RightShoulder']

		ikBone.length = bone.length
		ikBone.matrix = bone.matrix.copy()

	bone = ob.data.edit_bones.get('LeftForeArm')
	
	if bone:
		ikBone = ob.data.edit_bones.get('LeftForeArmDirection')

		if not ikBone:
			ikBone = ob.data.edit_bones.new('LeftForeArmDirection')
			ikBone.parent = ob.data.edit_bones['LeftShoulder']

		ikBone.length = bone.length
		ikBone.matrix = bone.matrix.copy()

	# Create constraints
	bpy.ops.object.mode_set(mode='POSE')

	bone = ob.pose.bones.get('LeftHand')
	ikBone = ob.pose.bones.get('LeftHandOrigin')
	poleBone = ob.pose.bones.get('LeftForeArmDirection')

	if bone and ikBone:
		c = bone.constraints.new('IK')
		c.target = ob
		c.subtarget = ikBone.name
		c.pole_target = ob
		c.pole_subtarget = poleBone.name
		c.pole_angle = 3.14159 * -127.9 / 180
		c.chain_count = 5
		c.use_rotation = True

	bone = ob.pose.bones.get('RightHand')
	ikBone = ob.pose.bones.get('RightHandOrigin')
	poleBone = ob.pose.bones.get('RightForeArmDirection')

	if bone and ikBone and poleBone:
		c = bone.constraints.new('IK')
		c.target = ob
		c.subtarget = ikBone.name
		c.pole_target = ob
		c.pole_subtarget = poleBone.name
		c.pole_angle = 3.14159 * 45.3 / 180
		c.chain_count = 5
		c.use_rotation = True
	
	bpy.ops.object.mode_set(mode=oldMode)

