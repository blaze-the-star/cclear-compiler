
try:
	from cclr_py_scripts.commands import *
	from cclr_py_scripts.lexer import Lexer, Token, TokenList
except:
	from commands import *
	from lexer import Lexer, Token, TokenList
from types import FunctionType
from tqdm import tqdm

class Parser(object):

	cursor:int = -1
	cursors_saved:int = [cursor]
	tokens:TokenList = []

	indent:int = 0
	expected_indent:int = 0
	can_dedent:bool = False
	is_awaiting_initial_indent:bool = False

	def parse(self, tokens:TokenList, show_bar:bool=False) -> list:
		self.cursor = -1
		self.cursors_saved = [-1]
		self.tokens = tokens

		self.indent = 0
		self.expected_indent = 0
		self.is_awaiting_initial_indent = True
		self.can_dedent = False

		commands:list = []
		i:int = 0
		with tqdm(total=len(self.tokens), desc="Parsinng CClear files", unit="token", disable=not show_bar) as pbar:
			while self.cursor != len(self.tokens)-1:

				loop_made_change:bool = False
				while True:
					if self.token_next_check("\n"):
						self.indent = 0
						loop_made_change = True
						continue
					tk = self.token_spy()
					ma = Lexer.RE_INDENT.match(tk.text)
					if ma != None:
						# TODO: Better handling of spaces and tabs
						self.indent = len(tk.text)
						if self.is_awaiting_initial_indent:
							self.expected_indent = self.indent
							self.is_awaiting_initial_indent = False

						self.token_next()
						loop_made_change = True
						continue
					break
				if loop_made_change:
					continue

				expression:Command = self.p_script()
				if expression.is_error():
					return [expression]
				commands.append(expression)
				# Update progress bar
				if self.cursor-pbar.n > len(tokens)/100:
					pbar.update(self.cursor-pbar.n)

			pbar.update(self.cursor+1-pbar.n)

		if len(commands) != 0:
			return CmdScript(commands)

		err:CmdError = CmdError(msg="Error in parse.", token=self.token_spy())
		return CmdScript(([err]))

	def eoe(self, left:FunctionType, right:FunctionType=None, op:str="NA", 
		pre_op:str="NA", pos_op:str="NA", cmd_type:CmdTypes=CmdTypes.NO_TYPE) -> Command:
		"""
		A base funtion for parsing tokens.
		"""

		self.token_save(0) # Return to slot 0 if pre op is used, but not all requirements are met

		if pre_op != "NA": # Using left op, optionally using right op, but not op.
			if self.token_next_check(pre_op):
				e2:Command = right()
				if e2.is_error():
					return e2
				if e2.is_empty():
					return left()

				if pos_op == "NA" or self.token_next_check(pos_op):
					return CmdGroup(type=cmd_type, right=e2, pre_op=pre_op, pos_op=pos_op)

			return left()

		elif pos_op != "NA": # Using right_op without left_op
			assert(False, "post_op requires pre_op because to implementation exists for without it.")

		elif op != "NA": # Using only op
			e1:Command = left()
			if e1.is_error():
				return e1

			self.token_save()
			if self.token_next_check(op):
				e2:Command = right()
				if e2.is_error():
					return e2
				if e2.is_empty():
					self.token_restore()
					return e1

				return CmdGroup(type=cmd_type, left=e1, right=e2, op=op)

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
				self.cursor += 1
				return True

		return False

	def token_now(self) -> str:
		return self.tokens[self.cursor]

	def token_restore(self, slot:int=0) -> None:
		self.cursor = self.cursors_saved[slot]

	def token_save(self, slot:int=0) -> None:
		append_by:int = (slot+1)-len(self.cursors_saved)
		self.cursors_saved += range(append_by)
		self.cursors_saved[slot] = self.cursor

	def token_spy(self) -> str:
		if self.cursor+1 >= len(self.tokens):
			return Token()
		return self.tokens[self.cursor+1]

	# =============================================================================
	# Parse Script
	# =============================================================================

	def p_script(self) -> Command:
		self.token_save()
		cmd:Command = CmdEmpty()
		
		reading_tk:Token = self.token_spy()

		cmd = self.p_vardec_start()
		if cmd.is_empty():
			self.token_restore()
			cmd = self.p_expr_start()

		if not cmd.is_empty(): # Return indentation error
			if self.indent > self.expected_indent:
				err:CmdError = CmdError(reading_tk, msg="Unexpected indentation")
				return err
			elif self.indent < self.expected_indent and not self.can_dedent:
				err:CmdError = CmdError(reading_tk, msg="Abrupt dedentation")
				return err

			return cmd

		err:CmdError = CmdError(reading_tk, msg="Undefined token '%s'"%reading_tk)
		return err

	# =============================================================================
	# Parse Misc
	# =============================================================================

	def p_empty(self) -> Command:
		return CmdEmpty()

	def p_name(self) -> Command:
		token:Token = self.token_spy()

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
				return CmdIdentifier(value=self.token_next())

		return CmdEmpty()

	# =============================================================================
	# Parse Expression
	# =============================================================================

	def p_expr_start(self) -> Command:
		return self.eoe(left=self.p_expr_sub, 
			cmd_type=CmdTypes.BINARY_EXPRESSION)

	def p_expr_sub(self) -> Command:
		return self.eoe(left=self.p_expr_add, right=self.p_expr_start, 
				op="-", cmd_type=CmdTypes.BINARY_EXPRESSION)

	def p_expr_add(self) -> Command:
		return self.eoe(left=self.p_expr_divi, right=self.p_expr_start, 
			op="+",	cmd_type=CmdTypes.BINARY_EXPRESSION)

	def p_expr_divi(self) -> Command:
		return self.eoe(left=self.p_expr_mult, right=self.p_expr_start, 
			op="/",	cmd_type=CmdTypes.BINARY_EXPRESSION)

	def p_expr_mult(self) -> Command:
		return self.eoe(left=self.p_expr_paren, right=self.p_expr_start, 
			op="*", cmd_type=CmdTypes.BINARY_EXPRESSION)

	def p_expr_paren(self) -> Command:
		return self.eoe(left=self.p_expr_literal, right=self.p_expr_start, \
			pre_op="(", pos_op=")", cmd_type=CmdTypes.BINARY_EXPRESSION)

	def p_expr_literal(self) -> Command:
		token:Token = self.token_spy()
		if token.text.isnumeric():
			self.token_next()
			return CmdNumericLiteral(value=token)

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
			if command.cmd_name.is_error():
				return command.cmd_name

			# Var type
			if self.token_next_check(":"):
				command.cmd_type = self.p_name()
				if command.cmd_type.is_error():
					return command.cmd_type
			else:
				err:CmdError = CmdError(self.token_spy(), msg="Variable declaration expected a ':'")
				return err

			# Var assignment
			command.cmd_asignment = self.p_vardec_assi()
			if command.cmd_asignment.is_error():
					return command.cmd_asignment

			if self.token_next_check(";"):
				if length != -1:
					return command
				err:CmdError = CmdError(self.token_spy(), msg="Error in variable declaration.")
				return err
			else:
				err:CmdError = CmdError(self.token_spy(), msg="Variable declaration was not closed with a ';'")
				return err

		return CmdEmpty()
		
	def p_vardec_assi(self) -> Command:
		return self.eoe(self.p_expr_start, self.p_vardec_assi,
				op="=", cmd_type=CmdTypes.ASSIGNMENT)

	def p_vardec_opti1(self) -> Command:
		return self.eoe(self.p_empty, self.p_vardec_opti2,
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
				err:CmdError = CmdError(token, msg="Invalid keyword for variable declaration '{}'".format(token))
				return err
			i += 1

		if len(keys) != 0:
			return CmdTokenList(keys=keys)

		err:CmdError = CmdError(self.token_spy(), msg="Error in parse option.")
		return err

if __name__ == "__main__":
	l = Lexer()
	p = Parser()

	script = "1 + 5 * 5 * (3 / 2 - 4 / 1 + 1) - 1 / 8"
	script = """
	
	alc new_var:int = 5;

	alc new_var:int = 5;


 """

	tokens = l.tokenize(script)
	parsed = p.parse(tokens)

	print("Script", script)

	print("Parsed", str(parsed))
