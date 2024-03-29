from io import StringIO
import shutil
from DayzAnimationTools.Utils.AsciiReader import AsciiReader
from DayzAnimationTools.Utils.DayzAnimUtils import *

class TxoImportSettings:

	__slots__ = (
		'fUnitScale',
		'bImportSkeleton',
		'bImportMesh',
		'bImportNormals',
		'bImportUVs',
		'bTryConnectBones'
	)
	
	def __init__(self):
		self.fUnitScale:float = 1.0
		self.bImportSkeleton = True
		self.bImportMesh = True
		self.bImportNormals = False
		self.bImportUVs = False
		self.bTryConnectBones = True

class TxoExportSettings:

	__slots__ = (
		'fUnitScale',
		'bExportSelectionOnly',
		'bExportShowingOnly',
		'bAutoCreateHeadLookBone',
		'headLookBoneName',
		'headLookBoneParentName',
		'bEnsureEntityPosition'
	)
	
	def __init__(self):
		self.fUnitScale:float = 1.0
		self.bExportSelectionOnly:bool = False
		self.bExportShowingOnly:bool = False
		self.bAutoCreateHeadLookBone:bool = True
		self.headLookBoneName:str = 'pin_lookat'
		self.headLookBoneParentName:str = 'head'
		self.bEnsureEntityPosition:bool = True


importSettings = TxoImportSettings()
exportSettings = TxoExportSettings()
txoObjectTags = {}

class Txo:

	__slots__ = (
		'name',
		'objects'
	)

	def __init__(self):
		self.name:str = ''
		self.objects:dict[str, TxoObject] = {}

	def CreateFromFile(filepath=None, inImportSettings = TxoImportSettings()):
		global importSettings
		importSettings = inImportSettings
		txo = Txo()

		buffer = b''
		with open(filepath, 'rb') as fs:
			buffer = fs.read()

		ascr = AsciiReader(buffer)
		txo.Read(ascr)

		return txo

	def Read(self, ascr: AsciiReader):
		ascr.SkipWhitespaces()

		while ascr.ReadStrIfPresent('$'):
			# Read object
			if ascr.ReadStrIfPresent('object'):
				ascr.SkipWhitespaces()

				# Read object name
				txoName = ascr.ReadEncapsulatedStr()
				ascr.SkipWhitespaces()

				# Read entry bracket
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces()

				txoObject = TxoObject()
				txoObject.Read(ascr)

				# Read closing bracket
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces()

				self.objects[txoName] = txoObject
	
	def Write(self, filepath = '', inExportSettings = TxoExportSettings()):
		global exportSettings
		exportSettings = inExportSettings

		with StringIO() as fs:
			for txoObjectName, txoObject in self.objects.items():
				fs.write(f'$object "{txoObjectName}" {{\n')
				txoObject.Write(fs)
				fs.write('}\n')

			# Write stream to file
			with open(filepath, 'w') as fd:
				fs.seek(0)
				shutil.copyfileobj(fs, fd, 1024)

class TxoObject:

	__slots__ = (
		'version',
		'tags',
		'rootBone',
		'materials',
		'lods'
	)

	def __init__(self):
		self.version:float = 1.0
		self.tags:dict[str, str] = {}
		self.materials:list[str] = []
		self.lods:dict[int, TxoLod] = {}
	
	def HasSkeleton(self) -> bool:
		return hasattr(self, 'rootBone')

	def Read(self, ascr: AsciiReader):

		# Read properties
		while ascr.ReadStrIfPresent('#'):
			if ascr.ReadStrIfPresent('version'):
				ascr.SkipWhitespaces()
				self.version = ascr.ReadFloat()
				ascr.SkipWhitespaces()
			elif ascr.ReadStrIfPresent('tag'):
				ascr.SkipWhitespaces()
				tagName = ascr.ReadVariableName()
				ascr.SkipWhitespaces()
				tagValue = ascr.ReadEncapsulatedStr()
				ascr.SkipWhitespaces()
				self.tags[tagName] = tagValue
		
		# Setup global use of tags
		global txoObjectTags
		txoObjectTags.clear()
		txoObjectTags = self.tags
		
		# Read subobjects
		while ascr.ReadStrIfPresent('$'):

			# Read skeleton
			if ascr.ReadStrIfPresent('node'):
				ascr.SkipWhitespaces()
				assert ascr.ReadEncapsulatedStrIfPresent('Scene_Root')
				ascr.SkipWhitespaces()
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces()
				self.rootBone = TxoBone()
				self.rootBone.Read(ascr)
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces()

			# Read materials
			elif ascr.ReadStrIfPresent('materials'):
				ascr.SkipWhitespaces()
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces()
				while ascr.ReadStrIfPresent('$material'):
					ascr.SkipWhitespaces()
					self.materials.append(ascr.ReadEncapsulatedStr())
					ascr.SkipWhitespaces()
					assert ascr.ReadStrIfPresent('{')
					ascr.SkipWhitespaces()
					assert ascr.ReadStrIfPresent('}')
					ascr.SkipWhitespaces()
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces()
				
			# Read lods
			elif ascr.ReadStrIfPresent('lod'):
				ascr.SkipWhitespaces()
				idxLod = ascr.ReadInt()
				ascr.SkipWhitespaces()

				# Read entry bracket
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces()

				txoLod = TxoLod()
				txoLod.Read(ascr)
				self.lods[idxLod] = txoLod

				# Read closing bracket
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces()

	def Write(self, fs:StringIO):
			# Write properties
			#fs.write(f' #version {self.version}\n') # Not needed as there is only one version (1.0)
			for tagName, tagValue in self.tags:
				fs.write(f' #tag {tagName} "{tagValue}"\n')

			# Write bone structure
			if self.HasSkeleton():
				fs.write(' $node "Scene_Root" {\n')
				self.rootBone.Write(fs)
				fs.write(' }\n')
			
			# Write materials
			if (len(self.materials) > 0):
				fs.write(' $materials {\n')
				for mat in self.materials:
					fs.write(f'  $material "{mat}" {{\n')
					fs.write('  }\n')
				fs.write(' }\n')

			# Write lods
			for idxLod, lod in self.lods.items():
				fs.write(f' $lod {idxLod} {{\n')
				lod.Write(fs)
				fs.write(' }\n')

