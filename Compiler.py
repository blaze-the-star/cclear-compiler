
import fire
import os
from Commands import *
from enum import IntEnum, auto
from typing import Dict

class LexerState:
	idx:int = -1 # Starts at -1 because char_next increments before returning
	script:str = ""
	tokens:list = []

	def __init__(self, _script:str) -> None:
		self.script = _script

	def is_parsing(self) -> bool:
		return self.idx < len(self.script)

	def char_next(self) -> str:
		self.idx += 1
		return self.script[self.idx:self.idx+1]

	def char_now(self) -> str:
		return self.script[self.idx:self.idx+1]

class Lexer:

	def is_symbol(self, char:str) -> bool:
		return char == "`" or char == "~" or char == "!" or char == "@" or		\
			char == "#" or char == "$" or char == "%" or char == "^" or			\
			char == "&" or char == "*" or char == "(" or char == ")" or			\
			char == "-" or char == "=" or char == "+" or char == "[" or			\
			char == "{" or char == "]" or char == "}" or char == "\\" or		\
			char == "|" or char == ":" or char == ";" or char == "\"" or		\
			char == "'" or char == "," or char == "<" or char == "." or			\
			char == ">" or char == "/" or char == "?"			

	def pares_state_any(self, t_state:LexerState) -> None:
		char:str = ""

		while t_state.is_parsing():
			char = t_state.char_now()
			
			if char.isalnum():
				self.pares_state_word( t_state )
				continue
			elif self.is_symbol(char):
				t_state.tokens.append(char)
				t_state.char_next()
				continue

			char = t_state.char_next()

		return t_state.tokens

	def pares_state_word(self, t_state:LexerState) -> None:
		char:str = t_state.char_now()
		token:str = ""

		while t_state.is_parsing():

			if char == " ":
				break
			elif char.isalnum():
				token += char
			elif char == "_":
				token += char
			else:
				break

			char = t_state.char_next()

		if len(token) != 0:
			t_state.tokens.append(token)

	def tokenize(self, script:str) -> list:
		t_state:LexerState = LexerState(script)
		self.pares_state_any(t_state)

		return t_state.tokens

