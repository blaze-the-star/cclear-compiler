
from enum import IntEnum, auto
from dataclasses import dataclass, field

try:
	from lexer import Token
except:
	from cclr_py_scripts.lexer import Token	

class CmdTypes(IntEnum):
	ERROR:int				= auto()
	EMPTY:int				= auto()

	SCRIPT:int				= auto()
	CODE_BLOCK:int			= auto()

	IDENTIFIER:int			= auto() # Delete?

	BINARY_EXPRESSION:int	= auto()
	NUMERIC_LITERAL:int		= auto()

	TYPE_NAME:int			= auto()
	VARIABLE_NAME:int		= auto()
	MTHD_NAME:int			= auto()
	PARAMS:int				= auto()
	VAR_TYPE_SPECI:int		= auto()

	ASSIGNMENT:int			= auto()
	DECLARATION:int			= auto()

	FLOW_START:int			= auto()
	FLOW_BLOCK:int			= auto()
	FLOW_STATMENT:int		= auto()

	MTHD_BLOCK:int			= auto()
	MTHD_STATMENT:int		= auto()
	MTHD_PARAMS:int			= auto()

	NO_TYPE:int				= auto()
	
@dataclass
class Command:
	type:int = CmdTypes.NO_TYPE
	indent:int = -1

	def __bool__(self) -> bool:
		return not self.is_empty()

	def __str__(self) -> str:
		return f"<'__str__' was not implemented in {self.__class__.__name__}>"

	def first_token(self) -> Token:
		breakpoint()
		assert(False, "Implement this!")

	def get_line(self) -> int: # Starting line of this command
		breakpoint()
		assert(False, "Implement this!")
		return -1

	def indents_str(self) -> str:
		string = ""
		for x in range(self.indent):
			string += "\t"
		return string

	def is_error(self) -> bool:
		return self.type == CmdTypes.ERROR

	def is_empty(self) -> bool:
		return self.type == CmdTypes.EMPTY

	def source(self) -> list:
		return []

@dataclass
class CmdEmpty(Command):
	
	def __post_init__(self) -> None:
		self.type = CmdTypes.EMPTY

	def __str__(self) -> str:
		return ""

	def cpp(self) -> str:
		return ""

	def hpp(self) -> str:
		return ""

#class CommandList:
#	commands:list = []
#
#	def __bool__(self):
#		return self.commands.__bool__()
#
#	def __getitem__(self, key):
#		return self.commands[key]
#
#	def __init__(self, commands:list=[]) -> None:
#		self.commands = commands
#
#	def __iter__(self):
#		return self.commands.__iter__()
#
#	def __len__(self):
#		return self.commands.__len__()
#
#	def __setitem__(self, key, value):
#		self.commands[key] = value
#
#	def __sizeof__(self) -> int:
#		return self.commands.__sizeof__()
#
#	def __str__(self) -> str:
#		string:str = ""
#		for cmd in self.commands:
#			string += str(cmd) + " "
#		return string[:-1]

@dataclass
class CmdGroup(Command):
	left:Command = CmdEmpty()
	right:Command = CmdEmpty()
	pre_op:str = "NA"
	pos_op:str = "NA"
	op:str = "NA"

	def __str__(self) -> str:
		string:str = ""
		if self.pre_op != "NA":
			string += f"{self.pre_op} "
		if not self.left.is_empty():
			string += str(self.left) + " "
		if self.op != "NA":
			string += str(self.op) + " "
		if not self.right.is_empty():
			string += str(self.right) + " "
		if self.pos_op != "NA":
			string += f"{self.pos_op} "
		string = string[:-1]
		return string

	def first_token(self) -> Token:
		if self.pre_op != "NA" and self.pre_op != "PASS":
			return self.pre_op
		if not self.left.is_empty():
			return self.left.first_token()
		if self.op != "NA" and self.op != "PASS":
			return self.op
		if not self.right.is_empty():
			return self.right.first_token()
		if self.pos_op != "NA" and self.pos_op != "PASS":
			return self.pos_op

		raise "err"

	def get_line(self) -> int: # Starting line of this command
		if not self.left.is_empty():
			return self.left.get_line()
		if self.op != "NA" and self.op != "PASS":
			return self.op.row
		if not self.right.is_empty():
			return self.right.get_line()

	def source(self) -> list:
		assert(False, "Not implemented")
		return [self.pre_op] + self.left.source() + [self.pos_op]