class TxoLod:

	__slots__ = (
		'lodFactor',
		'bones',
		'meshes'
	)

	def __init__(self):
		self.lodFactor:float = 1.0
		self.bones:list[str] = []
		self.meshes:dict[str, TxoMesh] = {}

	def Read(self, ascr: AsciiReader):
		
		global importSettings

		# Read properties
		while ascr.ReadStrIfPresent('#'):
			if ascr.ReadStrIfPresent('lodFactor'):
				ascr.SkipWhitespaces()
				self.lodFactor = ascr.ReadFloat()
				ascr.SkipWhitespaces()
		
		# Read subobjects
		while ascr.ReadStrIfPresent('$'):

			# Read bones
			if ascr.ReadStrIfPresent('bones'):
				ascr.SkipWhitespaces()
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces()
				while ascr.PeekStr(1) == '"':
					self.bones.append(ascr.ReadEncapsulatedStr())
					ascr.SkipWhitespaces()
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces()
				
			# Read meshes
			elif ascr.ReadStrIfPresent('mesh'):
				ascr.SkipWhitespaces()

				# Read mesh name
				meshName = ascr.ReadEncapsulatedStr()
				ascr.SkipWhitespaces()

				if importSettings.bImportMesh:
					# Read entry bracket
					assert ascr.ReadStrIfPresent('{')
					ascr.SkipWhitespaces()

					txoMesh = TxoMesh()
					txoMesh.Read(ascr)
					self.meshes[meshName] = txoMesh

					# Read closing bracket
					assert ascr.ReadStrIfPresent('}')
				else:
					# Skip until after this '$mesh {}' scope
					ascr.SkipScope('{', '}')

				ascr.SkipWhitespaces()

	def Write(self, fs:StringIO):
		# Write properties
		if self.lodFactor != 1.0: # only necessary if not 1.0
			fs.write(f'  #lodFactor {self.lodFactor}\n')
		
		# Write bones
		if len(self.bones) > 0:
			fs.write('  $bones {\n')
			for bone in self.bones:
				boneFixed = bone.replace(' ', '_')
				fs.write(f'    "{boneFixed}"\n')
			fs.write('  }\n')

		# Write meshes
		for meshName, mesh in self.meshes.items():
			fs.write(f'  $mesh "{meshName}" {{\n')
			mesh.Write(fs)
			fs.write('  }\n')

