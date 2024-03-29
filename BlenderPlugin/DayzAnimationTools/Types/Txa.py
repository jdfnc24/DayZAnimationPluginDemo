from io import StringIO
import shutil
from DayzAnimationTools.Utils.AsciiReader import AsciiReader
from DayzAnimationTools.Utils.DayzAnimUtils import *

SURVIVOR_IK_ANIM_BONES_L = \
[
	'LeftHandThumb1', 'LeftHandThumb2', 'LeftHandThumb3', 'LeftHandThumb4',
	'LeftHandIndex1', 'LeftHandIndex2', 'LeftHandIndex3', 'LeftHandIndex4',
	'LeftHandMiddle1', 'LeftHandMiddle2', 'LeftHandMiddle3', 'LeftHandMiddle4',
	'LeftHandRing', 'LeftHandRing1', 'LeftHandRing2', 'LeftHandRing3', 'LeftHandRing4',
	'LeftHandPinky', 'LeftHandPinky1', 'LeftHandPinky2', 'LeftHandPinky3', 'LeftHandPinky4',
	'LeftHandOrigin', 'LeftHand_Dummy', 'LeftForeArmDirection',
	'LeftForeArmDirectionOrigin'
	# Not necessary in blender, information extrapolated
	#'LeftHandIKTarget',
	#'LeftForeArmDirectionOrigin',
]

SURVIVOR_IK_ANIM_BONES_R = \
[
	'RightHandThumb1', 'RightHandThumb2', 'RightHandThumb3', 'RightHandThumb4',
	'RightHandIndex1', 'RightHandIndex2', 'RightHandIndex3', 'RightHandIndex4',
	'RightHandMiddle1', 'RightHandMiddle2', 'RightHandMiddle3', 'RightHandMiddle4',
	'RightHandRing', 'RightHandRing1', 'RightHandRing2', 'RightHandRing3', 'RightHandRing4',
	'RightHandPinky', 'RightHandPinky1', 'RightHandPinky2', 'RightHandPinky3', 'RightHandPinky4',
	'RightHandOrigin', 'RightHand_Dummy', 'RightForeArmDirection',
	'RightForeArmDirectionOrigin'
	# Not necessary in blender, information extrapolated
	#'RightForeArmDirectionOrigin',
]

SURVIVOR_RL_ANIM_BONES = \
[
	'Spine',
	'Spine1',
	'Spine2',
	'Spine3',
	'Neck',
	'Neck1',
	'Head',
	'LeftShoulder',
	'LeftArm',
	'LeftArmRoll',
	'LeftForeArm',
	'LeftForeArmRoll',
	'LeftHand',
	'LeftHandRing',
	'LeftHandRing1',
	'LeftHandRing2',
	'LeftHandRing3',
	'LeftHandMiddle1',
	'LeftHandMiddle2',
	'LeftHandMiddle3',
	'LeftHandIndex1',
	'LeftHandIndex2',
	'LeftHandIndex3',
	'LeftHandThumb1',
	'LeftHandThumb2',
	'LeftHandThumb3',
	'LeftHandPinky',
	'LeftHandPinky1',
	'LeftHandPinky2',
	'LeftHandPinky3',
	'LeftHand_Dummy',
	'LeftWristExtra',
	'LeftForeArmExtra',
	'LeftElbowExtra',
	'LeftArmExtra',
	'RightShoulder',
	'RightArm',
	'RightArmExtra',
	'RightArmRoll',
	'RightForeArm',
	'RightForeArmRoll',
	'RightHand',
	'RightHandRing',
	'RightHandRing1',
	'RightHandRing2',
	'RightHandRing3',
	'RightHandThumb1',
	'RightHandThumb2',
	'RightHandThumb3',
	'RightHandMiddle1',
	'RightHandMiddle2',
	'RightHandMiddle3',
	'RightHandIndex1',
	'RightHandIndex2',
	'RightHandIndex3',
	'RightHandPinky',
	'RightHandPinky1',
	'RightHandPinky2',
	'RightHandPinky3',
	'RightHand_Dummy',
	'RightWristExtra',
	'RightForeArmExtra',
	'RightElbowExtra',
	'Weapon_Trigger',
	'Weapon_Magazine',
	'Weapon_Bone_02',
	'Weapon_Bone_03',
	'Weapon_Bone_04',
	'Weapon_Bone_04',
	'Weapon_Bone_05',
]

