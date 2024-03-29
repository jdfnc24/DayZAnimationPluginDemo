
# Helpers to facilitate modularity of this program, for use of txo/txa outside of blender

def flt2str(number:float, precision=7):
	ret = '{0:.{prec}f}'.format(number, prec=precision).rstrip('0') or '0.0'
	if ret[len(ret) - 1] == '.': ret += '0'
	if float(ret) == 0.0: return '0.0'
	return ret

def fltRndIfCloseToInt(number:float, tolerance = 1e-4) -> float:
	closestInteger = float(round(number))
	if abs(number - closestInteger) <= tolerance:
		return closestInteger
	else:
		return number
	
class FVector():

	__slots__ = ( 'x', 'y', 'z' )

	def __init__(self, value:float):
		self.set(value, value, value)

	def __init__(self, x:float = 0.0, y:float = 0.0, z:float = 0.0):
		self.set(x,y,z)

	def set(self, x:float, y:float, z:float):
		self.x:float = x
		self.y:float = y
		self.z:float = z
	
	def toTuple(self) -> tuple[float, float, float]:
		return (self.x, self.y, self.z)
	
	def swapYZ(self):
		self.set(self.x, self.z, self.y)
	
	def GetSwapYZ(self):
		return FVector(self.x, self.z, self.y)
	
	def Mult(self, value:float):
		self.set(self.x * value, self.y * value, self.z * value)
	
	def GetStr(self, precision=7) -> str:
		x = flt2str(fltRndIfCloseToInt(self.x), precision)
		y = flt2str(fltRndIfCloseToInt(self.y), precision)
		z = flt2str(fltRndIfCloseToInt(self.z), precision)
		return f'{x} {y} {z}'
	
	def zero(): return FVector()
	def one(): return FVector(1.0,1.0,1.0)
	def aside(): return FVector(1.0,0.0,0.0)
	def up(): return FVector(0.0,1.0,0.0)
	def foward(): return FVector(0.0,0.0,1.0)

	def NearlyEquals(self, other, tolerance = 1e-04) -> bool:
		if not isinstance(other, self.__class__): return False
		if abs(self.x - other.x) >= tolerance: return False
		if abs(self.y - other.y) >= tolerance: return False
		if abs(self.z - other.z) >= tolerance: return False
		return True

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.x == other.x and self.y == other.y and self.z == other.z
		else:
			return False

	def __ne__(self, other): return not self.__eq__(other)
	def __str__(self): return self.GetStr()
	def __repr__(self): return str(self)
	def __add__(self, other): return FVector(self.x + other.x, self.y + other.y, self.z + other.z)
	def __sub__(self, other): return FVector(self.x - other.x, self.y - other.y, self.z - other.z)
	def __mult__(self, other): return FVector(self.x * other.x, self.y * other.y, self.z * other.z)
	def __truediv__(self, other): return FVector(self.x / other.x, self.y / other.y, self.z / other.z)



class FVector2D:

	__slots__ = ( 'x', 'y' )

	def __init__(self, x:float = 0.0, y:float = 0.0):
		self.set(x,y)

	def set(self, x:float, y:float):
		self.x:float = x
		self.y:float = y
	
	def toTuple(self) -> tuple[float, float]:
		return (self.x, self.y)
	
	def GetStr(self, precision=5) -> str:
		x = flt2str(fltRndIfCloseToInt(self.x), precision)
		y = flt2str(fltRndIfCloseToInt(self.y), precision)
		return f'{x} {y}'
	
	def zero(): return FVector2D()

	def __str__(self): return self.GetStr()
	def __repr__(self): return str(self)
	def __add__(self, other): return FVector2D(self.x + other.x, self.y + other.y)
	def __sub__(self, other): return FVector2D(self.x - other.x, self.y - other.y)
	def __mult__(self, other): return FVector2D(self.x * other.x, self.y * other.y)
	def __truediv__(self, other): return FVector2D(self.x / other.x, self.y / other.y)

class FMatrix3:

	__slots__ = ( 'a', 'b', 'c' )

	def __init__(self, a:FVector, b:FVector, c:FVector):
		self.a:FVector = a
		self.b:FVector = b
		self.c:FVector = c
		
	def __init__(self):
		self.set(
			FVector.aside(),
			FVector.up(),
			FVector.foward()
		)

	def identity():
		return FMatrix3(
			FVector.aside(),
			FVector.up(),
			FVector.foward()
		)

	def set(self, a:FVector, b:FVector, c:FVector):
		self.a:FVector = a
		self.b:FVector = b
		self.c:FVector = c
		
class FQuaternion:

	__slots__ = ( 'w', 'x', 'y', 'z' )

	def __init__(self, w:float = 1.0, x:float = 0.0, y:float = 0.0, z:float = 0.0):
		self.set(w,x,y,z)

	def set(self, w:float, x:float, y:float, z:float):
		self.w:float = w
		self.x:float = x
		self.y:float = y
		self.z:float = z
	
	def toTuple(self) -> tuple[float, float, float, float]:
		return (self.w, self.x, self.y, self.z)
	
	def GetStr(self, precision=7) -> str:
		w = flt2str(fltRndIfCloseToInt(self.w), precision)
		x = flt2str(fltRndIfCloseToInt(self.x), precision)
		y = flt2str(fltRndIfCloseToInt(self.y), precision)
		z = flt2str(fltRndIfCloseToInt(self.z), precision)
		return f'{w} {x} {y} {z}'
	
	def identity(): return FQuaternion()

	def NearlyEquals(self, other, tolerance = 1e-04) -> bool:
		if not isinstance(other, self.__class__): return False
		if abs(self.w - other.w) >= tolerance: return False
		if abs(self.x - other.x) >= tolerance: return False
		if abs(self.y - other.y) >= tolerance: return False
		if abs(self.z - other.z) >= tolerance: return False
		return True

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.w == other.w and self.x == other.x and self.y == other.y and self.z == other.z
		else:
			return False

	def __ne__(self, other): return not self.__eq__(other)
	def __str__(self): return self.GetStr()
	def __repr__(self): return str(self)