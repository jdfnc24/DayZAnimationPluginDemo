import bpy
import bpy_types
from mathutils import *
from bpy_extras.wm_utils.progress_report import ProgressReport, ProgressReportSubstep
from bpy_extras.io_utils import ExportHelper
from bpy.props import *
import os
import time
from DayzAnimationTools.Types.Txa import *

ANIM_TYPES = \
[
	('FB', 'Full Body', 'Full body animation'),
	('IK1H', 'Survivor IK 1h', 'Survivor one handed IK animation'),
	('IK2H', 'Survivor IK 2h', 'Survivor two handed IK animation'),
	('RL', 'Survivor Reload', 'Survivor reload animation'),
	('ADD', 'Additive', 'Additive animation')
]

class TXA_PT_Export_Include(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = "Include"
	bl_parent_id = "FILE_PT_operator"

	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator
		return operator.bl_idname == "EXPORT_SCENE_OT_txa"

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		sfile = context.space_data
		operator = sfile.active_operator

		layout.prop(operator, "bExportSelectedBonesOnly")
		layout.prop(operator, "bExportShowingBonesOnly")
		layout.prop(operator, "bExportTranslationKeys")
		layout.prop(operator, "bExportRotationKeys")
		layout.prop(operator, "bExportScaleKeys")

class TXA_PT_Export_Transform(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = "Transform"
	bl_parent_id = "FILE_PT_operator"

	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator
		return operator.bl_idname == "EXPORT_SCENE_OT_txa"

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		sfile = context.space_data
		operator = sfile.active_operator

		layout.prop(operator, "fUnitScale")

class TXA_PT_Export_Animation(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = "Animation"
	bl_parent_id = "FILE_PT_operator"

	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator
		return operator.bl_idname == "EXPORT_SCENE_OT_txa"

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		sfile = context.space_data
		operator = sfile.active_operator

		layout.prop(operator, "fpsOverride")
		layout.prop(operator, "eAnimType")
		layout.prop(operator, "bSaveAll")

def ExportTxaMenu(self, context):
	self.layout.operator(ExportTxaOperator.bl_idname, text='DayZ Animation (.txa)', icon='ARMATURE_DATA')

class ExportTxaOperator(bpy.types.Operator, ExportHelper):
	bl_idname = 'export_scene.txa'
	bl_label = 'Export Txa'
	bl_description = 'Make sure a skeleton is selected!'
	bl_options = {'PRESET'}

	filename_ext = '.txa'
	filter_glob: StringProperty(default='*.txa', options={'HIDDEN'})
	
	bExportSelectedBonesOnly : BoolProperty(
		name='Selected Bones Only',
		description='Export selected bones only',
		default=False
	)
	bExportShowingBonesOnly : BoolProperty(
		name='Showing Bones Only',
		description='Export showing (unhidden) bones only',
		default=False
	)
	bExportTranslationKeys: BoolProperty(
		name='Translation Keys',
		description='Should translation keys be exported?',
		default=True
	)
	bExportRotationKeys: BoolProperty(
		name='Rotation Keys',
		description='Should rotation keys be exported?',
		default=True
	)
	bExportScaleKeys: BoolProperty(
		name='Scale Keys',
		description='Should scale keys be exported?',
		default=False
	)
	fpsOverride : IntProperty(
		name='Override Fps',
		description='Use this fps instead the action\'s render fps, 0 for no override', 
		default=0,
		min=0
	)
	eAnimType : EnumProperty(
        items=ANIM_TYPES,
		name='Type',
		description='Animation type',
		default=0
	)
	bSaveAll : BoolProperty(
		name='Save All Actions',
		description='Saves all actions to ActionName.txa, ignores the filename you specify and only uses the directory', 
		default=False
	)
	fUnitScale: FloatProperty(
		name='Scale Factor',
		description='Multiplies keyframe translations',
		default=1.0,
		min=0.0001
	)

	def draw(self, context):
		pass

	def execute(self, context):
		start_time = time.process_time()

		exportSettings = TxaExportSettings()
		exportSettings.fUnitScale:float = self.fUnitScale
		exportSettings.bExportTranslationKeys:bool = self.bExportTranslationKeys
		exportSettings.bExportRotationKeys:bool = self.bExportRotationKeys
		exportSettings.bExportScaleKeys:bool = self.bExportScaleKeys
		exportSettings.bExportSelectedBonesOnly:int = self.bExportSelectedBonesOnly
		exportSettings.bExportShowingBonesOnly:int = self.bExportShowingBonesOnly
		exportSettings.fpsOverride:int = self.fpsOverride
		exportSettings.sAnimType:str = str(self.eAnimType)
		exportSettings.bSaveAll:bool = self.bSaveAll


		result = save(self, context, exportSettings)

		if not result:
			self.report({'INFO'}, 'Txa Export Finished in %.2f sec.' % (time.process_time() - start_time))
		else:
			self.report({'ERROR'}, result)

		return {'FINISHED'}

	@classmethod
	def poll(self, context):
		return True


def ShouldSkipBone(bone:bpy_types.Bone, exportSettings:TxaExportSettings = TxaExportSettings()) -> bool:
	'''
		Conditions that determine whether
		or not to skip exporting this bone
	'''

	if bone.name.lower().endswith('ik_helper'):
		return True
	
	if exportSettings.bExportSelectedBonesOnly and not bone.select:
		return True
	
	if exportSettings.bExportShowingBonesOnly and bone.hide:
		return True
	
	if exportSettings.sAnimType.startswith('IK'):
		bInList = False

		if exportSettings.sAnimType.endswith('1H'):
			lst = SURVIVOR_IK_ANIM_BONES_R
		else:
			lst = SURVIVOR_IK_ANIM_BONES_R + SURVIVOR_IK_ANIM_BONES_L

		for name in lst:
			if bone.name.lower() == name.lower():
				bInList = True
				break

		if not bInList:
			return True
	
	return False


def GetBoneLocation(bone:bpy_types.PoseBone, exportSettings:TxaExportSettings = TxaExportSettings()) -> FVector:
	mtxFix = Matrix(((0,1,0,0), (-1,0,0,0), (0,0,1,0), (0,0,0,1)))
	mtx = bone.matrix @ mtxFix.inverted()

	if (bone.parent is None):
		vec = mtx.translation
	else:
		if exportSettings.sAnimType.startswith('IK') and bone.name == 'LeftHandOrigin':
			mtxParent = bpy.context.object.pose.bones['RightHand_Dummy'].matrix
			mtx = bone.matrix @ Matrix.Translation((0,bone.length,0)).inverted() @ mtxFix.inverted()
			vec = ((mtxParent @ mtxFix.inverted()).inverted() @ mtx).translation
		elif exportSettings.sAnimType.startswith('IK') and bone.name == 'RightHandOrigin':
			mtxParent = bpy.context.object.pose.bones['RightHand'].matrix
			mtx = bone.matrix @ Matrix.Translation((0,bone.length,0)).inverted() @ mtxFix.inverted()
			vec = ((mtxParent @ mtxFix.inverted()).inverted() @ mtx).inverted().translation
		elif exportSettings.sAnimType.startswith('IK') and bone.name == 'LeftForeArmDirection':
			mtxParent = bpy.context.object.pose.bones['LeftHand'].matrix
			vec = ((mtxParent @ mtxFix.inverted()).inverted() @ mtx).translation
		elif exportSettings.sAnimType.startswith('IK') and bone.name == 'RightForeArmDirection':
			mtxParent = bpy.context.object.pose.bones['RightHand'].matrix
			vec = ((mtxParent @ mtxFix.inverted()).inverted() @ mtx).translation
		elif exportSettings.sAnimType.startswith('IK') and bone.name == 'LeftForeArm':
			mtxParent = bpy.context.object.pose.bones['LeftHand'].matrix
			vec = ((mtxParent @ mtxFix.inverted()).inverted() @ mtx).translation
		elif exportSettings.sAnimType.startswith('IK') and bone.name == 'RightForeArm':
			mtxParent = bpy.context.object.pose.bones['RightHand'].matrix
			vec = ((mtxParent @ mtxFix.inverted()).inverted() @ mtx).translation
		else:
			mtxParent = bone.parent.matrix
			vec = ((mtxParent @ mtxFix.inverted()).inverted() @ mtx).translation

	return FVector(vec.x, vec.y, vec.z)


def GetBoneRotation(bone:bpy_types.PoseBone, exportSettings:TxaExportSettings = TxaExportSettings()) -> FQuaternion:
	mtxFix = Matrix(((0,1,0,0), (-1,0,0,0), (0,0,1,0), (0,0,0,1)))
	mtx = bone.matrix @ mtxFix.inverted()

	if (bone.parent is not None):
		if exportSettings.sAnimType.startswith('IK') and bone.name == 'LeftHandOrigin':
			mtxParent = bpy.context.object.pose.bones['RightHand_Dummy'].matrix
			mtx = ((mtxParent @ mtxFix.inverted()).inverted() @ mtx)
		elif exportSettings.sAnimType.startswith('IK') and bone.name == 'RightHandOrigin':
			mtxParent = bpy.context.object.pose.bones['RightHand'].matrix
			mtx = ((mtxParent @ mtxFix.inverted()).inverted() @ mtx).inverted()
		elif exportSettings.sAnimType.startswith('IK') and bone.name.startswith('LeftForeArm'):
			mtxParent = bpy.context.object.pose.bones['LeftHand'].matrix
			mtx = ((mtxParent @ mtxFix.inverted()).inverted() @ mtx)
		elif exportSettings.sAnimType.startswith('IK') and bone.name.startswith('RightForeArm'):
			mtxParent = bpy.context.object.pose.bones['RightHand'].matrix
			mtx = ((mtxParent @ mtxFix.inverted()).inverted() @ mtx)
		else:
			mtxParent =  bone.parent.matrix
			mtx = ((mtxParent @ mtxFix.inverted()).inverted() @ mtx)
	
	q = mtx.to_quaternion()

	return FQuaternion(-q.w, -q.x, -q.y, -q.z)


def GetBoneScale(bone:bpy_types.PoseBone, exportSettings:TxaExportSettings = TxaExportSettings()) -> FVector:
	return FVector(bone.scale.x, bone.scale.y, bone.scale.z)


def save(self, context, exportSettings:TxaExportSettings = TxaExportSettings()):
	ob = bpy.context.object

	if ob.type != 'ARMATURE':
		return 'Select an armature first!'
	
	if ob.animation_data == None:
		return 'No animation data to export!'
	
	with ProgressReport(context.window_manager) as progress:

		if exportSettings.bSaveAll:
			if len(bpy.data.actions) < 1:
				return 'No actions to export!'
			
			path = os.path.dirname(self.filepath)

			actionOriginal = ob.animation_data.action

			for action in bpy.data.actions:
				ob.animation_data.action = action
				txaFilepath = os.path.join(path, action.name.replace(' ', '_') + '.txa')
				progress.enter_substeps(1, action.name)
				ret = export_action(self, context, progress, txaFilepath, exportSettings)
				if ret is not None:
					return ret
				progress.leave_substeps(f'Finished {action.name}')
			
			if actionOriginal is not None:
				ob.animation_data.action = actionOriginal
		else:
			if ob.animation_data.action == None:
				return 'No active action to export!'

			txaName = os.path.splitext(os.path.basename(self.filepath))[0]
			progress.enter_substeps(1, txaName)
			ret = export_action(self, context, progress, self.filepath, exportSettings)
			if ret is not None:
				return ret
			progress.leave_substeps(f'Finished {txaName}')


def export_action(self, context, progress, filepath, exportSettings:TxaExportSettings = TxaExportSettings()):
	ob = bpy.context.object

	action = ob.animation_data.action
	action.use_frame_range = True
	frame_original = context.scene.frame_current
	frame_start = max(0, int(action.frame_range[0]))
	frame_end = context.scene.frame_end
	
	txaAnimation = TxaAnimation()
	txaAnimation.numFrames = frame_end - frame_start + 1
	txaAnimation.fps = context.scene.render.fps

	if exportSettings.fpsOverride:
		txaAnimation.fps = exportSettings.fpsOverride
			
	constraintMap = {}
	def ToggleContraints(bValue:bool = False):
		if not bValue:
			for bone in ob.pose.bones:
				if len(bone.constraints) > 0:
					constraintMap[bone] = []
				for c in bone.constraints:
					constraintMap[bone].append(c.enabled)
					c.enabled = False
			if len(constraintMap) > 0:
				bpy.context.view_layer.update()
		else:
			bAny = len(constraintMap) > 0
			for bone, constraints in constraintMap.items():
				for i in range(len(constraints)):
					bone.constraints[i].enabled = constraints[i]
			if bAny:
				bpy.context.view_layer.update()

	# Disable constraints for now
	ToggleContraints()

	boneKeyframes:dict[str,list[TxaKeyframe]] = {}

	for frame in range(txaAnimation.numFrames):
		context.scene.frame_set(frame + frame_start)

		for pb in ob.pose.bones:
			boneName = pb.name

			if boneName not in boneKeyframes:
				boneKeyframes[boneName] = []

			bforearmdirection = exportSettings.sAnimType.startswith('IK') and (boneName.lower() == 'leftforearmdirection' or boneName.lower() == 'rightforearmdirection')

			if bforearmdirection:
				ToggleContraints(True)
			
			t = GetBoneLocation(pb, exportSettings)
			q = GetBoneRotation(pb, exportSettings)
			s = GetBoneScale(pb, exportSettings)

			if bforearmdirection:
				ToggleContraints()

			if frame:
				lastKf = boneKeyframes[boneName][len(boneKeyframes[boneName]) - 1]
				bSkipT, bSkipQ, bSkipS = False, False, False

				if not exportSettings.bExportTranslationKeys:
					bSkipT = True
				elif t.NearlyEquals(FVector.zero()):
					bSkipT = True
				elif lastKf.HasTranslation() and t.NearlyEquals(lastKf.translation):
					bSkipT = True

				if not exportSettings.bExportRotationKeys:
					bSkipQ = True
				elif q.NearlyEquals(FQuaternion.identity()):
					bSkipQ = True
				elif lastKf.HasRotation() and q.NearlyEquals(lastKf.rotation):
					bSkipQ = True

				if not exportSettings.bExportScaleKeys:
					bSkipS = True
				elif s.NearlyEquals(FVector.one()):
					bSkipS = True
				elif lastKf.HasScale() and s.NearlyEquals(lastKf.scale):
					bSkipS = True
				
				if bSkipT and bSkipQ and bSkipS:
					lastKf.frameEnd = frame
					continue

			txaKf = TxaKeyframe()
			txaKf.frameStart = frame

			if exportSettings.sAnimType.startswith('IK'):
				txaKf.frameEnd = 1
			else:
				txaKf.frameEnd = frame

			if exportSettings.bExportTranslationKeys and not t.NearlyEquals(FVector.zero()):
				txaKf.translation = t
			if exportSettings.bExportRotationKeys and not q.NearlyEquals(FQuaternion.identity()):
				txaKf.rotation = q
			if exportSettings.bExportScaleKeys and not s.NearlyEquals(FVector.one()):
				txaKf.scale = s
			boneKeyframes[boneName].append(txaKf)
			
		if exportSettings.sAnimType.startswith('IK'):
			break

	# Events
	for marker in action.pose_markers:
		if not '|' in marker.name: continue
		data = marker.name.split('|')
		if len(data) != 3: continue
		name, userString, userInt = data

		event = TxaEvent()
		event.frame = marker.frame
		event.name = name
		event.userString = userString
		event.userInt = int(userInt)
		
		txaAnimation.events.append(event)

	emptyKf = TxaKeyframe()
	emptyKf.frameEnd = frame_end

	def RecurseExportBone(bone:bpy_types.Bone, parentTxaBone:TxaBone):
		txaBone = None

		if ShouldSkipBone(bone, exportSettings) or (exportSettings.sAnimType == 'ADD' and bone.name not in boneKeyframes):
			print(f'[DayzAnimationTools]: Info: Skipping export for bone "{bone.name}"')
		else:
			txaBone = TxaBone()

			if bone.name in boneKeyframes:
				txaBone.keyframes = boneKeyframes[bone.name]
			else:
				txaBone.keyframes = [emptyKf]

			txaBoneName = bone.name

			if parentTxaBone == None:
				# if exportSettings.sAnimType.startswith('IK') and (txaBoneName.lower() == 'leftforearm' or txaBoneName.lower() == 'rightforearm'):
				# 	txaAnimation.rootBones[txaBoneName + 'DirectionOrigin'] = txaBone
				# 	txaBone = None
				# else:
				txaAnimation.rootBones[txaBoneName] = txaBone
			else:
				parentTxaBone.children[txaBoneName] = txaBone
			
			# Special case
			if bone.name == 'LeftHandOrigin': # LeftHandIKTarget (copy LeftHandOrigin)
				if parentTxaBone == None:
					txaAnimation.rootBones['LeftHandIKTarget'] = txaBone
				else:
					parentTxaBone.children['LeftHandIKTarget'] = txaBone


		for childBone in bone.children:
			RecurseExportBone(childBone, txaBone)
			
	# Setup Scene_Root bone if full body
	sceneRoot = None
	if exportSettings.sAnimType == 'FB':
		sceneRoot = TxaBone()
		sceneRoot.keyframes = [emptyKf]
		txaAnimation.rootBones['Scene_Root'] = sceneRoot
	
	for bone in ob.data.bones:
		if not bone.parent:
			RecurseExportBone(bone, sceneRoot)

	txa = Txa()
	txa.name = os.path.splitext(os.path.basename(filepath))[0].replace(' ', '_')
	txa.animations[txa.name] = txaAnimation
	txa.Write(filepath)

	# Re-enable constraints
	ToggleContraints(True)

	context.scene.frame_set(frame_original)
