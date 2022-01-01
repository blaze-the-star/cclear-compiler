
from tqdm import tqdm

class LexerState:
	idx:int = -1 # Starts at -1 because char_next increments before returning
	script:str = ""
	tokens:list = []
	show_bar:bool = False

	def __init__(self, _script:str) -> None:
		self.script = _script
		self.tokens = []

	def is_parsing(self) -> bool:
		return self.idx < len(self.script)

	def char_next(self) -> str:
		self.idx += 1
		return self.script[self.idx:self.idx+1]

	def char_now(self) -> str:
		return self.script[self.idx:self.idx+1]

	def char_spy(self) -> str:
		return self.script[self.idx+1:self.idx+2]

class Lexer:

	def is_symbol(self, char:str) -> bool:
		return char == "`" or char == "~" or char == "!" or char == "@" or		\
			char == "#" or char == "$" or char == "%" or char == "^" or			\
			char == "&" or char == "*" or char == "(" or char == ")" or			\
			char == "-" or char == "_" or char == "=" or char == "+" or 		\
			char == "[" or char == "{" or char == "]" or char == "}" or 			\
			char == "\\" or char == "|" or char == ":" or char == ";" or 		\
			char == "\"" or char == "'" or char == "," or char == "<" or 		\
			char == "." or	char == ">" or char == "/" or char == "?"			\

	def pares_state_any(self, t_state:LexerState) -> None:
		char:str = ""

		with tqdm(total=len(t_state.script), desc="Lexing CClear files", unit="char", disable=not t_state.show_bar) as pbar:
			while t_state.is_parsing():
				char = t_state.char_now()
				if char.isalnum() or (char =="_" and (t_state.char_spy() == "_" or not self.is_symbol(t_state.char_spy()) )):
					self.pares_state_word( t_state )
					continue
				elif self.is_symbol(char):
					t_state.tokens.append(char)
					t_state.char_next()
					continue
				char = t_state.char_next()
				# Update progress bar
				if t_state.idx-pbar.n > len(t_state.script)/100:
					pbar.update(t_state.idx-pbar.n)
			pbar.update(t_state.idx-pbar.n)

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

	def tokenize(self, script:str, show_bar:bool=False) -> list:
		if script == "":
			return []

		t_state:LexerState = LexerState(script)
		t_state.show_bar = show_bar
		self.pares_state_any(t_state)

		return t_state.tokens
