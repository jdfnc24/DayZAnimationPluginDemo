import bpy
import bpy_types
import bmesh
from mathutils import *
from bpy_extras.wm_utils.progress_report import ProgressReport, ProgressReportSubstep
from bpy_extras.io_utils import ExportHelper
from bpy.props import *
import os
import string
import time
from DayzAnimationTools.Types.Txo import *

def apply_transfrom(ob, use_location=False, use_rotation=False, use_scale=False):
	mb = ob.matrix_basis
	I = Matrix()
	loc, rot, scale = mb.decompose()

	# rotation
	T = Matrix.Translation(loc)
	R = mb.to_3x3().normalized().to_4x4()
	S = Matrix.Diagonal(scale).to_4x4()

	transform = [I, I, I]
	basis = [T, R, S]

	def swap(i):
		transform[i], basis[i] = basis[i], transform[i]

	if use_location:
		swap(0)
	if use_rotation:
		swap(1)
	if use_scale:
		swap(2)
		
	M = transform[0] @ transform[1] @ transform[2]
	if hasattr(ob.data, "transform"):
		ob.data.transform(M)
	for c in ob.children:
		c.matrix_local = M @ c.matrix_local
		
	ob.matrix_basis = basis[0] @ basis[1] @ basis[2]

class TXO_PT_Export_Include(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = "Include"
	bl_parent_id = "FILE_PT_operator"

	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator
		return operator.bl_idname == "EXPORT_SCENE_OT_txo"

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		sfile = context.space_data
		operator = sfile.active_operator

		layout.prop(operator, "bExportSelectionOnly")
		layout.prop(operator, "bExportShowingOnly")

class TXO_PT_Export_Transform(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = "Transform"
	bl_parent_id = "FILE_PT_operator"

	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator
		return operator.bl_idname == "EXPORT_SCENE_OT_txo"

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		sfile = context.space_data
		operator = sfile.active_operator

		layout.prop(operator, "fUnitScale")

class TXO_PT_Export_Armature(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = "Armature"
	bl_parent_id = "FILE_PT_operator"

	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator
		return operator.bl_idname == "EXPORT_SCENE_OT_txo"

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		sfile = context.space_data
		operator = sfile.active_operator

		layout.prop(operator, "bEnsureEntityPosition")
		layout.prop(operator, "bAutoCreateHeadLookBone")
		sub = layout.column()
		sub.enabled = operator.bAutoCreateHeadLookBone
		sub.prop(operator, "headLookBoneName")
		sub.prop(operator, "headLookBoneParentName")
		sub.prop(operator, "headLookOffset")


def ExportTxoMenu(self, context):
	self.layout.operator(ExportTxoOperator.bl_idname, text='DayZ Object (.txo)', icon='OBJECT_DATA')

class ExportTxoOperator(bpy.types.Operator, ExportHelper):
	bl_idname = 'export_scene.txo'
	bl_label = 'Export Txo'
	bl_description = 'Export mesh(es) and skeleton to a txo file.'
	bl_options = {'PRESET'}

	filename_ext = '.txo'
	filter_glob: StringProperty(default='*.txo', options={'HIDDEN'})
	
	fUnitScale: FloatProperty(
		name='Scale Factor',
		description='Multiplies vertex/bone positions',
		default=1.0,
		min=0.0001
	)
	bExportSelectionOnly : bpy.props.BoolProperty(
		name='Selection Only', 
		description='Export selected objects only',
		default=False
	)
	bExportShowingOnly : bpy.props.BoolProperty(
		name='Showing Only', 
		description='Export showing (unhidden) objects/bones only',
		default=False
	)
	bAutoCreateHeadLookBone : bpy.props.BoolProperty(
		name='Auto Create HeadLook',
		description='Automatically create the HeadLookBone, ' +
					'and only if HeadLookBone does not exist and HeadLook Parent does exist', 
		default=True
	)
	headLookBoneName : bpy.props.StringProperty(
		name='HeadLook Bone',
		description='Bone defined as the "HeadLookBoneName" in the ai config.cpp\n' +
					'Note: usually "pin_lookat" but use "lookat" for vanilla infected\n' +
					'(NOT Case Sensitive, except during bone creation)',
		default='pin_lookat'
	)
	headLookBoneParentName : bpy.props.StringProperty(
		name='HeadLook Parent',
		description='Specify parent of HeadLookBone\n' +
					'(NOT Case Sensitive)',
		default='head'
	)
	headLookOffset : bpy.props.FloatVectorProperty(
		name='HeadLook Offset',
		description='If created, HeadLook bone\'s offset vector (right, forward, up), in meters, from HeadLook Parent',
		default=Vector((0.0, 0.25, 0.0))
	)
	bEnsureEntityPosition: BoolProperty(
		name='Auto Create EntityPosition',
		description='Creates an "EntityPosition" bone if not present',
		default=True
	)

	def draw(self, context):
		pass

	def execute(self, context):
		start_time = time.process_time()

		exportSettings = TxoExportSettings()
		exportSettings.fUnitScale:float = self.fUnitScale
		exportSettings.bExportSelectionOnly:int = self.bExportSelectionOnly
		exportSettings.bExportShowingOnly:int = self.bExportShowingOnly
		exportSettings.bEnsureEntityPosition:bool = self.bEnsureEntityPosition
		exportSettings.bAutoCreateHeadLookBone:bool = self.bAutoCreateHeadLookBone
		exportSettings.headLookBoneName:str = self.headLookBoneName
		exportSettings.headLookBoneParentName:str = self.headLookBoneParentName

		result = save(self, context, exportSettings)

		if not result:
			self.report({'INFO'}, 'Txo Export Finished in %.2f sec.' % (time.process_time() - start_time))
		else:
			self.report({'ERROR'}, result)

		return {'FINISHED'}

	@classmethod
	def poll(self, context):
		return True

def ShouldExportBone(poseBone:bpy_types.Bone) -> bool:
	'''
		Conditions that determine whether
		or not to skip exporting this bone
	'''

	if poseBone.name.lower().endswith('ik_helper'):
		return False
	
	if poseBone.bone.hide:
		return False
	
	return True

def GetBoneLocation(bone:bpy_types.Bone) -> FVector:
	mtxFix = Matrix(((0,1,0,0), (-1,0,0,0), (0,0,1,0), (0,0,0,1)))
	mtxFinal = bone.matrix_local @ mtxFix.inverted()

	if (bone.parent is None):
		vec = mtxFinal.translation
	else:
		vec = ((bone.parent.matrix_local @ mtxFix.inverted()).inverted() @ mtxFinal).translation

	return FVector(vec.x, vec.y, vec.z)


def GetBoneRotation(bone:bpy_types.Bone) -> FMatrix3:
	mtxFix = Matrix(((0,1,0,0), (-1,0,0,0), (0,0,1,0), (0,0,0,1)))
	mtxFinal = bone.matrix_local @ mtxFix.inverted()

	if (bone.parent is not None):
		mtxFinal = (bone.parent.matrix_local @ mtxFix.inverted()).inverted() @ mtxFinal
	
	q = mtxFinal.to_quaternion()
	q = Quaternion((q.w, q.x, q.z, q.y))
	mtxFinal = q.to_matrix()
	
	ret = FMatrix3()
	ret.a.set(mtxFinal[0][0], mtxFinal[0][1], mtxFinal[0][2])
	ret.b.set(mtxFinal[1][0], mtxFinal[1][1], mtxFinal[1][2])
	ret.c.set(mtxFinal[2][0], mtxFinal[2][1], mtxFinal[2][2])
	return ret



def save(self, context, exportSettings:TxoExportSettings = TxoExportSettings()):
	with ProgressReport(context.window_manager) as progress:

		txoName = os.path.splitext(os.path.basename(self.filepath))[0]
		progress.enter_substeps(1, txoName)

		ret = export_action(self, context, progress, exportSettings)

		if ret is not None:
			return ret

		progress.leave_substeps("Finished!")


def export_action(self, context, progress, exportSettings:TxoExportSettings = TxoExportSettings()):
	lods:dict[int, list[bpy.types.Object]] = {}
	skeleton:bpy.types.Object = None

	objsToSearch = []
	for obj in bpy.data.objects:
		if exportSettings.bExportSelectionOnly and not obj.select_get():
			continue
		if exportSettings.bExportShowingOnly and obj.hide_get():
			continue
		objsToSearch.append(obj)

	for obj in objsToSearch:
		# set skeleton if not already found
		if obj.type == 'ARMATURE':
			if skeleton != None:
				print(f'[DayzAnimationTools]: Warning: Multiple skeletons present, skipping "{obj.name}"')
			else:
				apply_transfrom(obj, True, True, True)
				skeleton = obj

		# append mesh to appropriate lod
		elif obj.type == 'MESH':
			# skip bone preview mesh
			if obj.name.lower().endswith('_bone_vis'):
				continue
			
			# handle custom lod designation
			if obj.name.lower().rstrip(string.digits).endswith('_lod'):
				idx = obj.name.lower().rfind('_lod') + 4
				lodIdx = int(obj.name[idx:])
				if lodIdx not in lods: lods[lodIdx] = []
				apply_transfrom(obj, True, True, True)
				lods[lodIdx].append(obj)

			# just put it in lod 0
			else:
				if 0 not in lods: lods[0] = []
				apply_transfrom(obj, True, True, True)
				lods[0].append(obj)

	txoObject = TxoObject()


	if skeleton != None:
		rootBones = []
		entityPosBone = None
		pinLookatBone = None
		for bone in skeleton.data.bones:
			if bone.parent == None:
				rootBones.append(bone)
			if bone.name.lower() == 'entityposition':
				entityPosBone = bone
			if bone.name.lower() == exportSettings.headLookBoneName:
				pinLookatBone = bone

		def RecurseExportBone(parentBone:bpy_types.Bone, parentTxoBone:TxoBone):
			if parentBone.parent == None:
				parentTxoBone.keyframe.offset = GetBoneLocation(parentBone)
				parentTxoBone.keyframe.rotMatrix = GetBoneRotation(parentBone)

			for childBone in parentBone.children:
				if childBone.name.lower() == 'entityposition':
					if rootBone != skeleton.data.bones[0]: # if custom root bone, this was probably unintentional
						print(f'[DayzAnimationTools]: Warning: EntityPosition bone is a child of "{parentBone.name}" when it should be a sibiling to "{rootBone.name}", keyframes will probably be incorrect!')
					continue # because we already handle this bone seperately, and it should have no children

				childTxoBone = TxoBone()
				childTxoBone.keyframe.offset = GetBoneLocation(childBone)
				childTxoBone.keyframe.rotMatrix = GetBoneRotation(childBone)

				RecurseExportBone(childBone, childTxoBone)
				parentTxoBone.children[childBone.name] = childTxoBone

			 # Auto creation of headLook bone, a quarter meter in front of headLookBoneParentName
			if exportSettings.bAutoCreateHeadLookBone and not pinLookatBone and parentBone.name.lower() == exportSettings.headLookBoneParentName.lower():
				txoPinLookatBone = TxoBone()
				mtx = parentBone.matrix_local.copy()
				mtx.translation += Vector((0.0, 0.25, 0.0))
				vec = (parentBone.matrix_local.inverted() @ mtx).translation
				txoPinLookatBone.keyframe.offset = FVector(vec.x, vec.y, vec.z)
				parentTxoBone.children[exportSettings.headLookBoneName] = txoPinLookatBone

		# Setup Scene_Root bone
		txoObject.rootBone = TxoBone()

		for rootBone in rootBones:
			txoRootBone = TxoBone()
			RecurseExportBone(rootBone, txoRootBone)
			txoObject.rootBone.children[rootBone.name] = txoRootBone
		
		# Setup EntityPosition bone
		if entityPosBone != None:
			epTxoBone = TxoBone()
			epTxoBone.keyframe.offset = GetBoneLocation(entityPosBone)
			epTxoBone.keyframe.rotMatrix = GetBoneRotation(entityPosBone)
			txoObject.rootBone.children['EntityPosition'] = epTxoBone
		elif exportSettings.bEnsureEntityPosition:
			txoObject.rootBone.children['EntityPosition'] = TxoBone()


	for idxLod, lod in lods.items():
		txoLod = TxoLod()

		if skeleton != None:
			# get list of all bones weight in all this lod's meshes
			lodBonesWithWeightsUnsorted:list[str] = []
			for mesh in lod:
				for vg in mesh.vertex_groups:
					if vg.name not in lodBonesWithWeightsUnsorted:
						lodBonesWithWeightsUnsorted.append(vg.name)

			# sort it in the order of all bones for the lod
			for bone in skeleton.data.bones:
				if bone.name in lodBonesWithWeightsUnsorted:
					txoLod.bones.append(bone.name)
			
		for mesh in lod:

			# setup materials
			if len(mesh.material_slots) == 0:
				if 'DefaultGeneratedMaterial' not in txoObject.materials:
					txoObject.materials.append('DefaultGeneratedMaterial')
			else:
				for mat in mesh.material_slots:
					if mat.name not in txoObject.materials:
						txoObject.materials.append(mat.name)

			bm = bmesh.new()
			bm.from_mesh(mesh.data)
			bm.faces.ensure_lookup_table()
			mesh.data.calc_normals_split()

			txoMesh = TxoMesh()

			if skeleton != None:
				vertexWeightLayer = bm.verts.layers.deform.verify()
				meshBonesWithWeights:list[str] = []
				for vg in mesh.vertex_groups:
					meshBonesWithWeights.append(vg.name)

			for vert in bm.verts:
				txoVertex = TxoVertex()
				txoVertex.pos = FVector(vert.co.x, vert.co.y, vert.co.z)
				if skeleton != None:
					if len(vert[vertexWeightLayer]) != 0:
						if len(vert[vertexWeightLayer]) > 4:
							print(f'[DayzAnimationTools]: Warning: "{mesh.name}" has a vertex ' +
			  				f'({vert.index}) weighted to more than 4 bones, since this is not ' +
							'supported by DayZ, the 4th bone will be given all the remaining weight!')
						totalWeight = 0.0
						for idxWeight, idxBone in enumerate(vert[vertexWeightLayer].keys()):
							if meshBonesWithWeights[idxBone] not in txoLod.bones:
								continue # vertex group is not named after a bone, skip it
							idxLodWeightedBones = txoLod.bones.index(meshBonesWithWeights[idxBone])
							if idxWeight < 4:
								txoVertex.weights[idxLodWeightedBones] = vert[vertexWeightLayer][idxBone]
								totalWeight += vert[vertexWeightLayer][idxBone]
							else:
								txoVertex.weights[idxLodWeightedBones] = 1.0 - totalWeight
								break

				txoMesh.verts.append(txoVertex)

			for face in bm.faces:
				numTxoFv = len(txoMesh.faceVerts)

				# insert face verts in reverse order
				for idxLoop, loop in enumerate(face.loops):
					txoFaceVert = TxoFaceVertex()
					txoFaceVert.vertIndex = loop.vert.index
					idxTxoFv = len(face.loops) - idxLoop + numTxoFv - 1
					txoFaceVert.idxList = [idxTxoFv, idxTxoFv]
					txoMesh.faceVerts.insert(numTxoFv, txoFaceVert)
					normal = mesh.data.loops[loop.index].normal
					txoMesh.normals.insert(numTxoFv, FVector(normal.x, normal.y, normal.z))
				
				txoFace = TxoFace()
				if len(mesh.material_slots) == 0 and face.material_index == 0:
					txoFace.idxMaterial = txoObject.materials.index('DefaultGeneratedMaterial')
				else:
					txoFace.idxMaterial = txoObject.materials.index(mesh.material_slots[face.material_index].name)

				for i in range(len(face.verts)):
					txoFace.faceVertIndices.append(numTxoFv + i)
				
				txoMesh.faces.append(txoFace)
				
			if obj.name.lower().rstrip(string.digits).endswith('_lod'):
				meshName = mesh.name[:mesh.name.lower().rfind('_lod')]
			else:
				meshName = mesh.name


			# TODO: uv layers, necessary?
			for _ in range(len(txoMesh.faceVerts)):
				txoMesh.texCoords.append(FVector2D())
				
			txoLod.meshes[meshName] = txoMesh
		
		txoObject.lods[idxLod] = txoLod

	
	txo = Txo()
	txo.objects = {'': txoObject}
	txo.Write(self.filepath, exportSettings)