SURVIVOR_RL_SKIP_TRANS_ANIM_BONES = \
[
	'Spine',
	'Spine1',
	'Spine2',
	'Spine3',
	'Neck',
	'Neck1',
	'Head'
]

class TxaImportSettings:

	__slots__ = (
		'fUnitScale',
		'bImportTranslationKeys',
		'bImportRotationKeys',
		'bImportScaleKeys'
	)
	
	def __init__(self):
		self.fUnitScale:float = 1.0
		self.bImportTranslationKeys:bool = True
		self.bImportRotationKeys:bool = True
		self.bImportScaleKeys:bool = False

class TxaExportSettings:

	__slots__ = (
		'fUnitScale',
		'bExportTranslationKeys',
		'bExportRotationKeys',
		'bExportScaleKeys',
		'bExportSelectedBonesOnly',
		'bExportShowingBonesOnly',
		'fpsOverride',
		'bSaveAll',
		'sAnimType',
	)
	
	def __init__(self):
		self.fUnitScale:float = 1.0
		self.bExportTranslationKeys:bool = True
		self.bExportRotationKeys:bool = True
		self.bExportScaleKeys:bool = False
		self.bExportSelectedBonesOnly:bool = False
		self.bExportShowingBonesOnly:bool = False
		self.fpsOverride:int = 0
		self.sAnimType:str = 'FB'



importSettings = TxaImportSettings()

class Txa:

	__slots__ = (
		'name',
		'animations'
	)

	def __init__(self):
		self.name:str = ''
		self.animations:dict[str, TxaAnimation] = {}

	def CreateFromFile(filepath=None, inImportSettings = TxaImportSettings()):
		global importSettings
		importSettings = inImportSettings
		txa = Txa()

		buffer = b''
		with open(filepath, 'rb') as fs:
			buffer = fs.read()

		ascr = AsciiReader(buffer)
		txa.Read(ascr)

		return txa

	def Read(self, ascr: AsciiReader):
		ascr.SkipWhitespaces()

		while ascr.ReadStrIfPresent('$'):
			# Read animation
			if ascr.ReadStrIfPresent('animation'):
				ascr.SkipWhitespaces()

				# Read animation name
				txaName = ascr.ReadEncapsulatedStr()
				ascr.SkipWhitespaces()

				# Read entry bracket
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces()

				txaAnimation = TxaAnimation()
				txaAnimation.Read(ascr)

				# Read closing bracket
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces()

				self.animations[txaName] = txaAnimation
	
	def Write(self, filepath = '', inExportSettings = TxaExportSettings()):
		global exportSettings
		exportSettings = inExportSettings

		with StringIO() as fs:
			for txaAnimationName, txaAnimation in self.animations.items():
				fs.write(f'$animation "{txaAnimationName}" {{\n')
				txaAnimation.Write(fs)
				fs.write('}\n')

			# Write stream to file
			with open(filepath, 'w') as fd:
				fs.seek(0)
				shutil.copyfileobj(fs, fd, 1024)