@dataclass
class CmdToken(Command):
	token:Token = None

	def __str__(self) -> str:
		return self.token.text

	def cpp(self) -> str:
		return str(self.token)

	def hpp(self) -> str:
		return str(self.token)

	def first_token(self) -> Token:
		return self.token

	def source(self) -> list:
		return [self.token]

@dataclass
class CmdTokenList(Command):
	keys:list[Token] = field(default_factory=list[Token])

	def __str__(self) -> str:
		ret:str = ""
		for key in self.keys:
			ret += key.text + " "
		ret = ret[0:-1]
		return ret

	def source(self) -> list:
		return self.keys

# =============================================================================
# === Statements ===
# =============================================================================

class CmdBinaryExpression: pass # Pre-define

@dataclass
class CmdNumericLiteral(Command):
	value:Token = ""

	def __str__(self) -> str:
		return str(self.value)

	def cpp(self) -> str:
		return f"{self.value}"

	def hpp(self) -> str:
		return self.hpp()

	def first_token(self) -> Token:
		return self.value

	def get_line(self) -> int: # Starting line of this command
		return self.value.row

	def source(self) -> list:
		return [self.value]

@dataclass
class CmdAssign(Command):
	cmd_expr:CmdBinaryExpression = CmdEmpty()
	equator:Token = Token()

	def __str__(self) -> str:
		return f"{self.equator} {self.cmd_expr}"

	def cpp(self) -> str:
		return f" {self.equator} {self.cmd_expr.cpp()}"

	def hpp(self) -> str:
		return f" {self.equator} {self.cmd_expr.hpp()}"

	def first_token(self) -> Token:
		return self.var_name()

@dataclass
class CmdVarTypeSpeci(Command):
	var_name:Token = Token()
	type_name:Token = Token()
	op:Token = Token()

	def __str__(self) -> str:
		return f"{self.var_name}{self.op}{self.type_name}"

	def cpp(self) -> str:
		return f"{self.type_name} {self.var_name}"

	def hpp(self) -> str:
		return self.cpp()

	def first_token(self) -> Token:
		return self.var_name()

@dataclass
class CmdCodeBlk(Command):
	body:list[Command] = field(default_factory=list[Command])

	def __str__(self) -> str:
		ret:str = ""
		for command in self.body:
			ret += str(command) + " "
		return ret[:-1]

	def cpp(self) -> str:
		indents = self.indents_str()
		string = indents+"{\n"
		for st in self.body:
			string += st.cpp()
		string += str(indents)+"}\n"
		return string

	def hpp(self) -> str:
		indents = self.indents_str()
		string = indents+"{\n"
		for st in self.body:
			string += st.hpp()
		string += str(indents)+"}\n"
		return string

	def first_token(self) -> Token:
		return self.body[0].first_token()

@dataclass
class CmdBinaryExpression(Command):
	op:Token = ""
	left:Command = CmdEmpty()
	right:Command = CmdEmpty()

	def __str__(self) -> str:
		string:str = ""
		if not self.left.is_empty():
			string += str(self.left) + " "
		return string + str(self.op) +" "+ str(self.right)

	def cpp(self) -> str:
		return f"{self.left.cpp()} {self.op} {self.right.cpp()}"

	def hpp(self) -> str:
		return f"{self.left.hpp()} {self.op} {self.right.hpp()}"

	def source(self) -> list:
		return self.left.source() + [self.op] + self.right.source()