class TxoMesh:

	__slots__ = (
		'texCoordLayers',
		'faces',
		'faceVerts',
		'verts',
		'texCoords',
		'normals'
	)

	def __init__(self):
		self.texCoordLayers:int = 1
		self.faces:list[TxoFace] = []
		self.faceVerts:list[TxoFaceVertex] = []
		self.verts:list[TxoVertex] = []
		self.texCoords:list[FVector2D] = []
		self.normals:list[FVector] = []

	def Read(self, ascr: AsciiReader):

		# Read properties
		while ascr.ReadStrIfPresent('#'):
			if ascr.ReadStrIfPresent('texCoords'):
				ascr.SkipWhitespaces()
				self.texCoordLayers = ascr.ReadInt()
				ascr.SkipWhitespaces()

		global importSettings
		global txoObjectTags

		# Read subobjects
		while ascr.ReadStrIfPresent('$'):

			# Read faces
			if ascr.ReadStrIfPresent('faces'):
				ascr.SkipWhitespaces()
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces()
				while ascr.PeekStr(1) != '}':
					face = TxoFace()
					face.Read(ascr)
					self.faces.append(face)
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces()
			
			# Read faceVerts
			elif ascr.ReadStrIfPresent('faceVerts'):
				ascr.SkipWhitespaces()
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces()
				while ascr.PeekStr(1).isdigit():
					faceVert = TxoFaceVertex()
					faceVert.Read(ascr)
					self.faceVerts.append(faceVert)
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces()
			
			# Read verts
			elif ascr.ReadStrIfPresent('verts'):
				ascr.SkipWhitespaces()
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces()
				while ascr.PeekStr(1) != '}':
					vert = TxoVertex()
					vert.Read(ascr)
					self.verts.append(vert)
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces()
			
			# Read texCoords
			elif ascr.ReadStrIfPresent('texCoords'):
				ascr.SkipWhitespaces()
				if (importSettings.bImportUVs):
					assert ascr.ReadStrIfPresent('{')
					ascr.SkipWhitespaces()
					while ascr.PeekStr(1) != '}':
						x = ascr.ReadFloat()
						ascr.Seek(1)
						y = ascr.ReadFloat()
						ascr.SkipWhitespaces()
						self.texCoords.append(FVector2D(x, y))
					assert ascr.ReadStrIfPresent('}')
				else:
					ascr.SkipScope('{', '}')
				ascr.SkipWhitespaces()
			
			# Read normals
			elif ascr.ReadStrIfPresent('normals'):
				ascr.SkipWhitespaces()
				if importSettings.bImportNormals:
					assert ascr.ReadStrIfPresent('{')
					ascr.SkipWhitespaces()
					idxClose = ascr.Find(b'}', ascr.GetPos())
					while ascr.GetPos() < idxClose:
						normal = ReadTxoVector(ascr)
						ascr.SkipWhitespaces()
						if 'Coords' in txoObjectTags and txoObjectTags['Coords'] == 'XZY':
							normal.swapYZ()
						self.normals.append(normal)
					assert ascr.ReadStrIfPresent('}')
				else:
					ascr.SkipScope('{', '}')
				ascr.SkipWhitespaces()

	def Write(self, fs:StringIO):
		# Write properties
		fs.write(f'   #texCoords {self.texCoordLayers}\n')
		
		# Write faces
		if len(self.faces) > 0:
			fs.write('   $faces {\n')
			for face in self.faces:
				face.Write(fs)
			fs.write('   }\n')

		# Write faceVerts
		if len(self.faceVerts) > 0:
			fs.write('   $faceVerts {\n')
			for faceVert in self.faceVerts:
				faceVert.Write(fs)
			fs.write('   }\n')

		# Write verts
		if len(self.verts) > 0:
			fs.write('   $verts {\n')
			for vert in self.verts:
				vert.Write(fs)
			fs.write('   }\n')

		# Write texCoords
		if len(self.texCoords) > 0:
			fs.write('   $texCoords {\n')
			for texCoord in self.texCoords:
				fs.write(f'     {str(texCoord)}\n')
			fs.write('   }\n')

		# Write normals
		if len(self.normals) > 0:
			fs.write('   $normals {\n')
			for normal in self.normals:
				fs.write(f'     {normal.GetStr(4)}\n')
			fs.write('   }\n')

class TxoFace:

	__slots__ = (
		'idxMaterial',
		'faceVertIndices'
	)

	def __init__(self):
		self.idxMaterial:int = 0
		self.faceVertIndices:list[int] = []
	
	def Read(self, ascr: AsciiReader):
		self.idxMaterial = ascr.ReadInt()
		ascr.Seek(1)
		numVerts = ascr.ReadInt()
		for _ in range(numVerts):
			ascr.Seek(1)
			self.faceVertIndices.append(ascr.ReadInt())
		ascr.SkipWhitespaces()

	def Write(self, fs:StringIO):
		fs.write(f'     {self.idxMaterial} {len(self.faceVertIndices)}')
		for idxFaceVert in self.faceVertIndices:
			fs.write(f' {idxFaceVert}')
		fs.write('\n')

