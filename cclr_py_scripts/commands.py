
from enum import IntEnum, auto

try:
	from cclr_py_scripts.lexer import Token
except:
	from lexer import Token


class CmdTypes(IntEnum):
	ERROR:int				= auto()
	EMPTY:int				= auto()
	SCRIPT:int				= auto()
	IDENTIFIER:int			= auto()
	BINARY_EXPRESSION:int	= auto()
	NUMERIC_LITERAL:int		= auto()
	OBJ_TYPE:int			= auto()
	VARIABLE:int			= auto()
	ASSIGNMENT:int			= auto()
	DECLARATION:int			= auto()
	NO_TYPE:int				= auto()
	

class CmdEmpty: pass


class Command:
	type:int = CmdTypes.NO_TYPE
	scope:int = CmdTypes.NO_TYPE

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

class CommandList:
	commands:list = []

	def __bool__(self):
		return self.commands.__bool__()

	def __getitem__(self, key):
		return self.commands[key]

	def __init__(self, commands:list=[]) -> None:
		self.commands = commands

	def __iter__(self):
		return self.commands.__iter__()

	def __len__(self):
		return self.commands.__len__()

	def __setitem__(self, key, value):
		self.commands[key] = value

	def __sizeof__(self) -> int:
		return self.commands.__sizeof__()

	def __str__(self) -> str:
		string:str = ""
		for cmd in self.commands:
			string += str(cmd) + " "
		return string[:-1]

class CmdBinaryExpression(Command):
	type:int = CmdTypes.BINARY_EXPRESSION
	op:Token = ""
	left:Command = CmdEmpty()
	right:Command = CmdEmpty()

	def __init__(self, op:Token="", left:Command=CmdEmpty(), right:Command=CmdEmpty()) -> None:
		self.op = op
		
		if left != None:
			self.left = left

		if right != None:
			self.right = right

	def __str__(self) -> str:
		string:str = ""
		if not self.left.is_empty():
			string += str(self.left) + " "
		return string + str(self.op) +" "+ str(self.right)

	def source(self) -> list:
		return self.left.source() + [self.op] + self.right.source()

class CmdEmpty(Command):
	type:int = CmdTypes.EMPTY
	cursor:int = -1

	def __str__(self) -> str:
		return ""

class CmdError(Command):
	type:int = CmdTypes.ERROR
	msg:str = ""
	token:Token = None

	def __init__(self, token:Token, msg:str="") -> None:
		self.msg = msg
		self.token = token
		print(str(self))
		breakpoint()

	def __str__(self) -> str:
		return "Error in line %s col %s : %s"%(self.token.row, self.token.col, self.msg)

class CmdGroup(Command):
	left:Command = CmdEmpty()
	right:Command = CmdEmpty()
	pre_op:str = "NA"
	pos_op:str = "NA"
	op:str = "NA"

	def __init__(self, type:int=CmdTypes.NO_TYPE, left:Command=CmdEmpty(), right:Command=CmdEmpty(), pre_op:str="NA", pos_op:str="NA", op:str="NA") -> None:
		self.type = type
		self.left = left
		self.right = right
		self.pre_op = pre_op
		self.pos_op = pos_op
		self.op = op

	def __str__(self) -> str:
		string:str = ""
		if self.pre_op != "NA":
			string += self.pre_op + " "
		if not self.left.is_empty():
			string += str(self.left) + " "
		if self.op != "NA":
			string += self.op + " "
		if not self.right.is_empty():
			string += str(self.right) + " "
		if self.pos_op != "NA":
			string += self.pos_op + " "
		string = string[:-1]
		return string

	def source(self) -> list:
		assert(False, "Not implemented")
		return [self.pre_op] + self.left.source() + [self.pos_op]

class CmdIdentifier(Command):
	type:int = CmdTypes.IDENTIFIER
	value:Token = None

	def __init__(self, value:str="") -> None:
		self.value = value

	def __str__(self) -> str:
		return self.value.text

	def source(self) -> list:
		return [self.value]

class CmdNumericLiteral(Command):
	type:int = CmdTypes.NUMERIC_LITERAL
	value:Token = ""

	def __init__(self, value:Token="") -> None:
		self.value = value

	def __str__(self) -> str:
		return str(self.value)

	def source(self) -> list:
		return [self.value]

class CmdScript(Command):
	type:int = CmdTypes.SCRIPT
	commands:list = []

	def __init__(self, commands:list=[]) -> None:
		self.commands = commands

	def __str__(self) -> str:
		ret:str = ""
		for command in self.commands:
			ret += str(command) + " "
		return ret[:-1]

class CmdTokenList(Command):
	type:int = -1
	keys:list = []

	def __init__(self, keys:list=[]) -> None:
		self.keys = keys

	def __str__(self) -> str:
		ret:str = ""
		for key in self.keys:
			ret += key.text + " "
		ret = ret[0:-1]
		return ret

	def source(self) -> list:
		return self.keys

class CmdVarDeclaration(Command):
	type:int = CmdTypes.DECLARATION
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
		string:str = "alc"+str(self.cmd_options)+" "+str(self.cmd_name)+":"+str(self.cmd_type)
		if not self.cmd_asignment.is_empty():
			string += " "+str(self.cmd_asignment)
		return string + ";\n"

	def source(self) -> list:
		return ["alc"] + self.cmd_options.source() + self.cmd_name.source() + \
			[":"] + self.cmd_type.source() + self.cmd_asignment.source() + [";"]