class DeltaNumber:
	def __init__(self, value) -> None:
		self.value = value
	

	def __repr__(self) -> str:
		return f"{self.value}"
	

	def abs(self):
		return abs(DeltaNumber(self.value))

	
	def neg(self):
		return DeltaNumber(self.value * -1)


	def add(self, right):
		if isinstance(right, DeltaNumber):
			return DeltaNumber(self.value + right.value)
	

	def subtract(self, right):
		if isinstance(right, DeltaNumber):
			return DeltaNumber(self.value - right.value)
	

	def multiply(self, right):
		if isinstance(right, DeltaNumber):
			return DeltaNumber(self.value * right.value)
	

	def divide(self, right):
		if isinstance(right, DeltaNumber):
			return DeltaNumber(self.value / right.value)
	

	def power(self, right):
		if isinstance(right, DeltaNumber):
			return DeltaNumber(pow(self.value, right.value))
	

	def comp_ee(self, right):
		if isinstance(right, DeltaNumber):
			return DeltaBool(bool(self.value == right.value))
	

	def comp_ne(self, right):
		if isinstance(right, DeltaNumber):
			return DeltaBool(bool(self.value != right.value))
	

	def comp_lr(self, right):
		if isinstance(right, DeltaNumber):
			return DeltaBool(bool(self.value < right.value))


	def comp_gr(self, right):
		if isinstance(right, DeltaNumber):
			return DeltaBool(bool(self.value > right.value))


	def comp_le(self, right):
		if isinstance(right, DeltaNumber):
			return DeltaBool(bool(self.value <= right.value))


	def comp_ge(self, right):
		if isinstance(right, DeltaNumber):
			return DeltaBool(bool(self.value >= right.value))



class DeltaBool:
	def __init__(self, value) -> None:
		self.value = value
	

	def __repr__(self) -> str:
		return str(self.value).lower()
	

	def comp_ee(self, right):
		if isinstance(right, DeltaBool):
			return DeltaBool(bool(self.value == right.value))
	

	def comp_ne(self, right):
		if isinstance(right, DeltaBool):
			return DeltaBool(bool(self.value != right.value))



class DeltaString:
	def __init__(self, value) -> None:
		self.value = value
	

	def __repr__(self) -> str:
		return self.value


	def add(self, right):
		if isinstance(right, DeltaString):
			return DeltaString(self.value + right.value)
	

	def comp_ee(self, right):
		if isinstance(right, DeltaString):
			return DeltaBool(bool(self.value == right.value))
	

	def comp_ne(self, right):
		if isinstance(right, DeltaString):
			return DeltaBool(bool(self.value != right.value))



class DeltaArray:
	def __init__(self, length, value) -> None:
		self.length = length
		self.value = value


	def __repr__(self) -> str:
		return str(self.value)



class DeltaNone:
	def __repr__(self) -> str:
		return "null"



class DeltaScope:
	def __init__(self, statements) -> None:
		self.statements = statements