class TxoVertex:

	__slots__ = (
		'pos',
		'weights'
	)

	def __init__(self):
		self.pos:FVector = FVector()
		self.weights:dict[int, float] = {}
	
	def Read(self, ascr: AsciiReader):
		# Read position
		self.pos = ReadTxoVector(ascr)
		ascr.Seek(1)

		global txoObjectTags
		if 'Coords' in txoObjectTags and txoObjectTags['Coords'] == 'XZY':
			self.pos.swapYZ()

		# Read weights
		numWeights = ascr.ReadInt()
		for _ in range(numWeights):
			ascr.Seek(1)
			idxBone = ascr.ReadInt()
			ascr.Seek(1)
			weight = ascr.ReadFloat()
			self.weights[idxBone] = weight
		ascr.SkipWhitespaces()

	def Write(self, fs:StringIO):
		fs.write(f'     {str(self.pos)} {len(self.weights)}')
		for idxBone, weight in self.weights.items():
			fs.write(f' {idxBone} {flt2str(fltRndIfCloseToInt(weight, 1e-3),3)}')
		fs.write('\n')

class TxoFaceVertex:

	__slots__ = (
		'vertIndex',
		'idxList' # unknown ints, 2 or more of them, usually just the its index in faceVerts list
	)

	def __init__(self):
		self.vertIndex:int = 0
		self.idxList:list[int] = []
	
	def Read(self, ascr: AsciiReader):
		self.vertIndex = ascr.ReadInt()
		ascr.Seek(1)
		self.idxList.append(ascr.ReadInt())
		ascr.Seek(1)
		self.idxList.append(ascr.ReadInt())
		ascr.Seek(1)
		while ascr.PeekStr(1).isdigit():
			self.idxList.append(ascr.ReadInt())
		ascr.SkipWhitespaces()
		
	def Write(self, fs:StringIO):
		fs.write(f'     {self.vertIndex}')
		for idx in self.idxList:
			fs.write(f' {idx}')
		fs.write('\n')

class TxoBone:

	__slots__ = (
		'keyframe', # for rest pose
		'children'
	)

	def __init__(self):
		self.keyframe:TxoKeyframe = TxoKeyframe()
		self.children:dict[str, TxoBone] = {}
	
	def Read(self, ascr: AsciiReader, depth:int = 0):
		while ascr.ReadStrIfPresent('$'):
			if ascr.ReadStrIfPresent('frame'):
				ascr.SkipWhitespaces()
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces(depth + 10)
				self.keyframe.Read(ascr)
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces(depth + 10)
			elif ascr.ReadStrIfPresent('node'):
				ascr.SkipWhitespaces()
				childName = ascr.ReadEncapsulatedStr()
				ascr.SkipWhitespaces()
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces(depth + 10)
				child = TxoBone()
				child.Read(ascr, depth + 1)
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces(depth + 10)
				self.children[childName] = child

	def Write(self, fs:StringIO, depth:int = 0):
		# Write keyframe
		fs.write(' ' * (depth + 2))
		fs.write('$frame {\n')
		self.keyframe.Write(fs, depth)
		fs.write(' ' * (depth + 2))
		fs.write('}\n')

		# Write children
		for childName, child in self.children.items():
			fs.write(' ' * (depth + 2))
			childNameFixed = childName.replace(' ', '_')
			fs.write(f'$node "{childNameFixed}" {{\n')
			child.Write(fs, depth + 1)
			fs.write(' ' * (depth + 2))
			fs.write('}\n')

class TxoKeyframe:

	__slots__ = (
		'rotMatrix',
		'offset'
	)

	def __init__(self):
		self.rotMatrix:FMatrix3 = FMatrix3()
		self.offset:FVector = FVector()
	
	def Read(self, ascr:AsciiReader):
		a = ReadTxoVector(ascr)
		ascr.SkipWhitespacesSlow()
		b = ReadTxoVector(ascr)
		ascr.SkipWhitespacesSlow()
		c = ReadTxoVector(ascr)
		ascr.SkipWhitespacesSlow()
		self.rotMatrix.set(a, b, c)
		
		self.offset = ReadTxoVector(ascr)
		ascr.SkipWhitespacesSlow()

		global txoObjectTags
		if 'Coords' in txoObjectTags and txoObjectTags['Coords'] == 'XZY':
			self.offset.swapYZ()

	def Write(self, fs:StringIO, depth:int = 0):
		fs.write(' ' * (depth + 3))
		fs.write(str(self.rotMatrix.a) + '\n')
		fs.write(' ' * (depth + 3))
		fs.write(str(self.rotMatrix.b) + '\n')
		fs.write(' ' * (depth + 3))
		fs.write(str(self.rotMatrix.c) + '\n')
		fs.write(' ' * (depth + 3))
		fs.write(str(self.offset) + '\n')
		
def ReadTxoVector(ascr:AsciiReader) -> FVector:
	x = ascr.ReadFloat()
	ascr.Seek(1)
	y = ascr.ReadFloat()
	ascr.Seek(1)
	z = ascr.ReadFloat()
	return FVector(x, y, z)