
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

	def compile( self, command:CmdStmntArr, show_pbar:bool=False ) -> str:
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
			cmd_name:Command = command.cmd_name
			cmd_type:Command = command.cmd_type
			cmd_asignment:Command = command.cmd_asignment
			if not cmd_options.is_empty():
				dec_option:str = ""
				for dec_option in cmd_options.right.keys:
					compiled += dec_option + " "
			if not cmd_type.is_empty():
				compiled += str(cmd_type.value) + " "
			else:
				assert(False)
			if not cmd_name.is_empty():
				compiled += str(cmd_name.value)
			else:
				assert(False)
			if not cmd_asignment.is_empty():
				compiled += " = " + str(cmd_asignment.right)
			compiled += ";\n"

		elif command.type == CmdTypes.FLOW_START:
			compiled += self.compile(command.left)
			#compiled += "START1 ----------------------------- \n"
			compiled += self.compile(command.right)
			#compiled += "START2 ----------------------------- \n"


		elif command.type == CmdTypes.FLOW_BLOCK:
			compiled += self.compile(command.left)
			#compiled += "BLOK1 ----------------------------- \n"
			compiled += self.compile(command.right)
			#compiled += "BLOK2 ----------------------------- \n"


		elif command.type == CmdTypes.FLOW_STATMENT:
			compiled += self.indent_of_token(command.pre_op)
			#compiled += "STATE1 ----------------------------- \n"
			if command.pre_op == "else":
				compiled += f"{command.pre_op}:\n"
			else:
				compiled += f"{command.pre_op} ({command.right}):\n"
			#compiled += "STATE2 ----------------------------- \n"


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