class Parser:

	cursor:int = -1
	cursor_saved:int = cursor
	tokens:list = []

	def parse(self, tokens:list) -> list:
		self.cursor = -1
		self.cursor_saved = -1
		self.tokens = tokens

		commands:list = []
		while self.cursor < len(self.tokens)-1:
			expression:Command = self.parse_script()
			if expression.is_error():
				return [expression]
			commands.append(expression)

		if len(commands) != 0:
			return commands

		return [CmdError(msg="Error in parse.")]

	def tmplt_express_ex_op_ex(self, higher_expression, variant) -> Command:
		expression1:Command = higher_expression()
		if expression1.is_error():
			return expression1

		expression2:Command = variant()
		if expression2.is_error():
			return expression2
		if expression2.is_empty():
			return expression1
		if expression2.type == CmdTypes.BINARY_EXPRESSION:
			expression2.left = expression1
			return expression2

		return CmdError(msg="Error in [express][op][express].")

	def tmplt_express_ex_op_ex_right(self, higher_expression, variant_self, check_op:str) -> Command:
		if self.token_spy() == check_op:
			op:str = self.token_next()
			expression:Command = higher_expression()
			if expression.is_error() or expression.is_empty():
				return expression
			return CmdBinaryExpression( op=op, right=expression )
			
		# Empty
		return CmdEmpty()

	def tmplt_express_op_ex_op(self, higher_expression, inner_expression, open_op:str, close_op:str) -> Command:
		self.token_save()
		if self.token_next_check(open_op):
			expression:Command = inner_expression()
			if self.token_next_check(close_op):
				return CmdGroup(value=expression, left="(", right=")")

			return CmdEmpty()

		return higher_expression()

	def token_inspect(self, expectation:str) -> str:
		return self.token_next() == expectation

	def token_next(self) -> str:
		self.cursor += 1
		if self.cursor+1 > len(self.tokens):
			return ""
		return self.tokens[self.cursor]

	def token_next_check(self, equater:str) -> bool: # Returns the next token. Also increments the cursor if the next token is equal to *equater*.
		val:str = ""
		if self.cursor < len(self.tokens)-1:
			val = self.tokens[self.cursor+1]
			if val == equater:
				self.cursor += 1
				return True

		return False

	def token_now(self) -> str:
		return self.tokens[self.cursor]

	def token_restore(self) -> None:
		self.cursor = self.cursor_saved

	def token_save(self) -> None:
		self.cursor_saved = self.cursor

	def token_spy(self) -> str:
		if self.cursor+1 >= len(self.tokens):
			return ""
		return self.tokens[self.cursor+1]

	# =============================================================================
	# Parse Script
	# =============================================================================

	def parse_script(self) -> Command:
		cmd:Command = self.parse_expression()
		if not cmd.is_empty(): # Return results or error
			return cmd
		
		cmd:Command = self.parse_var_declaration()
		if not cmd.is_empty(): # Return results or error
			return cmd

		return CmdError(msg="Undefined token '%s'" % self.token_spy())

	# =============================================================================
	# Parse Misc
	# =============================================================================

	def parse_name(self) -> Command:
		token:Dict = self.token_spy()

		if token[0].isalpha() or token[0] == "_":
			use:bool = True

			i:int = 0
			char:str = ""
			while i < len(token):
				char = token[i:i+1]
				if not char.isalnum() and char != "_":
					use = False
					break
				i += 1

			if use:
				return CmdIdentifier(value=self.token_next())

		return CmdError(msg="Name not valid.")

	# =============================================================================
	# Parse Expression
	# =============================================================================

	def parse_expression(self) -> Command:
		return self.parse_expr_sub_l()

	def parse_expr_sub_l(self) -> Command:
		return self.tmplt_express_ex_op_ex(self.parse_expr_add_l, self.parse_expr_sub_r)
	def parse_expr_sub_r(self) -> Command:
		return self.tmplt_express_ex_op_ex_right(self.parse_expr_add_l, self.parse_expr_sub_r, "-")

	def parse_expr_add_l(self) -> Command:
		return self.tmplt_express_ex_op_ex(self.parse_expr_div_l, self.parse_expr_add_r)
	def parse_expr_add_r(self) -> Command:
		return self.tmplt_express_ex_op_ex_right(self.parse_expr_div_l, self.parse_expr_add_r, "+")

	def parse_expr_div_l(self) -> Command:
		return self.tmplt_express_ex_op_ex(self.parse_expr_mult_l, self.parse_expr_div_r)
	def parse_expr_div_r(self) -> Command:
		return self.tmplt_express_ex_op_ex_right(self.parse_expr_mult_l, self.parse_expr_div_r, "/")

	def parse_expr_mult_l(self) -> Command:
		return self.tmplt_express_ex_op_ex(self.parse_expr_paren, self.parse_expr_mult_r)
	def parse_expr_mult_r(self) -> Command:
		return self.tmplt_express_ex_op_ex_right(self.parse_expr_paren, self.parse_expr_mult_r, "*")

	def parse_expr_paren(self) -> Command:
		return self.tmplt_express_op_ex_op(self.parse_expr_prime, self.parse_expression, "(", ")")

	def parse_expr_prime(self) -> Command:
		token:str = self.token_spy()
		if token.isnumeric():
			self.token_next()
			return CmdNumericLiteral(value=token)

		return CmdEmpty()

	# =============================================================================
	# Parse Variable
	# =============================================================================

	def parse_var_declaration(self) -> Command:
		if self.token_next_check("alc"):
			command:CmdVarDeclaration = CmdVarDeclaration()
			
			length:int = -1
			i:int = self.cursor
			while i != len(self.tokens):
				if self.tokens[i] == ";":
					length = i - self.cursor
					break
				i += 1

			# Var options
			command.cmd_options = self.parse_var_options()
			if command.cmd_options.is_error():
				return command.cmd_options

			# Var name
			command.cmd_name = self.parse_name()
			if command.cmd_name.is_error():
				return command.cmd_name

			# Var type
			if self.token_next_check(":"):
				command.cmd_type = self.parse_name()
				if command.cmd_type.is_error():
					return command.cmd_type
			else:
				return CmdError(msg="Expected a ':'")

			# Var assignment
			command.cmd_asignment = self.parse_var_assignment()
			if command.cmd_asignment.is_error():
					return command.cmd_asignment

			if self.token_next_check(";"):
				if length != -1:
					return command
				return CmdError(msg="Error in variable declaration.")
			else:
				return CmdError(msg="ERROR: Variable declaration expected a ';'")

		return CmdEmpty()
		
	def parse_var_assignment(self) -> Command:
		return self.tmplt_express_ex_op_ex_right(self.parse_expression, self.parse_var_assignment, "=")

	def parse_var_options(self) -> Command:
		return self.tmplt_express_op_ex_op(self.parse_empty, self.parse_var_option, "(", ")")

	def parse_var_option(self) -> Command:
		keys:list = []
		i:int = self.cursor+1
		while i != len(self.tokens):
			token:str = self.tokens[i]
			if token == "static" or token == "const":
				keys.append(token)
				self.token_next()
			else:
				break
			i += 1

		if len(keys) != 0:
			return CmdTokenList(keys=keys)

		return CmdError(msg="Error in parse option.")

	def parse_empty(self) -> Command:
		return CmdEmpty()

class Compiler:

	def compile( self, commands:list ) -> str:
		compiled:str = ""

		command:Command
		for command in commands:
			if command.type == CmdTypes.VAR_DECLATION:
				cmd_options:Command = command.cmd_options
				cmd_name:Command = command.cmd_name
				cmd_type:Command = command.cmd_type
				cmd_asignment:Command = command.cmd_asignment

				if not cmd_options.is_empty():
					dec_option:str = ""
					for dec_option in cmd_options.value.keys:
						compiled += dec_option + " "

				if not cmd_type.is_empty():
					compiled += cmd_type.value + " "
				else:
					assert(False)

				if not cmd_name.is_empty():
					compiled += cmd_name.value
				else:
					assert(False)

				if not cmd_asignment.is_empty():
					compiled += " = " + str(cmd_asignment.right)

				compiled += ";\n"

		return compiled

# =============================================================================
# Command Line Interface
# =============================================================================

def command( s:str="ExampleProject/script.cclr" ) -> None:
	assert(s.endswith(".cclr"))

	dir, file_name = os.path.split(s)
	cache_dir:str = os.path.join("./", "__cclrcach__")
	out_cpp:str = file_name[0:-4]+"cpp"
	out_h:str = file_name[0:-4]+"h"

	source_code:int = ""
	with open(os.path.join(".",s), "r") as file:
		source_code = file.read()

	lx = Lexer()
	ps = Parser()
	c = Compiler()

	tokens:list = lx.tokenize(source_code)
	commands:list = ps.parse(tokens)
	cpp_code:str = c.compile(commands)

	if not os.path.isdir(cache_dir):
		os.mkdir(cache_dir)

	with open( os.path.join(cache_dir,out_cpp), "w") as file:
		file.write(cpp_code)
	with open( os.path.join(cache_dir,out_h), "w") as file:
		file.write("hi h")

if __name__ == "__main__":
	fire.Fire(command)