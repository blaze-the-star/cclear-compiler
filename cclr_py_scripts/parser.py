
try:
	from cclr_py_scripts.commands import *
	from cclr_py_scripts.lexer import Lexer, Token, TokenList, TokenTypes
except:
	from commands import *
	from lexer import Lexer, Token, TokenList, TokenTypes

import enum
from types import FunctionType
from tqdm import tqdm

class ParserException(Exception):
	msg:str = ""

	def __init__(self, msg:str="") -> None:
		self.msg = msg

	def message(self, token:Token, script:tuple) -> str:
		return f"[Error on line {token.row} col {token.col} - {self.msg}]"

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
				self.check_indent(val)
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

		cmd:Command = self.p_vardec_start()

		if cmd.is_empty():
			cmd = self.p_ifblk_start()

		if cmd.is_empty():
			cmd = self.p_expr_start()

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
		while self.cursor < len(self.tokens)-1:
			if self.token_spy().indent == self.expected_indent:
				cmd:Command = self.p_statement()
				self.can_dedent = True
				body.append( cmd )

			elif self.token_spy().indent < self.expected_indent and self.can_dedent:
				#self.expected_indent = self.token_spy().indent
				break
			else:
				raise( ParserException("Indent error; TODO: Put a proper message here (Parser.p_scope)") )

		if len(body) == 0:
			raise( ParserException("TODO: Put a proper message here (Parser.p_scope)") )


		self.expected_indent -= 1

		return CmdStmntArr(type=cmd_type, commands=body, indents=self.expected_indent)

	# ============================================
	# =================================
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
				return CmdIdentifier(value=token, indent=self.token_next().indent)

		return CmdEmpty()

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

		return self.p_expr_var()

	def p_expr_var(self) -> Command:
		e1 = self.p_name()
		if e1.is_error() or e1.is_empty():
			return e1
		e1.type = CmdTypes.VARIABLE
		return e1

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
			if command.cmd_options.is_error():
				return command.cmd_options

			# Var name
			command.cmd_name = self.p_name()
			if command.cmd_name.is_empty():
				raise( ParserException("Invalid name in variable declaration") )


			# Var type
			if self.token_next_check(":"):
				command.cmd_type = self.p_name()
				if command.cmd_type.is_empty():
					raise( ParserException("Invalid type in variable declaration") ) 
			else:
				raise( ParserException("Expected a ':' between declaring variable's name and type") )

			# Var assignment
			command.cmd_asignment = self.p_vardec_assi()
			if command.cmd_asignment.is_error():
					return command.cmd_asignment

			if self.token_next_check(";"):
				if length != -1:
					return command
				raise( ParserException("Error in variable declaration.") )

			else:
				raise( ParserException(f"Expected variable declaration to end with ';' but got '{self.token_spy()}'") )

		return CmdEmpty()
		
	def p_vardec_assi(self) -> Command:
		return self.t_eoe(self.p_empty, self.p_expr_start,
				pre_op="=", cmd_type=CmdTypes.ASSIGNMENT)

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

	def t_stmnt(self, stmnt_def, cmd_type:CmdTypes=CmdTypes.NO_TYPE) -> Command:
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

	def p_ifblk_start(self) -> Command:
		return self.t_eoe( self.p_ifblk_block1, self.p_ifblk_block2_3,
			op="PASS", cmd_type=CmdTypes.FLOW_START )

	def p_ifblk_block1(self) -> Command:
		return self.t_stmnt(self.p_ifblk_def1, cmd_type=CmdTypes.FLOW_BLOCK)

	def p_ifblk_block2_3(self) -> Command:
		return self.t_eoe( self.p_ifblk_block2, self.p_ifblk_block3,
			op="PASS", cmd_type=CmdTypes.FLOW_BLOCK )

	def p_ifblk_block2(self) -> Command:
		return self.t_stmnt(self.p_ifblk_def2, cmd_type=CmdTypes.FLOW_BLOCK)

	def p_ifblk_block3(self) -> Command:
		return self.t_stmnt(self.p_ifblk_def3, cmd_type=CmdTypes.FLOW_BLOCK)

	def p_ifblk_def1(self) -> Command:
		return self.t_eoe( self.p_empty, self.p_expr_start, 
			pre_op="if", pos_op=";", cmd_type=CmdTypes.FLOW_STATMENT )

	def p_ifblk_def2(self) -> Command:
		return self.t_eoe( self.p_empty, self.p_expr_start, 
			pre_op="elif", pos_op=";", cmd_type=CmdTypes.FLOW_STATMENT )

	def p_ifblk_def3(self) -> Command:
		return self.t_eoe( self.p_empty, self.p_expr_start, 
			pre_op="else", pos_op=";", cmd_type=CmdTypes.FLOW_STATMENT )

if __name__ == "__main__":
	l = Lexer()
	p = Parser()

	script = "1 + 5 * 5 * (3 / 2 - 4 / 1 + 1) - 1 / 8"
	script = """
	
alc new_var:int = 5;

alc new_var:int = 5;

if 5;
	alc new:thing;


 """

	tokens = l.tokenize(script)
	parsed = p.parse(tokens)

	print("Script", script)

	print("Parsed", str(parsed))
