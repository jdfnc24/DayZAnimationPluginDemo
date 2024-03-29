import bpy
from mathutils import *
from bpy_extras.wm_utils.progress_report import ProgressReport
from bpy_extras.io_utils import ImportHelper
from bpy.props import *
import os
import time
from DayzAnimationTools.Types.Txa import *

class TXA_PT_Import_Include(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = "Include"
	bl_parent_id = "FILE_PT_operator"

	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator
		return operator.bl_idname == "IMPORT_SCENE_OT_txa"

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		sfile = context.space_data
		operator = sfile.active_operator

		layout.prop(operator, "bImportTranslationKeys")
		layout.prop(operator, "bImportRotationKeys")
		layout.prop(operator, "bImportScaleKeys")

class TXA_PT_Import_Transform(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = "Transform"
	bl_parent_id = "FILE_PT_operator"

	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator
		return operator.bl_idname == "IMPORT_SCENE_OT_txa"

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		sfile = context.space_data
		operator = sfile.active_operator

		layout.prop(operator, "fUnitScale")

def ImportTxaMenu(self, context):
	self.layout.operator(ImportTxaOperator.bl_idname, text='DayZ Animation (.txa)', icon='ARMATURE_DATA')

class ImportTxaOperator(bpy.types.Operator, ImportHelper):
	bl_idname = 'import_scene.txa'
	bl_label = 'Import Txa'
	bl_description = 'Make sure a skeleton is selected!'
	bl_options = {'PRESET'}

	filename_ext = '.txa'
	filter_glob: StringProperty(default='*.txa', options={'HIDDEN'})

	files: CollectionProperty(type=bpy.types.PropertyGroup)

	fUnitScale: FloatProperty(
		name='Scale Factor',
		description='Multiplies keyframe translations',
		default=1.0,
		min=0.0001,
	)
	bImportTranslationKeys: BoolProperty(
		name='Translation Keys',
		description='Should translation keys be imported?',
		default=True
	)
	bImportRotationKeys: BoolProperty(
		name='Rotation Keys',
		description='Should rotation keys be imported?',
		default=True
	)
	bImportScaleKeys: BoolProperty(
		name='Scale Keys',
		description='Should scale keys be imported?',
		default=False
	)

	def draw(self, context):
		pass

	def execute(self, context):
		start_time = time.process_time()

		importSettings = TxaImportSettings()
		importSettings.fUnitScale:float = self.fUnitScale
		importSettings.bImportTranslationKeys:bool = self.bImportTranslationKeys
		importSettings.bImportRotationKeys:bool = self.bImportRotationKeys
		importSettings.bImportScaleKeys:bool = self.bImportScaleKeys

		result = load(self, context, importSettings)

		if not result:
			self.report({'INFO'}, 'Txa Import Finished in %.2f sec.' % (time.process_time() - start_time))
		else:
			self.report({'ERROR'}, result)

		return {'FINISHED'}

	@classmethod
	def poll(self, context):
		return True


def load(self, context, importSettings:TxaImportSettings = TxaImportSettings()):
	ob = bpy.context.object
	if ob.type != 'ARMATURE':
		return 'Select an armature first!'

	path = os.path.dirname(self.filepath)
	path = os.path.normpath(path)

	if ob.animation_data is None:
		ob.animation_data_create()

	with ProgressReport(context.window_manager) as progress:
		progress.enter_substeps(len(self.files))

		# Force all bones to use quaternion rotation
		for bone in ob.pose.bones.data.bones:
			bone.rotation_mode = 'QUATERNION'

		for f in self.files:
			txaName = os.path.splitext(f.name)[0]
			progress.enter_substeps(1, txaName)
			
			txaPath = os.path.normpath(os.path.join(path, f.name))
			txa = Txa.CreateFromFile(txaPath, importSettings)
			txa.name = txaName

			# Save active animation as nla strip if necessary
			if ob.animation_data.action is not None:
				action = ob.animation_data.action
				track = ob.animation_data.nla_tracks.new()
				track.strips.new(action.name, round(action.frame_range[0]), action)
			
			bpy.ops.object.mode_set(mode='POSE')
			action = bpy.data.actions.new(txa.name)
			ob.animation_data.action = action
			ob.animation_data.action.use_fake_user = True
			
			mtxFix = Matrix(((0,1,0,0), (-1,0,0,0), (0,0,1,0), (0,0,0,1)))

			for txaAnimationName, txaAnimation in txa.animations.items():
			
				# Setup flattened bone dict
				boneKeyframesFlattened:dict[str, list[TxaKeyframe]] = {}

				def RecurseImportBone(parentBone:TxaBone):
					for childName, child in parentBone.children.items():
						boneKeyframesFlattened[childName] = child.keyframes
						RecurseImportBone(child)

				for rootBoneName, rootBone in txaAnimation.rootBones.items():
					boneKeyframesFlattened[rootBoneName] = rootBone.keyframes
					RecurseImportBone(rootBone)

				scene = bpy.context.scene
				scene.render.fps = txaAnimation.fps
				scene.frame_start = 0
				scene.frame_end = txaAnimation.numFrames - 1

				progress.enter_substeps(len(boneKeyframesFlattened))
			
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

				# Look up table that we use to get a given bone by name
				# without having to worry about casing
				blBones = {}
				for bone in ob.pose.bones:
					name = bone.name.lower().replace(' ', '_')
					if name in blBones:
						print("[DayzAnimationTools]: Warning - Dupe bone name conflict for '%s'\n" % bone.name)
					blBones[name] = bone

				for txaBoneName, txaBoneKeyframes in boneKeyframesFlattened.items():
					if txaBoneName.lower() not in blBones:
						if txaBoneName.lower() not in ['scene_root', 'lefthandiktarget', 'leftforearmdirection', 'rightforearmdirection']: # bones to skip silently
							bSurvivorIKName = False
							for s in SURVIVOR_IK_ANIM_BONES:
								if txaBoneName.lower().startswith(s.lower()):
									bSurvivorIKName = True
									break
							if bSurvivorIKName:
								print(f'[DayzAnimationTools]: Warning - Ignoring survivor IK bone "{txaBoneName}" used in {txaName} because `Tools > Add Survivor IK Bones` is required first!')
							else:
								print(f'[DayzAnimationTools]: Warning - bone "{txaBoneName}" used in {txaName} does not exist in the selected skeleton, skipping animation data for this bone!')
					else:
						bone = blBones[txaBoneName.lower()]

						transKeys:dict[int, Vector] = {}
						rotKeys:dict[int, Quaternion] = {}
						scaleKeys:dict[int, Vector] = {}

						for kf in txaBoneKeyframes:
							if kf.HasTranslation():
								transKeys[kf.frameStart] = Vector(kf.translation.toTuple())
							if kf.HasRotation():
								rotKeys[kf.frameStart] = Quaternion(kf.rotation.toTuple())
							if kf.HasScale():
								scaleKeys[kf.frameStart] = Vector(kf.scale.toTuple())

						t_fcurves, q_fcurves, s_fcurves = None, None, None
						if len(transKeys) and importSettings.bImportTranslationKeys:
							t_fcurves = generate_fcurves(action.fcurves, bone.name, 'location', 3)
							for axis, fcurve in enumerate(t_fcurves):
								fcurve.color_mode = 'AUTO_RGB'
								fcurve.keyframe_points.add(len(transKeys))

						if len(rotKeys) and importSettings.bImportRotationKeys:
							q_fcurves = generate_fcurves(action.fcurves, bone.name, 'rotation_quaternion', 4)
							for axis, fcurve in enumerate(q_fcurves):
								fcurve.color_mode = 'AUTO_YRGB'
								fcurve.keyframe_points.add(len(rotKeys))

						if len(scaleKeys) and importSettings.bImportScaleKeys:
							s_fcurves = generate_fcurves(action.fcurves, bone.name, 'scale', 3)
							for axis, fcurve in enumerate(s_fcurves):
								fcurve.color_mode = 'AUTO_RGB'
								fcurve.keyframe_points.add(len(scaleKeys))

						for frame in range(txaAnimation.numFrames):

							# Rotation
							if frame in rotKeys and importSettings.bImportRotationKeys:
								rot = rotKeys[frame].to_matrix().to_4x4()

								if bone.parent is None:
									bone.matrix = rot @ mtxFix
								else:
									if bone.name == 'LeftHandOrigin':
										bone.matrix = ob.pose.bones['RightHand_Dummy'].matrix @ mtxFix.inverted() @ rot @ mtxFix
									elif bone.name == 'LeftForeArmDirectionOrigin':
										ToggleContraints(True)
										bone.matrix = ob.pose.bones['LeftHand'].matrix @ mtxFix.inverted() @ rot @ mtxFix
										ToggleContraints()
									elif bone.name == 'RightHandOrigin':
										bone.matrix = ob.pose.bones['RightHand'].matrix @ mtxFix.inverted() @ rot.inverted() @ mtxFix
									elif bone.name == 'RightForeArmDirectionOrigin':
										bone.matrix = ob.pose.bones['RightHand'].matrix @ mtxFix.inverted() @ rot @ mtxFix
									else:
										bone.matrix = bone.parent.matrix @ mtxFix.inverted() @ rot @ mtxFix

								quat = bone.rotation_quaternion
								idxKey = list(rotKeys.keys()).index(frame)
								for axis, fcurve in enumerate(q_fcurves):
									fcurve.keyframe_points[idxKey].co = Vector((frame, quat[axis]))
									fcurve.keyframe_points[idxKey].interpolation = 'LINEAR'
							
							# Translation
							if frame in transKeys and importSettings.bImportTranslationKeys:
								trans = transKeys[frame]

								#if not (abs(trans.x) < 1e-04 and abs(trans.y) < 1e-04 and abs(trans.z) < 1e-04):
								if bone.parent is None:
									bone.matrix = Matrix.Translation(trans) @ mtxFix.inverted()
								else:
									if bone.name == 'LeftHandOrigin':
										mtx = ob.pose.bones['Weapon_Root'].matrix @ mtxFix.inverted() @ Matrix.Translation(trans) @ mtxFix
										bone.matrix = mtx
									elif bone.name == 'LeftForeArmDirectionOrigin':
										ToggleContraints(True)
										mtx = ob.pose.bones['LeftHand'].matrix @ mtxFix.inverted() @ Matrix.Translation(trans) @ mtxFix
										bone.matrix = mtx
										ToggleContraints()
									elif bone.name == 'RightHandOrigin':
										mtx = ob.pose.bones['RightHand'].matrix @ mtxFix.inverted() @ Matrix.Translation(trans).inverted() @ mtxFix
										bone.matrix = mtx @ Matrix.Translation((0,bone.length,0))
									elif bone.name == 'RightForeArmDirectionOrigin':
										mtx = ob.pose.bones['RightHand'].matrix @ mtxFix.inverted() @ Matrix.Translation(trans) @ mtxFix
										bone.matrix = mtx
									else:
										bone.matrix = bone.parent.matrix @ mtxFix.inverted() @ Matrix.Translation(trans) @ mtxFix

								idxKey = list(transKeys.keys()).index(frame)
								for axis, fcurve in enumerate(t_fcurves):
									fcurve.keyframe_points[idxKey].co = Vector((frame, bone.location[axis]))
									fcurve.keyframe_points[idxKey].interpolation = 'LINEAR'

							# Scale
							if frame in scaleKeys and importSettings.bImportScaleKeys:
								scale = scaleKeys[frame]

								idxKey = list(scaleKeys.keys()).index(frame)
								for axis, fcurve in enumerate(s_fcurves):
									fcurve.keyframe_points[idxKey].co = Vector((frame, scale[axis]))
									fcurve.keyframe_points[idxKey].interpolation = 'LINEAR'

						# Update fcurves
						if len(transKeys) and importSettings.bImportTranslationKeys:
							for fc in t_fcurves: fc.update()
						if len(rotKeys) and importSettings.bImportRotationKeys:
							for fc in q_fcurves: fc.update()
						if len(scaleKeys) and importSettings.bImportScaleKeys:
							for fc in s_fcurves: fc.update()

						# Remove any leftover temporary transformations for this bone
						bone.matrix_basis.identity()

					progress.step()
				progress.leave_substeps()

				# Hack to fix LeftHandOrigin after the fact to comply with the "use bone tail" ik property
				if importSettings.bImportTranslationKeys:
					for txaBoneName in boneKeyframesFlattened:
						if txaBoneName.lower() == 'lefthandorigin' and txaBoneName.lower() in blBones:
							bone = blBones[txaBoneName.lower()]
							context.scene.frame_set(0)
							bone.matrix = bone.matrix @ Matrix.Translation((0,bone.length,0))
							newLocation = bone.location.copy()

							for axis in range(3):
								fcurve = action.fcurves.find(data_path=f'pose.bones["{bone.name}"].location', index=axis)
								for kf in fcurve.keyframe_points:
									if kf.co.x == 0:
										kf.co.y = newLocation[axis]
									elif kf.co.x == 1:
										kf.co.y = newLocation[axis]
										break
								fcurve.update()
							break

				# Re-enable constraints
				for bone, constraints in constraintMap.items():
					for i in range(len(constraints)):
						bone.constraints[i].enabled = constraints[i]

				# Events as notetracks
				for event in txaAnimation.events:
					notetrack = ob.animation_data.action.pose_markers.new(f'{event.name}|{event.userString}|{event.userInt}')
					notetrack.frame = event.frame

			bpy.context.evaluated_depsgraph_get().update()
			bpy.ops.object.mode_set(mode='POSE')

			# Re-enable constraints
			ToggleContraints(True)

			progress.leave_substeps()

		# Print when all files have been imported
		progress.leave_substeps("Finished!")


def generate_fcurves(action_fcurves, tag_name, _type, count):
	'''
		'tag_name': The name of the pose bone to generate fcurves for
		'_type': The type of fcurve to add
				ex: 'location', 'rotation_quaternion', 'scale'
		'count': Number of fcurves to generate (should match up with the
				 number of channels for a given fcurve type)
		Returns a list of the generated fcurves
	'''
	return [action_fcurves.new(data_path='pose.bones["%s"].%s' %
							   (tag_name, _type),
							   index=index,
							   action_group=tag_name)
			for index in range(count)]