class TxaAnimation:

	__slots__ = (
		'version',
		'fps',
		'numFrames',
		'rootBones',
		'events',
		'custProps'
	)

	def __init__(self):
		self.version:float = 1.0
		self.fps:int = 0
		self.numFrames:int = 0
		self.rootBones:dict[str, TxaBone] = {}
		self.events:list[TxaEvent] = []
		self.custProps:list[TxaCustomProperty] = []

	def Read(self, ascr: AsciiReader):

		# Read properties
		while ascr.ReadStrIfPresent('#'):
			if ascr.ReadStrIfPresent('version'):
				ascr.SkipWhitespaces()
				self.version = ascr.ReadFloat()
				ascr.SkipWhitespaces()
			elif ascr.ReadStrIfPresent('fps'):
				ascr.SkipWhitespaces()
				self.fps = ascr.ReadInt()
				ascr.SkipWhitespaces()
			elif ascr.ReadStrIfPresent('numFrames'):
				ascr.SkipWhitespaces()
				self.numFrames = ascr.ReadInt()
				ascr.SkipWhitespaces()
		
		# Read subobjects
		while ascr.ReadStrIfPresent('$'):
			
			# Read root bone
			if ascr.ReadStrIfPresent('node'):
				ascr.SkipWhitespaces()
				txaBoneName = ascr.ReadEncapsulatedStr()
				ascr.SkipWhitespaces()
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces()
				txaBone = TxaBone()
				txaBone.Read(ascr)
				self.rootBones[txaBoneName] = txaBone
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces()

			# Read events
			elif ascr.ReadStrIfPresent('events'):
				ascr.SkipWhitespaces()

				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces()

				while ascr.ReadStrIfPresent('#event'):
					ascr.SkipWhitespaces()
					event = TxaEvent()
					event.Read(ascr)
					self.events.append(event)
					ascr.SkipWhitespaces()

				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces()
			
			# Read custom properties
			elif ascr.ReadStrIfPresent('custProps'):
				ascr.SkipWhitespaces()

				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces()

				while ascr.ReadStrIfPresent('#custProp'):
					ascr.SkipWhitespaces()
					prop = TxaCustomProperty()
					prop.Read(ascr)
					self.custProps.append(prop)
					ascr.SkipWhitespaces()

				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces()

	def Write(self, fs:StringIO):
			# Write properties
			#fs.write(f' #version {self.version}\n') # Not needed as there is only one version (1.0)
			fs.write(f' #fps {self.fps}\n')
			fs.write(f' #numFrames {self.numFrames}\n')

			# Write bones
			for rootBoneName, rootBone in self.rootBones.items():
				fs.write(f' $node "{rootBoneName}" {{\n')
				rootBone.Write(fs)
				fs.write(' }\n')

			# Write events
			if len(self.events):
				fs.write(f' $events {{\n')
				for event in self.events:
					event.Write(fs)
				fs.write('}\n')

			# Write custom properties
			if len(self.custProps):
				fs.write(f' $custProps {{\n')
				for custProp in self.custProps:
					custProp.Write(fs)
				fs.write('}\n')

class TxaBone:

	__slots__ = (
		'keyframes',
		'children'
	)

	def __init__(self):
		self.keyframes:list[TxaKeyframe] = []
		self.children:dict[str, TxaBone] = {}
	
	def Read(self, ascr: AsciiReader, depth:int = 0):

		while ascr.ReadStrIfPresent('$'):

			# Read keyframe
			if ascr.ReadStrIfPresent('keys t q s'):
				ascr.SkipWhitespaces()

				# open keys subobject
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces(depth + 10)

				while ascr.ReadStrIfPresent('$frame'):
					ascr.SkipWhitespaces()

					kf = TxaKeyframe()
					kf.frameStart = ascr.ReadInt()
					ascr.SkipWhitespaces()

					if ascr.PeekStr(1).isnumeric():
						kf.frameEnd = ascr.ReadInt()
						ascr.SkipWhitespaces()

					# open frame subobject
					assert ascr.ReadStrIfPresent('{')
					ascr.SkipWhitespaces(depth + 10)

					kf.Read(ascr, depth)
					self.keyframes.append(kf)

					# close frame subobject
					assert ascr.ReadStrIfPresent('}')
					ascr.SkipWhitespaces(depth + 10)
				
				# close keys subobject
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces(depth + 10)
				
			elif ascr.ReadStrIfPresent('node'):
				ascr.SkipWhitespaces()
				childName = ascr.ReadEncapsulatedStr()
				ascr.SkipWhitespaces()
				assert ascr.ReadStrIfPresent('{')
				ascr.SkipWhitespaces(depth + 10)
				child = TxaBone()
				child.Read(ascr, depth + 1)
				assert ascr.ReadStrIfPresent('}')
				ascr.SkipWhitespaces(depth + 10)
				self.children[childName] = child

	def Write(self, fs:StringIO, depth:int = 0):
		# Write keys
		fs.write(' ' * (depth + 2))
		fs.write('$keys t q s {\n')
		for kf in self.keyframes:
			kf.Write(fs, depth)
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

