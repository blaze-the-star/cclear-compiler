
from enum import IntEnum, auto

class CmdTypes(IntEnum):
	ERROR:int				= auto()
	EMPTY:int				= auto()
	IDENTIFIER:int			= auto()
	BINARY_EXPRESSION:int	= auto()
	NUMERIC_LITERAL:int		= auto()
	VAR_NAME:int			= auto()
	VAR_OPTIONS:int			= auto()
	VAR_DECLATION:int		= auto()
	OBJ_TYPE:int			= auto()
	
class Command:
	type:int = -1
	scope:int = -1

	def __init__(self, type:int=-1, scope:int=-1, msg:str="") -> None:
		if type != -1:
			self.type = type

		if self.type == CmdTypes.ERROR:
			breakpoint()

		self.scope = scope
		self.message = msg

	def __str__(self) -> str:
		return "<Command, type:%s>" % self.type

	def is_error(self) -> bool:
		return self.type == CmdTypes.ERROR

	def is_empty(self) -> bool:
		return self.type == CmdTypes.EMPTY

	def source(self) -> list:
		return []

class CmdEmpty(Command):
	type:int = CmdTypes.EMPTY

	def __str__(self) -> str:
		""

class CmdError(Command):
	type:int = CmdTypes.ERROR
	msg:str = ""

	def __init__(self, msg:str="") -> None:
		self.msg = msg
		breakpoint()

	def __str__(self) -> str:
		return "<Command Error: %s>" % self.msg

class CmdIdentifier(Command):
	type:int = CmdTypes.IDENTIFIER
	value:str = ""

	def __init__(self, value:str="") -> None:
		self.value = value

	def __str__(self) -> str:
		return self.value

	def source(self) -> list:
		return [self.value]

class CmdNumericLiteral(Command):
	type:int = CmdTypes.NUMERIC_LITERAL
	value:str = ""

	def __init__(self, value:str="") -> None:
		self.value = value

	def __str__(self) -> str:
		return self.value

	def source(self) -> list:
		return [self.value]

class CmdBinaryExpression(Command):
	type:int = CmdTypes.BINARY_EXPRESSION
	op:str = ""
	left:Command = CmdEmpty()
	right:Command = CmdEmpty()

	def __init__(self, op:str="", left:Command=CmdEmpty(), right:Command=CmdEmpty()) -> None:
		self.op = op
		
		if left != None:
			self.left = left

		if right != None:
			self.right = right

	def __str__(self) -> str:
		return str(self.left) + self.op + str(self.right)

	def source(self) -> list:
		return self.left.source() + [self.op] + self.right.source()

class CmdTokenList(Command):
	type:int = -1
	keys:list = []

	def __init__(self, keys:list=[]) -> None:
		self.keys = keys

	def __str__(self) -> str:
		ret:str = ""
		for key in self.keys:
			ret += key
		return ret

	def source(self) -> list:
		return self.keys

class CmdGroup(Command):
	type:int = CmdTypes.NUMERIC_LITERAL
	value:Command = CmdEmpty()
	left:str = ""
	right:str = ""

	def __init__(self, value:Command=CmdEmpty(), left:str="", right:str="") -> None:
		self.value = value
		self.left = left
		self.right = right

	def __str__(self) -> str:
		return self.left + str(self.value) + self.right

	def source(self) -> list:
		return [self.left] + self.value.source() + [self.right]

class CmdVarDeclaration(Command):
	type:int = CmdTypes.VAR_DECLATION
	cmd_options:Command = CmdEmpty()
	cmd_name:Command = CmdEmpty()
	cmd_type:Command = CmdEmpty()
	cmd_asignment:Command = CmdEmpty()

	def __init__(self, cmd_options=CmdEmpty(), cmd_name=CmdEmpty(), 
		cmd_type=CmdEmpty(), cmd_asignment=CmdEmpty()) -> None:
		self.cmd_options = cmd_options
		self.cmd_name = cmd_name
		self.cmd_type = cmd_type
		self.cmd_asignment = cmd_asignment

	def __str__(self) -> str:
		return "alc "+str(self.cmd_options)+" "+str(self.cmd_name)+":"+str(self.cmd_type)+" "+self.cmd_asignment+";"

	def source(self) -> list:
		return ["alc"] + self.cmd_options.source() + self.cmd_name.source() + \
			[":"] + self.cmd_type.source() + self.cmd_asignment.source() + [";"]