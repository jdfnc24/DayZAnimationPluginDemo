import bpy
import bmesh
from mathutils import *
from bpy_extras.wm_utils.progress_report import ProgressReport
from bpy.props import *
from bpy_extras.io_utils import ImportHelper
import os
import time
import math
from DayzAnimationTools.Types.Txo import *

blender_version = bpy.app.version

class TXO_PT_Import_Include(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = "Include"
	bl_parent_id = "FILE_PT_operator"

	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator
		return operator.bl_idname == "IMPORT_SCENE_OT_txo"

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		sfile = context.space_data
		operator = sfile.active_operator

		layout.prop(operator, "bImportSkeleton")
		layout.prop(operator, "bImportMesh")
		layout.prop(operator, "bImportNormals")
		layout.prop(operator, "bImportUVs")
		if blender_version >= (4, 1, 0):
			layout.prop(operator, "bSmoothShading")
			if operator.bSmoothShading:
				layout.prop(operator, "fSmoothAngle")

class TXO_PT_Import_Transform(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = "Transform"
	bl_parent_id = "FILE_PT_operator"

	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator
		return operator.bl_idname == "IMPORT_SCENE_OT_txo"

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		sfile = context.space_data
		operator = sfile.active_operator

		layout.prop(operator, "fUnitScale")

class TXO_PT_Import_Armature(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = "Armature"
	bl_parent_id = "FILE_PT_operator"

	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator
		return operator.bl_idname == "IMPORT_SCENE_OT_txo"

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		sfile = context.space_data
		operator = sfile.active_operator

		layout.prop(operator, "bTryConnectBones")

def ImportTxoMenu(self, context):
	self.layout.operator(ImportTxoOperator.bl_idname, text='DayZ Object (.txo)', icon='OBJECT_DATA')

class ImportTxoOperator(bpy.types.Operator, ImportHelper):
	bl_idname = 'import_scene.txo'
	bl_label = 'Import Txo'
	bl_description = 'Import one or more txo files'
	bl_options = {'PRESET'}

	filename_ext = '.txo'
	filter_glob: StringProperty(default='*.txo', options={'HIDDEN'})

	files: CollectionProperty(type=bpy.types.PropertyGroup)
	
	fUnitScale: FloatProperty(
		name='Scale Factor',
		description='Multiplies vertex/bone positions',
		default=1.0,
		min=0.0001
	)
	bImportSkeleton: BoolProperty(
		name='Skeleton',
		description='',
		default=True
	)
	bImportMesh: BoolProperty(
		name='Meshes',
		description='',
		default=True
	)
	bImportNormals: BoolProperty(
		name='Vertex Normals',
		description='',
		default=False
	)
	bImportUVs: BoolProperty(
		name='UV Coordinates',
		description='',
		default=False
	)
	bTryConnectBones: BoolProperty(
		name='Connect Bones',
		description='Connects children with no siblings to their parent, makes the skeleton look cleaner, but can limit translation ability',
		default=True
	)
	if blender_version >= (4, 1, 0):
		bSmoothShading: BoolProperty(
			name='Smooth Shading',
			description='Apply smooth shading to the mesh',
			default=False
		)
		fSmoothAngle: FloatProperty(
			name='Smooth Angle',
			description='Angle threshold for smooth shading (in degrees)',
			default=60.0,
			min=0.0,
			max=180.0,
			subtype='ANGLE'
		)

	def draw(self, context):
		pass
	
	def apply_smooth_shading(obj, angle):

		# Enter Edit Mode
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')

		# Set sharpness by angle

		# Exit Edit Mode
		bpy.ops.object.mode_set(mode='OBJECT')

		# Add the "Set Sharp by Angle" modifier
		mod = obj.modifiers.new("SmoothByAngle", 'SET_SHARP_BY_ANGLE')
		mod.angle = math.radians(angle)

		# Optionally, you can also use the "Shade Smooth by Angle" operator

	def execute(self, context):
		start_time = time.process_time()

		importSettings = TxoImportSettings()
		if blender_version >= (4, 1, 0):
			importSettings.fUnitScale = self.fUnitScale
		else:
			importSettings.fUnitScale:float = self.fUnitScale
		importSettings.bImportSkeleton = self.bImportSkeleton
		importSettings.bImportMesh = self.bImportMesh
		importSettings.bImportNormals = self.bImportNormals
		importSettings.bImportUVs = self.bImportUVs
		importSettings.bTryConnectBones = self.bTryConnectBones

		result = load(self, context, importSettings)

		if not result:
			self.report({'INFO'}, 'Txo Import Finished in %.2f sec.' % (time.process_time() - start_time))
			if blender_version >= (4, 1, 0):
				# Apply smooth shading if enabled
				if self.bSmoothShading:
					for obj in context.scene.objects:
						if obj.type == 'MESH':
							apply_smooth_shading(obj, self.fSmoothAngle)
		else:
			self.report({'ERROR'}, result)

		return {'FINISHED'}

	@classmethod
	def poll(self, context):
		return True


def load(self, context, importSettings:TxoImportSettings = TxoImportSettings()):
	path = os.path.dirname(self.filepath)
	path = os.path.normpath(path)
	
	with ProgressReport(context.window_manager) as progress:
		progress.enter_substeps(len(self.files))

		mtxFix = Matrix(((0,1,0,0), (-1,0,0,0), (0,0,1,0), (0,0,0,1)))

		for f in self.files:
			txoName = os.path.splitext(f.name)[0]
			progress.enter_substeps(1, txoName)
			
			txoPath = os.path.normpath(os.path.join(path, f.name))
			txo = Txo.CreateFromFile(txoPath, importSettings)
			txo.name = txoName

			for txoObjectName, txoObject in txo.objects.items():

				mesh_objs = []
				mesh_mats = []

				# Setup Materials
				for mat in txoObject.materials:
					new_mat = bpy.data.materials.get(mat)
					if new_mat is not None:
						mesh_mats.append(new_mat)
						continue

					new_mat = bpy.data.materials.new(name=mat)
					new_mat.use_nodes = True

					bsdf_shader = new_mat.node_tree.nodes["Principled BSDF"]
					material_color_map = new_mat.node_tree.nodes.new("ShaderNodeTexImage")

				# Setup flattened bone dict if this txoObject has a skeleton
				bonesFlattened:dict[str, ImportBone] = {}
				if txoObject.HasSkeleton():
					class ImportBone:
						def __init__(self, idx:int, idxParent:int, txoBone:TxoBone):
							self.idx:int = idx
							self.idxParent:int = idxParent
							self.txoBone:TxoBone = txoBone

					def RecurseImportBone(parentBone:TxoBone, parentBoneIdx:int = -1):
						for childName, child in parentBone.children.items():
							idxBone = len(bonesFlattened)
							bonesFlattened[childName] = ImportBone(idxBone, parentBoneIdx, child)
							RecurseImportBone(child, idxBone)

					RecurseImportBone(txoObject.rootBone)

				# For each lod in this txoObject
				for idxTxoLod, txoLod in txoObject.lods.items():

					# For each mesh in this lod
					for txoMeshName, txoMesh in txoLod.meshes.items():

						# Setup data
						nameFixed = txoMeshName
						if len(txoObject.lods) > 1:
							nameFixed += '_lod%d' % idxTxoLod
						new_mesh = bpy.data.meshes.new(nameFixed)
						blend_mesh = bmesh.new()
						vertexWeightLayer = blend_mesh.verts.layers.deform.new()
						vertexUvLayers = []
						vertexSplitNormalBuffer = []

						# Setup uv layers
						for uvLayer in range(txoMesh.texCoordLayers):
							vertexUvLayers.append(blend_mesh.loops.layers.uv.new("UVSet_%d" % uvLayer))

						# Create vertices
						for vert in txoMesh.verts:
							blend_mesh.verts.new(vert.pos.toTuple())
						blend_mesh.verts.ensure_lookup_table()

						# Assign weights to vertices
						if importSettings.bImportSkeleton:
							for idxVert, vert in enumerate(txoMesh.verts):
								for idxBone, weight in vert.weights.items():
									boneName = txoLod.bones[idxBone]
									if boneName not in bonesFlattened:
										print(f'Warning: Cannot find bone "{boneName}" for skinning vertex in {txo.name}')
									elif weight > 0.0:
											blend_mesh.verts[idxVert][vertexWeightLayer][idxBone] = weight

						# Create faces
						for txoFace in txoMesh.faces:

							# Get verts by index
							faceVerts = []
							for idx in txoFace.faceVertIndices:
								faceVerts.append(blend_mesh.verts[txoMesh.faceVerts[idx].vertIndex])

							# Create face
							face = blend_mesh.faces.new(faceVerts)

							for idxLoop, loop in enumerate(face.loops):

								idxVert = txoFace.faceVertIndices[idxLoop]

								# Assign Normals
								if importSettings.bImportNormals:
									normal = Vector(txoMesh.normals[idxVert].toTuple()).normalized()
									vertexSplitNormalBuffer.append(normal)

								# Assign vertex uv layers
								if importSettings.bImportUVs:
									for idxUvLayer in range(txoMesh.texCoordLayers):
										idxUv = idxVert * txoMesh.texCoordLayers + idxUvLayer
										uv = (0.0, 1.0)
										if idxUv < len(txoMesh.texCoords):
											uv = txoMesh.texCoords[idxUv].toTuple()
										loop[vertexUvLayers[idxUvLayer]].uv = Vector(uv)

						blend_mesh.to_mesh(new_mesh)

						# Begin vertex normal assignment logic
						if importSettings.bImportNormals:
							if blender_version >= (4, 1, 0):
								new_mesh.normals_split_custom_set_from_vertices(vertexSplitNormalBuffer)
							else:
								new_mesh.create_normals_split()
								new_mesh.validate(clean_customdata=False)
								new_mesh.normals_split_custom_set(vertexSplitNormalBuffer)
						else:
							for p in new_mesh.polygons:
								p.use_smooth = True

						if blender_version < (4, 1, 0):
							new_mesh.use_auto_smooth = True

						# Add the mesh to the scene
						obj = bpy.data.objects.new(txoMeshName, new_mesh)
						mesh_objs.append(obj)

						# Apply mesh materials
						for mat in mesh_mats:
							obj.data.materials.append(mat)

						bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)
						bpy.context.view_layer.objects.active = obj

						# Create vertex groups for weights
						if importSettings.bImportSkeleton:
							for bone in txoLod.bones:
								obj.vertex_groups.new(name=bone)


				# Create the skeleton
				if importSettings.bImportSkeleton and txoObject.HasSkeleton():
					armature = bpy.data.armatures.new("Armature")
					skel_obj = bpy.data.objects.new(txo.name, armature)
					skel_obj.show_in_front = True

					bpy.context.view_layer.active_layer_collection.collection.objects.link(skel_obj)
					bpy.context.view_layer.objects.active = skel_obj

					bpy.ops.object.mode_set(mode='EDIT')

					for boneName, bone in bonesFlattened.items():
						skBone = armature.edit_bones.new(boneName)
						skBone.length = 0.1

						trans = Matrix.Translation(bone.txoBone.keyframe.offset.toTuple())

						rot = Matrix(
							(
								bone.txoBone.keyframe.rotMatrix.a.toTuple(),
								bone.txoBone.keyframe.rotMatrix.b.toTuple(),
								bone.txoBone.keyframe.rotMatrix.c.toTuple()
							)
						)
						
						quat = rot.to_quaternion().normalized()
						rot = Quaternion((quat.w, quat.x, quat.z, quat.y)).to_matrix()

						mtx = trans @ rot.to_4x4()

						if bone.idxParent == -1:
							skBone.matrix = mtx
						else:
							# Set parent
							skBone.parent = armature.edit_bones[bone.idxParent]
							skBone.matrix = skBone.parent.matrix @ mtx
							skBone.length = skBone.parent.length

							# If this is the only child of its parent, set parent length to distance from this bone
							if len(bonesFlattened[skBone.parent.name].txoBone.children) == 1:
								skBone.parent.length = (skBone.head - skBone.parent.head).length
								#print ("bone " , boneName , " " , skBone.parent.length)
								# when bone distance of parent is zero
								if skBone.parent.length == 0:
									skBone.parent.length = 0.1
							
					for skBone in armature.edit_bones:
						skBone.matrix = skBone.matrix @ mtxFix

						if skBone.parent is not None:
							if (skBone.head - skBone.parent.tail).length < 0.001:
								if importSettings.bTryConnectBones:
									skBone.use_connect = True
							else:
								if len(skBone.children) == 0:
									skBone.length = skBone.parent.length / 2

					# Reset the view mode
					bpy.ops.object.mode_set(mode='OBJECT')

					# Set armature deform for weights
					for mesh_obj in mesh_objs:
						if importSettings.bImportSkeleton and txoObject.HasSkeleton():
							mesh_obj.parent = skel_obj
							modifier = mesh_obj.modifiers.new('Armature Rig', 'ARMATURE')
							modifier.object = skel_obj
							modifier.use_bone_envelopes = False
						modifier.use_vertex_groups = True

			# Update the scene
			bpy.context.view_layer.update()

			# Reset the view mode
			bpy.ops.object.mode_set(mode='OBJECT')

			progress.leave_substeps()

		progress.leave_substeps("Finished!")

	return None
