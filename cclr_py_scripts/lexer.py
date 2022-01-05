
import re
from typing import Dict, Tuple
from enum import IntEnum, auto
from tqdm import tqdm

class TokenTypes(IntEnum):
	NONE:int			= auto()
	UNKNOWN:int			= auto()
	ERROR:int			= auto()
	VARNAME:int			= auto()
	KEYWORD:int			= auto()
	INT:int				= auto()
	FLOAT:int			= auto()
	NEWLINE:int			= auto()
	INDENT:int			= auto()
	SPACES:int			= auto()
	SYMBOL:int			= auto()
	COMMENT:int			= auto()

class TokenList:
	tokens:list = []

	def __bool__(self):
		return self.tokens.__bool__()

	def __getitem__(self, key):
		return self.tokens[key]

	def __init__(self, tokens:list=[]) -> None:
		self.tokens = tokens

	def __iter__(self):
		return self.tokens.__iter__()

	def __len__(self):
		return self.tokens.__len__()

	def __setitem__(self, key, value):
		self.tokens[key] = value

	def __sizeof__(self) -> int:
		return self.tokens.__sizeof__()

	def __str__(self) -> str:
		string:str = ""
		for token in self.tokens:
			string += str(token) + " "
		return string[:-1]

class Token:
	text:str = ""
	idx:int = -1
	row:int = -1
	col:int = -1
	type:int = TokenTypes.NONE

	def __add__(self, add_by:str) -> str:
		assert(add_by is str, "TypeError: unsupported operand type(s) for +: 'Token' and '{}'".format(type(add_by).__name__))
		return self.text + add_by

	def __eq__(self, obj:object) -> bool:
		if isinstance(obj, str):
			return self.text == obj
		elif isinstance(obj, Token):
			return self.text == obj.text
		elif isinstance(obj, int):
			return self.type == obj
		elif isinstance(obj, Tuple):
			if len(obj) == 2:
				return self.row == obj[0] and self.col == obj[1]
			return False
		else:
			return False

	def __init__(self, text:str="", idx:int=-1, row:int=-1, col:int=-1, type:int=TokenTypes.NONE) -> None:
		self.text = text
		self.idx = idx
		self.row = row
		self.col = col
		self.type = type

	def __str__(self) -> str:
		return self.text

class Lexer:

	RE_INDENT = re.compile(r"(?:^)[ \t]+", flags=re.MULTILINE)

	codes:Dict = {
		re.compile(r"//.*")											:TokenTypes.COMMENT,	# Matches a one-line comment
		re.compile(r"/\*.*\*/")										:TokenTypes.COMMENT,	# Matches a multi-line comment
		re.compile(r"([a-zA-Z]+|[_]+[a-zA-Z0-9])[a-zA-Z0-9_]*")		:TokenTypes.VARNAME,	# Matches a valid variable name
		re.compile(r"alc")											:TokenTypes.KEYWORD,	# Matches keyword alc
		re.compile(r"(if|else|elif)")								:TokenTypes.KEYWORD,	# Matches keyword for if statements
		re.compile(r"[0-9]+")										:TokenTypes.INT,		# Matches valid int
		re.compile(r"[0-9]*\.[0-9]+")								:TokenTypes.FLOAT,		# Matches valid float
		re.compile(r"\n")											:TokenTypes.NEWLINE,	# Matches a new line
		RE_INDENT													:TokenTypes.INDENT,		# Matches a indents at start of fline
		re.compile(r"[)(]")											:TokenTypes.SYMBOL,		# Matches parenthesis
		re.compile(r"[+\-*/|^%]")									:TokenTypes.SYMBOL,		# Matches any math symbol
		re.compile(r"(>=|<=|==|[!&|?><=])")							:TokenTypes.SYMBOL,		# Matches any logic symbol
		re.compile(r"[:;]")											:TokenTypes.SYMBOL,		# Matches end statement or type specifier symbol
		re.compile(r" ")											:TokenTypes.NONE,		# Do NOT match spacescr,
		re.compile(r".+?(?:\b)")									:TokenTypes.ERROR,		# Matches any token for an error,
	}

	def is_symbol(self, char:str) -> bool:
		return char == "`" or char == "~" or char == "!" or char == "@" or		\
			char == "#" or char == "$" or char == "%" or char == "^" or			\
			char == "&" or char == "*" or char == "(" or char == ")" or			\
			char == "-" or char == "_" or char == "=" or char == "+" or 		\
			char == "[" or char == "{" or char == "]" or char == "}" or 			\
			char == "\\" or char == "|" or char == ":" or char == ";" or 		\
			char == "\"" or char == "'" or char == "," or char == "<" or 		\
			char == "." or	char == ">" or char == "/" or char == "?"			\

	def tokenize(self, script:str, show_bar:bool=False) -> TokenList:
		if script == "":
			return []

		tokens:list = []
		
		with tqdm(total=len(script), desc="Lexing CClear files", unit="char", disable=not show_bar) as pbar:
			i:int = 0
			r:int = 0 # Row
			c:int = 0 # Column
			while i != len(script):
				old_i:int = i
				resulting_tk:Token = Token()
				for pattern, type in self.codes.items():
					m = pattern.match(script, i)
					if m:
						text_length:int = m.end(0) - m.start(0)
						test2 = text_length

						if type != TokenTypes.NONE:
							resulting_tk = Token(script[i:i+text_length], i, r, c, type)
							tokens.append( resulting_tk )

						i += text_length
						c += text_length

						if type == TokenTypes.NEWLINE:
							c = 0
							r += 1

						break

				if tokens[-1].type == TokenTypes.ERROR:
					print("Error on line {} column {} : Invalid token '{}'"	\
						.format(resulting_tk.row,resulting_tk.col, 			\
						resulting_tk.text))
					i += 1
					c += 1
					return TokenList([])

				# Update progress bar
				if i-pbar.n > len(script)/100:
					pbar.update(i-pbar.n)

			pbar.update(i-pbar.n)

		return TokenList(tokens)

	def token_str(tokens:list) -> str:
		string:str = ""
		for token in tokens:
			string += str(string)
		return string