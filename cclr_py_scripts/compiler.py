
try: 
	from lexer import Lexer, TokenList
	from parser import Parser
	from commands import *
except Exception as err: 
	from cclr_py_scripts.commands import *
	from cclr_py_scripts.lexer import Lexer, TokenList
	from cclr_py_scripts.parser import Parser
	from cclr_py_scripts.commands import *
	
from enum import IntEnum, auto
from typing import Dict
from tqdm import tqdm

class Compiler:

	def compile( self, command:CmdCodeBlk, show_pbar:bool=False ) -> str:
		if command.type == CmdTypes.ERROR or command.type == CmdTypes.EMPTY:
			return ""

		compiled:str = ""

		if command.type == CmdTypes.SCRIPT:
			compiled += "\n"
			for _command in command.body:
				compiled += self.compile(_command)
			

		elif command.type == CmdTypes.CODE_BLOCK:
			indents:str = self.indents(command.indents)
			compiled += indents+"{\n"
			for _command in command.body:
				compiled += self.compile(_command)
			compiled += indents+"}\n"
				
		elif command.type == CmdTypes.DECLARATION:
			tk:Token = command.first_token()
			compiled += self.indent_of_token(tk)
			cmd_options:Command = command.cmd_options
			cmd_var_type_speci:Command = command.cmd_var_type_speci
			cmd_asignment:Command = command.cmd_asignment
			if not cmd_options.is_empty():
				dec_option:str = ""
				for dec_option in cmd_options.right.keys:
					compiled += dec_option + " "
			if not cmd_var_type_speci.is_empty():
				compiled += str(cmd_var_type_speci) + " "
			else:
				assert(False)
			if not cmd_asignment.is_empty():
				compiled += " = " + str(cmd_asignment.right)
			compiled += ";\n"

		# --- If Elif and Else ---
		elif command.type == CmdTypes.FLOW_START:
			compiled += self.compile(command.left)
			compiled += self.compile(command.right)
		elif command.type == CmdTypes.FLOW_BLOCK:
			compiled += self.compile(command.left)
			compiled += self.compile(command.right)
		elif command.type == CmdTypes.FLOW_STATMENT:
			compiled += self.indent_of_token(command.pre_op)
			if command.pre_op == "else":
				compiled += f"{command.pre_op}:\n"
			else:
				compiled += f"{command.pre_op} ({command.right}):\n"

		# --- Function ---
		elif command.type == CmdTypes.MTHD_BLOCK:
			compiled += self.compile(command.left)
			compiled += self.compile(command.right) + "\n"
		elif command.type == CmdTypes.MTHD_STATMENT:
			if command.pre_op != "NA":
				compiled += str(command.pre_op) + " "
			if not command.left.is_empty():
				compiled += str(command.left.token)
			compiled += self.compile(command.right)
			if command.pos_op != "NA":
				compiled += str(command.pos_op) + "\n"


		elif command.type == CmdTypes.MTHD_PARAMS:
			compiled += f"{command.pre_op} {self.compile(command.right)}{command.pos_op}"
		elif command.type == CmdTypes.PARAMS:
			compiled += f"{self.compile(command.left)}{command.op} {self.compile(command.right)} "
		elif command.type == CmdTypes.VAR_TYPE_SPECI:
			compiled += f"{command.left.token}"
			if not command.right.is_empty():
				compiled += f"{command.op}{command.right.token}"
			else:
				compiled += " "

		return compiled

	def indent_of_token(self, token:Token) -> str:
		return self.indents( token.indent)

	def indents(self, count:int) -> str:
		indents:str = ""
		for i in range(count):
			indents += "\t"
		return indents

if __name__ == "__main__":
	cclr1:str = """
if 5+5;
	if 2;
		alc anotherthing:int;
else;

	alc _2:int;

func sum(a:int, b:int);
	alc summation:int;
"""

	cpp1:str = """
stuff thing;

if (5):
	else:something;
	"""

	l = Lexer()
	p = Parser()
	c = Compiler()

	compiled:str = ""
	#try:
	compiled = c.compile( p.parse( l.tokenize(cclr1) ) )
	#except ParserException as err:
	#	print(err.args[0])
	print(f"Compiled: \'\'\'{compiled}\'\'\'")