class TxaKeyframe:

	__slots__ = (
		'frameStart',
		'frameEnd',
		'translation',
		'rotation',
		'scale'
	)

	def __init__(self):
		self.frameStart:int = 0
		self.frameEnd:int = 0
	
	def HasTranslation(self) -> bool:
		return hasattr(self, 'translation')
	
	def HasRotation(self) -> bool:
		return hasattr(self, 'rotation')
	
	def HasScale(self) -> bool:
		return hasattr(self, 'scale')
	
	def __str__(self):
		ret = '(t: '
		if self.HasTranslation():
			ret += str(self.translation)
		else:
			ret += 'None'
		if self.HasRotation():
			ret += ', q: ' + str(self.rotation)
		else:
			ret += ', None'
		if self.HasScale():
			ret += ', s: ' + str(self.scale)
		else:
			ret += ', None'
		ret += ')'

		return ret
	
	def __repr__(self): return str(self)
	
	def Read(self, ascr: AsciiReader, depth:int = 0):
		while ascr.ReadStrIfPresent('#'):
			# read translation
			if ascr.ReadStrIfPresent('t'):
				ascr.SkipWhitespaces()
				self.translation = ReadTxaVector(ascr)
				ascr.SkipWhitespaces(depth + 10)
			
			# read quaternion rotation
			elif ascr.ReadStrIfPresent('q'):
				ascr.SkipWhitespaces()
				self.rotation = ReadTxaQuaternion(ascr)
				ascr.SkipWhitespaces(depth + 10)
			
			# read scale
			elif ascr.ReadStrIfPresent('s'):
				ascr.SkipWhitespaces()
				self.scale = ReadTxaVector(ascr)
				ascr.SkipWhitespaces(depth + 10)

	def Write(self, fs:StringIO, depth:int = 0):
		fs.write(' ' * (depth + 3))
		if self.frameStart == self.frameEnd:
			fs.write(f'$frame {self.frameStart} {{\n')
		else:
			fs.write(f'$frame {self.frameStart} {self.frameEnd} {{\n')
		if self.HasTranslation():
			fs.write(' ' * (depth + 4))
			fs.write(f'#t {str(self.translation.GetSwapYZ())}\n')
		if self.HasRotation():
			fs.write(' ' * (depth + 4))
			rotFixed = FQuaternion(self.rotation.x, self.rotation.z, self.rotation.y, -self.rotation.w)
			fs.write(f'#q {str(rotFixed)}\n')
		if self.HasScale():
			fs.write(' ' * (depth + 4))
			fs.write(f'#s {str(self.scale.GetSwapYZ())}\n')
		fs.write(' ' * (depth + 3))
		fs.write('}\n')

class TxaEvent:

	__slots__ = (
		'frame',
		'name',
		'userString',
		'userInt'
	)

	def __init__(self):
		self.frame:int = 0
		self.name:str = ''
		self.userString:str = ''
		self.userInt:int = -1
	
	def Read(self, ascr: AsciiReader):
		self.frame = ascr.ReadInt()
		ascr.SkipWhitespaces()
		self.name = ascr.ReadEncapsulatedStr()
		ascr.SkipWhitespaces()
		self.userString = ascr.ReadEncapsulatedStr()
		ascr.SkipWhitespaces()
		self.userInt = ascr.ReadInt()
		ascr.SkipWhitespaces()

	def Write(self, fs:StringIO):
		fs.write(f'  #event {self.frame} "{self.name}" "{self.userString}" {self.userInt}\n')

	def __str__(self): return f'{self.name}|{self.userString}|{self.userInt}'
	def __repr__(self): return str(self)

class TxaCustomProperty:

	__slots__ = (
		'name',
		'value'
	)

	def __init__(self):
		self.name:str = ''
		self.value:str = ''
	
	def Read(self, ascr: AsciiReader):
		self.name = ascr.ReadEncapsulatedStr()
		ascr.SkipWhitespaces()
		self.value = ascr.ReadEncapsulatedStr()
		ascr.SkipWhitespaces()

	def Write(self, fs:StringIO):
		fs.write(f'  #custProp "{self.name}" "{self.value}"\n')

def ReadTxaVector(ascr:AsciiReader) -> FVector:
	x = ascr.ReadFloat()
	ascr.Seek(1)
	z = ascr.ReadFloat()
	ascr.Seek(1)
	y = ascr.ReadFloat()
	return FVector(x, y, z)
		
def ReadTxaQuaternion(ascr:AsciiReader) -> FQuaternion:
	x = ascr.ReadFloat()
	ascr.Seek(1)
	z = ascr.ReadFloat()
	ascr.Seek(1)
	y = ascr.ReadFloat()
	ascr.Seek(1)
	w = -ascr.ReadFloat()
	return FQuaternion(w, x, y, z)