@dataclass
class CmdVarDeclaration(Command):
	cmd_options:Command = CmdEmpty()
	cmd_var_type_speci:CmdVarTypeSpeci = CmdEmpty()
	cmd_asignment:Command = CmdEmpty()

	def __str__(self) -> str:
		string:str = "alc"+str(self.cmd_options)+" "+str(self.cmd_var_type_speci)
		if not self.cmd_asignment.is_empty():
			string += " "+str(self.cmd_asignment)
		return string + ";\n"

	def cpp(self) -> str:
		return f"{self.indents_str()}{self.cmd_var_type_speci.cpp()}{self.cmd_asignment.cpp()};\n"

	def hpp(self) -> str:
		return f"{self.indents_str()}{self.cmd_var_type_speci.hpp()}{self.cmd_asignment.hpp()};\n"

	def first_token(self) -> Token:
		return self.cmd_var_type_speci.left.first_token()

	def source(self) -> list:
		return ["alc"] + self.cmd_options.source() + self.cmd_name.source() + \
			[":"] + self.cmd_type.source() + self.cmd_asignment.source() + [";"]

@dataclass
class CmdFunc(Command):
	cmd_rtn_type:Command	= CmdEmpty()
	cmd_name:Command		= CmdEmpty()
	cmd_params:Command		= CmdEmpty()
	cmd_code_blk:Command	= CmdEmpty()
	cmd_namespace:Command	= CmdEmpty()

	def cpp(self) -> str:
		return str(self.cmd_rtn_type) + " " + str(self.cmd_name) + "(" + self.cmd_params.cpp() + ")" + "\n" + self.cmd_code_blk.cpp()

	def hpp(self) -> str:
		return str(self.cmd_rtn_type) + " " + self.cmd_namespace.hpp() + str(self.cmd_name) + "(" + self.cmd_params.cpp() + ")" + "\n"

	def first_token(self) -> Token:
		return self.cmd_rtn_type.first_token()

	def source(self) -> list:
		return f"func {self.cmd_name.source()}({self.cmd_params.source()}):{self.cmd_rtn_type.source()};\n{self.cmd_code_blk.source()}"

@dataclass
class CmdIfBlock(Command):
	statements:list[Command] = field(default_factory=list[Command])

	def cpp(self) -> str:
		string:str = ""
		for st in self.statements:
			string += st.cpp()
		return string

	def hpp(self) -> str:
		string:str = ""
		for st in self.statements:
			string += st.hpp()
		return string

	def first_token(self) -> Token:
		return self.cmd_rtn_type.first_token()

	def source(self) -> list:
		string:str = ""
		for st in self.statements:
			string += st.cpp()
		return string

@dataclass
class CmdIfStmnt(Command):
	tok_if:Token = Token()
	tok_end:Token = Token()
	cmd_expr:Command = CmdEmpty()
	cmd_code_blk:Command = CmdEmpty()

	def cpp(self) -> str:
		if_str = str(self.tok_if)
		if self.tok_if == "elif":
			if_str = "else if"
		elif self.tok_if == "els":
			if_str = "else"
		expr:str = ""
		if self.cmd_expr.cpp() != "":
			expr = f"({self.cmd_expr.cpp()})"

		return f"{self.indents_str()}{if_str} {expr}\n{self.cmd_code_blk.cpp()}"

	def hpp(self) -> str:
		expr:str = ""
		if not self.cmd_expr.is_empty():
			expr = f"({self.cmd_expr.cpp()})"
		return f"{self.indents_str()}{self.tok_if} {expr}\n{self.cmd_code_blk.hpp()}"

	def first_token(self) -> Token:
		return self.cmd_rtn_type.first_token()

	def source(self) -> list:
		return f"{self.if_token} {self.cmd_expr.source()};\n{self.cmd_code_blk.source()}"