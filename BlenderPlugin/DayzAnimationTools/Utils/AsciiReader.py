from io import BytesIO
import struct

class AsciiReader:
	def __init__(self, buffer:bytes):
		self.Buffer = buffer
		self.BaseStream = BytesIO(self.Buffer)

	def Read(self, *args) -> bytes:
		return self.BaseStream.read(*args)
	
	def Find(self, *args) -> int:
		return self.Buffer.find(*args)

	def GetPos(self) -> int:
		return self.BaseStream.tell()

	def SetPos(self, pos: int):
		self.BaseStream.seek(pos)

	def Seek(self, offset):
		self.SetPos(self.GetPos() + offset)
	
	def ReadStr(self, numToRead:int) -> str:
		assert numToRead > 0
		try:
			readBytes = self.BaseStream.read(numToRead)
			readStruct = struct.unpack('<' + "%is" % (numToRead), readBytes)[0]
			readStr = readStruct.decode("ascii")
			return readStr
		except:pass
		return ''
	
	def PeekStr(self, numToRead:int) -> str:
		ret:str = ''
		assert numToRead > 0
		startPos = self.GetPos()
		ret = self.ReadStr(numToRead)
		self.SetPos(startPos)
		return ret

	def ReadStrIfPresent(self, toRead:str) -> bool:
		startPos = self.GetPos()
		try:
			assert len(toRead) > 0
			readStr = self.ReadStr(len(toRead))
			if readStr == toRead:
				return True
		except:pass

		self.SetPos(startPos)
		return False
	
	def ReadEncapsulatedStr(self, encapsulator:str = '"') -> str:
		ret:str = ''
		if self.ReadStrIfPresent(encapsulator):
			while True:
				if self.ReadStrIfPresent(encapsulator):
					break
				else:
					ret += self.ReadStr(1)
		return ret
	
	def ReadEncapsulatedStrIfPresent(self, toRead:str, encapsulator:str = '"') -> bool:
		if self.ReadStrIfPresent(encapsulator):
			if self.ReadStrIfPresent(toRead):
				if self.ReadStrIfPresent(encapsulator):
					return True
		return False
	
	def ReadVariableName(self) -> str:
		ret = self.ReadStr(1)
		assert ret.isalpha() or ret == '_'
		while True:
			c = self.PeekStr(1)
			if c.isalnum() or c == '_':
				ret += c
				self.Seek(1)
			else:
				break
		return ret


	def ReadInt(self) -> int:
		ret = self.ReadStr(1)
		assert ret == '-' or ret.isdigit()
		while True:
			c = self.ReadStr(1)
			if c.isdigit():
				ret += c
			else:
				self.Seek(-1)
				break
		
		return int(ret)

	def ReadFloat(self) -> float:
		ret = self.ReadStr(1)
		assert ret == '-' or ret.isdigit()
		bHasDecimal = False
		while True:
			c = self.ReadStr(1)
			if (not bHasDecimal and c == '.') or c.isdigit():
				ret += c
			else:
				self.Seek(-1)
				break
			
		return float(ret)

	def SkipWhitespacesSlow(self):
		while True:
			c = self.ReadStr(1)
			if not c.isspace():
				self.Seek(-1)
				break
	
	def SkipWhitespaces(self, searchSize:int = 10):
		overflow = self.GetPos() + searchSize - len(self)
		if (overflow > 0):
			searchSize -= overflow
		
		buffer = self.ReadStr(searchSize)
		stripped = buffer.lstrip()
		numWhiteSpaces = len(buffer) - len(stripped)
		if numWhiteSpaces != searchSize:
			self.Seek(numWhiteSpaces - searchSize)
	
	def ReadUntil(self, until:str) -> bool:
		pos = self.GetPos()
		idx = self.Buffer.find(until, pos)
		if idx != -1:
			self.SetPos(idx)
			return True
		return False
	
	def SkipScope(self, scopeOpener:str, scopeCloser:str):
		assert self.ReadStr(len(scopeOpener)) == scopeOpener
		scopes = 1
		while scopes > 0:
			idxOpen = self.Buffer.find(b'{', self.GetPos())
			idxClose = self.Buffer.find(b'}', self.GetPos())
			if idxOpen < idxClose and idxOpen != -1:
				scopes += 1
				self.SetPos(idxOpen + 1)
			else:
				scopes -= 1
				self.SetPos(idxClose + 1)

	def __len__(self):
		return len(self.Buffer)
