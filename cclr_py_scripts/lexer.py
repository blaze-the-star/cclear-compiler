
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

class TokenList(list):
	def __str__(self) -> str:
		string:str = ""
		for token in self:
			string += str(token) + " "
		return string[:-1]

class Token:
	text:str = ""
	idx:int = -1
	row:int = -1
	col:int = -1
	indent:int = -1
	type:int = TokenTypes.NONE

	def __add__(self, add_by:str) -> str:
		assert add_by is str, "TypeError: unsupported operand type(s) for +: 'Token' and '{}'".format(type(add_by).__name__)
		return self.text + add_by

	def __eq__(self, obj:object) -> bool:
		if isinstance(obj, str):
			return self.text == obj
		elif isinstance(obj, Token):
			return self.text == obj.text
		elif isinstance(obj, re.Pattern):
			return obj.fullmatch(self.text)
		elif isinstance(obj, int):
			return self.type == obj
		elif isinstance(obj, Tuple):
			if len(obj) == 2:
				return self.row == obj[0] and self.col == obj[1]
			return False
		else:
			return False

	def __init__(self, text:str="", idx:int=-1, row:int=-1, col:int=-1, indent:int=-1, type:int=TokenTypes.NONE) -> None:
		self.text = text
		self.idx = idx
		self.row = row
		self.col = col
		self.indent = indent
		self.type = type

	def __repr__(self):
		return f"'{self.text}', {self.type.__repr__()}"

	def __str__(self) -> str:
		if self.text == "NA" or self.text == "PASS":
			return ""
		return self.text

class Lexer:

	RE_INDENT = re.compile(r"(?:^)[ \t]+", flags=re.MULTILINE)

	codes:Dict = {
		re.compile(r"//.*")											:TokenTypes.COMMENT,	# Matches comment one-line 
		re.compile(r"/\*.*\*/")										:TokenTypes.COMMENT,	# Matches comment multi-line
		re.compile(r"([a-zA-Z]+|[_]+[a-zA-Z0-9])[a-zA-Z0-9_]*")		:TokenTypes.VARNAME,	# Matches variable name
		re.compile(r"alc")											:TokenTypes.KEYWORD,	# Matches keyword alc
		re.compile(r"(if|else|elif)")								:TokenTypes.KEYWORD,	# Matches keyword if else elif
		re.compile(r"[0-9]+")										:TokenTypes.INT,		# Matches meta int
		re.compile(r"[0-9]*\.[0-9]+")								:TokenTypes.FLOAT,		# Matches meta float
		re.compile(r"\n")											:TokenTypes.NEWLINE,	# Matches new-line
		RE_INDENT													:TokenTypes.INDENT,		# Matches indents at start of fline
		re.compile(r"[)(]")											:TokenTypes.SYMBOL,		# Matches parenthesis
		re.compile(r"[+\-*/|^%]")									:TokenTypes.SYMBOL,		# Matches symbols (math)
		re.compile(r"(>=|<=|==|[!&|?><=])")							:TokenTypes.SYMBOL,		# Matches symbols (logic)
		re.compile(r"[:;,]")										:TokenTypes.SYMBOL,		# Matches symbols (other)
		re.compile(r" ")											:TokenTypes.NONE,		# Match space,
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
			ind:int = 0 # Indent
			while i != len(script):
				resulting_tk:Token = Token()
				for pattern, type in self.codes.items():
					m = pattern.match(script, i)
					if m:
						text_length:int = m.end(0) - m.start(0)
						matched:str = script[i:i+text_length]

						i += text_length
						c += text_length

						if type == TokenTypes.INDENT:
							# TODO: Handle tabs and spaces
							ind += text_length
						elif type == TokenTypes.NEWLINE:
							c = 0
							ind = 0
							r += 1
						elif type == TokenTypes.NONE:
							pass
						elif type != TokenTypes.NONE:
							resulting_tk = Token(matched, i, r+1, c, ind, type)
							tokens.append( resulting_tk )

						break

				if len(tokens)!=0 and tokens[-1].type == TokenTypes.ERROR:
					print("Error on line {} column {} : Invalid token '{}'"	\
						.format(resulting_tk.row,resulting_tk.col, 			\
						resulting_tk.text))
					breakpoint()
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