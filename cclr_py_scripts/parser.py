
try:
	from cclr_py_scripts.commands import *
	from cclr_py_scripts.lexer import Lexer, Token, TokenList, TokenTypes
except:
	from commands import *
	from lexer import Lexer, Token, TokenList, TokenTypes

import enum
import re
import io
from types import FunctionType
from tqdm import tqdm

class ParserException(Exception):
	msg:str = ""
	script:tuple = tuple()

	def __init__(self, msg:str="") -> None:
		self.msg = msg

	def code_line(self, code:str, start:int, end:int, highlight:int=-1) -> str:
		start = max(0,start)

		buf = io.StringIO(code)
		for i in range(start):
			buf.readline()

		res = ""
		for i in range(start, end+1):
			h:str = "   "
			if highlight == i:
				h = ">> "
			res += f"{h}{str(i).ljust(6)}|  {buf.readline()}"

		return res[:-1]

	def message(self, token:Token, script:tuple) -> str:
		line = token.row-1
		return f"\n{self.code_line(script[1], line-2,line+2, line)}\n--------- \n[Error in {script[0]} on line {line} col {token.col} - {self.msg}]\n"

class Parser(object):

	cursor:int = -1
	cursors_saved:int = [cursor]
	tokens:TokenList = []
	script:tuple = ("","")

	indent:int = 0
	expected_indent:int = 0
	can_dedent:bool = False

	def check_indent( self, checkee ) -> bool:
		if checkee.indent != self.expected_indent:
			if checkee.indent < self.expected_indent:
				if self.can_dedent:
					# Dedenting here might cause problems?
					return False
				else:
					raise ParserException("Abrupt unindent")
			else:
				raise ParserException("Unexpected indent")
		return True
			
	def parse(self, tokens:TokenList, script:tuple=("filename",""), show_bar:bool=False) -> list:
		self.cursor = -1
		self.cursors_saved = [-1]
		self.tokens = tokens
		self.script = script

		self.indent = 0
		self.expected_indent = -1
		self.is_awaiting_initial_indent = True
		self.can_dedent = False

		try:
			return self.p_scope(cmd_type=CmdTypes.SCRIPT)
		except ParserException as err:
			print(err.message(self.token_now(), self.script))

		return CmdEmpty()

	def t_eoe(self, left:FunctionType, right:FunctionType=None, op:str="NA", 
		pre_op:str="NA", pos_op:str="NA", cmd_type:CmdTypes=CmdTypes.NO_TYPE) -> Command:
		"""
		A base funtion for parsing tokens.
		"""
		if pre_op != "NA": # Using left op, optionally using right op, but not op.
			if self.token_next_check(pre_op):
				tk_pre_op = self.token_now()

				e2:Command = CmdEmpty()
				if right != None:
					e2 = right()
				if e2.is_error():
					return e2
				if e2.is_empty():
					e2 = left()

				if pos_op == "NA" or self.token_next_check(pos_op):
					tk_pos_op:Token = self.token_now()
					if pos_op == "NA":
						tk_pos_op = pos_op
					return CmdGroup(type=cmd_type, right=e2, pre_op=tk_pre_op, pos_op=tk_pos_op, indent=tk_pre_op.indent)

			return left()

		elif pos_op != "NA": # Using right_op without left_op
			assert(False, "post_op requires pre_op because to implementation exists for without it.")

		elif op != "NA" or op == "PASS" and self.check_indent(self.token_spy()): # Using only op
			e1:Command = left()
			if e1.is_error():
				return e1
				
			if self.token_next_check(op) or op == "PASS":
				tk_op:Token = self.token_now()
				e2:Command = right()
				if e2.is_error():
					return e2
				if e2.is_empty():
					return e1

				if tk_op == "PASS":
					return CmdGroup(type=cmd_type, left=e1, right=e2, indent=e1.indent)
				else:
					return CmdGroup(type=cmd_type, left=e1, right=e2, op=tk_op, indent=e1.indent)

			return e1

		return left()

	def t_indent_stmnt(self, stmnt_def, cmd_type:CmdTypes=CmdTypes.NO_TYPE) -> Command:
		if self.check_indent(self.token_spy()):
			s1:Command = stmnt_def()
			if s1.is_empty() or s1.is_error():
				return s1

			tk:Token = s1.first_token()
			self.expected_indent += 1
			s2:Command = self.p_scope(tk.row, cmd_type=CmdTypes.CODE_BLOCK)
			if s2.is_empty() or s2.is_error():
				return s1

			return CmdGroup( left=s1, right=s2,	type=cmd_type, indent=s1.indent )
		
		return CmdEmpty()

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
			if val == equater and self.check_indent(val):
				self.cursor += 1
				return True

		return False

	def token_now(self) -> str:
		return self.tokens[self.cursor]

	def token_restore(self, slot:int=0, reset:bool=True) -> None:
		self.cursor = self.cursors_saved[slot]
		if reset:
			self.cursors_saved[slot] = -1

	def token_save(self, slot:int=0) -> None:
		append_by:int = (slot+1)-len(self.cursors_saved)
		self.cursors_saved += [-1 for _ in range(append_by)]
		self.cursors_saved[slot] = self.cursor

	def token_spy(self) -> str:
		if self.cursor+1 >= len(self.tokens):
			return Token()
		return self.tokens[self.cursor+1]

	def token_unique_save(self) -> int:
		for i, slot in enumerate(self.cursors_saved):
			if slot == -1:
				return i
			
		self.cursors_saved.append(-1)
		return len(self.cursors_saved)-1

	# =============================================================================
	# Parse Script
	# =============================================================================

	def p_statement(self) -> Command:
		reading_tk:Token = self.token_spy()

		cmd:Command = self.p_vardec_start()		# Variable Declaration
		if cmd.is_empty():
			cmd = self.p_ifblk_blk2()			# If
		if cmd.is_empty():
			cmd = self.p_funcblk_start()		# Func
		if cmd.is_empty():
			cmd = self.p_expr_start()			# Expression

		if not cmd.is_empty():
			return cmd

		if reading_tk.type == TokenTypes.NONE:
			return CmdEmpty()

		raise( ParserException(f"Undefined token '{reading_tk}'") )

	def p_scope(self, row:int=-1, cmd_type:CmdTypes=CmdTypes.NO_TYPE) -> Command:
		if self.expected_indent == -1:
			self.expected_indent = self.token_spy().indent
		self.can_dedent = False

		body:list = []
		while True:
			if self.token_spy().indent == self.expected_indent:
				cmd:Command = self.p_statement()
				self.can_dedent = True
				body.append( cmd )

			elif self.token_spy().indent < self.expected_indent and self.can_dedent:
				self.expected_indent -= 1
				break
			else:
				raise( ParserException("Indent error; TODO: Put a proper message here (Parser.p_scope)") )

		if len(body) == 0:
			raise( ParserException("TODO: Put a proper message here (Parser.p_scope)") )


		return CmdCodeBlk(type=cmd_type, body=body, indent=self.expected_indent)

	# =============================================================================
	# Parse Misc
	# =============================================================================

	def p_empty(self) -> Command:
		return CmdEmpty()

	def p_name(self) -> Command:
		token:Token = self.token_spy()

		if len(token.text) == 0:
			return CmdEmpty()

		if token.text[0].isalpha() or token.text[0] == "_":
			use:bool = True

			i:int = 0
			char:str = ""
			while i < len(token.text):
				char = token.text[i:i+1]
				if not char.isalnum() and char != "_":
					use = False
					break
				i += 1

			if use:
				return CmdToken(token=token, indent=self.token_next().indent)

		return CmdEmpty()

	def p_var_name(self) -> Command:
		cmd:Command = self.p_name()
		cmd.type = CmdTypes.VARIABLE_NAME
		return cmd

	def p_type_name(self) -> Command:
		cmd:Command = self.p_name()
		cmd.type = CmdTypes.TYPE_NAME
		return cmd

	def p_mthd_name(self) -> Command:
		cmd:Command = self.p_name()
		cmd.type = CmdTypes.MTHD_NAME
		return cmd

	# =============================================================================
	# Parse Parameter Array
	# =============================================================================

	def p_params(self) -> Command:
		return self.t_eoe(left=self.p_var_type_specify, right=self.p_params,
			op=",", cmd_type=CmdTypes.PARAMS)

	def p_var_type_specify(self) -> Command:
		var_name = self.p_var_name()
		if var_name:
			if self.token_next_check(":"):
				tk = self.token_now()
				type_name = self.p_type_name()
				if type_name:
					return CmdVarTypeSpeci(type=CmdTypes.VAR_TYPE_SPECI, var_name=var_name.token, type_name=type_name.token, op=tk)

			raise ParserException("TODO: add proper message here (p_var_type_specify)")

		return CmdEmpty()

		return CmdVarTypeSpeci()
		self.t_eoe(left=self.p_var_name, right=self.p_type_name,
			op=":", cmd_type=CmdTypes.VAR_TYPE_SPECI)

	# =============================================================================
	# Parse Expression
	# =============================================================================

	def p_expr_start(self) -> Command:
		return self.t_eoe(left=self.p_expr_sub, 
			cmd_type=CmdTypes.BINARY_EXPRESSION)

	def p_expr_sub(self) -> Command:
		return self.t_eoe(left=self.p_expr_add, right=self.p_expr_start, 
				op="-", cmd_type=CmdTypes.BINARY_EXPRESSION)

	def p_expr_add(self) -> Command:
		return self.t_eoe(left=self.p_expr_divi, right=self.p_expr_start, 
			op="+",	cmd_type=CmdTypes.BINARY_EXPRESSION)

	def p_expr_divi(self) -> Command:
		return self.t_eoe(left=self.p_expr_mult, right=self.p_expr_start, 
			op="/",	cmd_type=CmdTypes.BINARY_EXPRESSION)

	def p_expr_mult(self) -> Command:
		return self.t_eoe(left=self.p_expr_paren, right=self.p_expr_start, 
			op="*", cmd_type=CmdTypes.BINARY_EXPRESSION)

	def p_expr_paren(self) -> Command:
		return self.t_eoe(left=self.p_expr_literal, right=self.p_expr_start, 
			pre_op="(", pos_op=")", cmd_type=CmdTypes.BINARY_EXPRESSION)

	def p_expr_literal(self) -> Command:
		token:Token = self.token_spy()
		if token.text.isnumeric():
			self.token_next()
			return CmdNumericLiteral(value=token, indent=token.indent)

		return self.p_var_name()

	# =============================================================================
	# Parse Variable Declaration
	# =============================================================================

	def p_vardec_start(self) -> Command:
		if self.token_next_check("alc"):
			command:CmdVarDeclaration = CmdVarDeclaration()
			command.indent = self.token_now().indent
			
			length:int = -1
			i:int = self.cursor
			while i != len(self.tokens):
				if self.tokens[i] == ";":
					length = i - self.cursor
					break
				i += 1

			# Var options
			command.cmd_options = self.p_vardec_opti1()

			# Var type specify
			command.cmd_var_type_speci = self.p_var_type_specify()

			# Var assignment
			command.cmd_asignment = self.p_vardec_assi()

			if self.token_next_check(";"):
				if length != -1:
					return command
				raise( ParserException("Error in variable declaration.") )

			else:
				raise( ParserException(f"Expected variable declaration to end with ';' but got '{self.token_spy()}'") )

		return CmdEmpty()
		
	def p_vardec_assi(self) -> Command:
		if self.token_next_check("="):
			eq = self.token_now()
			expr = self.p_expr_start()
			if expr:
				return CmdAssign(equator=eq, cmd_expr=expr)
			raise ParserException("TODO: Add proper message here (p_vardec_assi)")

		return CmdEmpty()

	def p_vardec_opti1(self) -> Command:
		return self.t_eoe(self.p_empty, self.p_vardec_opti2,
				pre_op="(", pos_op=")", cmd_type=CmdTypes.DECLARATION)

	def p_vardec_opti2(self) -> Command:
		keys:list = []
		i:int = self.cursor+1
		while i != len(self.tokens):
			token:Token = self.tokens[i]
			if token == "static" or token == "const":
				keys.append(token)
				self.token_next()
			elif token == ")":
				break
			else:
				raise( ParserException(f"Invalid keyword for variable declaration '{token}'") )
			i += 1

		if len(keys) != 0:
			return CmdTokenList(keys=keys)

		raise( ParserException("Error in parse option.") )

	# =============================================================================
	# Parse If block
	# =============================================================================

	REGEX_IF:re.Pattern = re.compile("(if|elif|else if|else|els)")
	REGEX_SUBIF:re.Pattern = re.compile("(elif|else if|else|els)")

	def p_ifblk_blk2(self) -> CmdIfBlock:
		if_arr = list()
		while self.cursor < len(self.tokens):
			if len(if_arr) == 0:
				cmd_if:Command = self.p_ifblk_stmnt2("if")
				if cmd_if.is_empty():
					return cmd_if
				if_arr.append(cmd_if)

			else:
				cmd_if:Command = self.p_ifblk_stmnt2(self.REGEX_SUBIF)
				if cmd_if.is_empty():
					return CmdIfBlock(indent=self.expected_indent, statements=if_arr)
				if_arr.append(cmd_if)

	def p_ifblk_stmnt2(self, starting_keyword=REGEX_IF) -> CmdIfBlock:
		if self.token_next_check(starting_keyword):
			tk = self.token_now()
			expr = CmdEmpty()
			if tk != "(else|els)":
				expr = self.p_expr_start()
				if expr.is_empty():
					raise ParserException(f"Expected '{tk}' statement to have an expression but got token '{self.token_spy()}' ")

			if self.token_next_check(";"):
				tk_end = self.token_now()
				self.expected_indent += 1
				block = self.p_scope(self.expected_indent, cmd_type=CmdTypes.CODE_BLOCK)
				return CmdIfStmnt(indent=self.expected_indent, tok_if=tk, tok_end=tk_end, cmd_expr=expr, cmd_code_blk=block)
			else:
				raise ParserException(f"Expected '{tk}' statement to end with a ';' but got '{self.token_spy()}' ")

		return self.p_empty()

	def p_ifblk_start(self) -> Command:
		return self.t_eoe( self.p_ifblk_block1, self.p_ifblk_block2_3,
			op="PASS", cmd_type=CmdTypes.FLOW_START )

	def p_ifblk_block1(self) -> Command:
		return self.t_indent_stmnt(self.p_ifblk_def1, cmd_type=CmdTypes.FLOW_BLOCK)

	def p_ifblk_block2_3(self) -> Command:
		return self.t_eoe( self.p_ifblk_block2, self.p_ifblk_block3,
			op="PASS", cmd_type=CmdTypes.FLOW_BLOCK )

	def p_ifblk_block2(self) -> Command:
		return self.t_indent_stmnt(self.p_ifblk_def2, cmd_type=CmdTypes.FLOW_BLOCK)

	def p_ifblk_block3(self) -> Command:
		return self.t_indent_stmnt(self.p_ifblk_def3, cmd_type=CmdTypes.FLOW_BLOCK)

	def p_ifblk_def1(self) -> Command:
		return self.t_eoe( self.p_empty, self.p_expr_start, 
			pre_op="if", pos_op=";", cmd_type=CmdTypes.FLOW_STATMENT )

	def p_ifblk_def2(self) -> Command:
		return self.t_eoe( self.p_empty, self.p_expr_start, 
			pre_op="elif", pos_op=";", cmd_type=CmdTypes.FLOW_STATMENT )

	def p_ifblk_def3(self) -> Command:
		return self.t_eoe( self.p_empty, self.p_expr_start, 
			pre_op="else", pos_op=";", cmd_type=CmdTypes.FLOW_STATMENT )

	# =============================================================================
	# Parse Func block
	# =============================================================================

	def p_funcblk_start(self) -> Command:
		return self.t_indent_stmnt(self.p_funcblk_def, cmd_type=CmdTypes.MTHD_BLOCK)

	def p_funcblk_def(self) -> Command:
		return self.t_eoe( self.p_empty, self.p_funcblk_name, 
			pre_op="func", pos_op=";", cmd_type=CmdTypes.MTHD_STATMENT )

	def p_funcblk_name(self) -> Command:
		return self.t_eoe( self.p_mthd_name, self.p_mthd_params, 
			op="PASS",cmd_type=CmdTypes.MTHD_STATMENT )

	def p_mthd_params(self):
		return self.t_eoe( self.p_empty, self.p_params, 
			pre_op="(", pos_op=")",cmd_type=CmdTypes.MTHD_PARAMS )

if __name__ == "__main__":
	l = Lexer()
	p = Parser()

	script = "1 + 5 * 5 * (3 / 2 - 4 / 1 + 1) - 1 / 8"
	script = """
alc new_var:int = 5;
alc new_var2:int = 5;
if 5;
	alc new1:int;
	if new1;
		alc old:int;
elif 6;
	alc new2:int;
elif 8;
	alc new3:int;
els;
	alc new4:int;
"""

	tokens = l.tokenize(script)
	parsed = p.parse(tokens, script=("NOFILE", script))
	print(f"Parsed '{parsed.cpp()}'")
