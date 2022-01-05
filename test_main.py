
import unittest
from cclr_py_scripts import parser
from cclr_py_scripts.commands import *
from cclr_py_scripts.lexer import Lexer, TokenList
from cclr_py_scripts.parser import Parser
from cclr_py_scripts.compiler import Compiler
from cclr_py_scripts.commands import *

class TestLexer(unittest.TestCase):

	#def test1_progress_bar(self) -> None:
	#	l = Lexer()
	#	b = "j"
	#	l.tokenize( b, True )
	#	b = "ja;skdlj;lskdjf ;saldiifhsl;dkhjf lsa;dhfgslkdjhff 98u9 w4v5t"
	#	l.tokenize( b, True )
	#	b = ""
	#	for x in range(1999):
	#		b += str(x) + " "
	#	l.tokenize( b, True )

	def test_empty(self) -> None:
		l = Lexer()
		self.assertEqual (
			l.tokenize(""),
			[] )

	def test_names(self) -> None:
		l = Lexer()
		self.assertEqual (
			str(l.tokenize("    hello my_name 2isa tes5t ____hi _yo___")),
			"     hello my_name 2 isa tes5t ____hi _yo___" )

	def test_expressions(self) -> None:
		l = Lexer()
		self.assertEqual (
			str(l.tokenize(
"""
1 + 1 + 1 + 1 + (1) + (1+1) 
	* 5 * 5 * 5 * 5 * (5) * (5*5) 
	- 6 - 6 - 6 - 6 - (6) - (6-6)
"""
			)),
			"\n 1 + 1 + 1 + 1 + ( 1 ) + ( 1 + 1 ) \n \t * 5 * 5 * 5 * 5 * ( 5 ) * ( 5 * 5 ) \n \t - 6 - 6 - 6 - 6 - ( 6 ) - ( 6 - 6 ) \n" )

	def test_numbers(self) -> None:
		l = Lexer()
		self.assertEqual (
			str(l.tokenize("1 2 3 123 4 5 6")),
			"1 2 3 123 4 5 6" )

	def test_symbols(self) -> None:
		l = Lexer()
		self.assertEqual (
			str(l.tokenize("%^&*()+-=")),
			"% ^ & * ( ) + - =" )

	def test_tokens(self) -> None:
		l = Lexer()
		self.assertEqual (
			str(l.tokenize("alc a b c do1thing 1andstuff")),
			"alc a b c do1thing 1 andstuff" )

class TestParser(unittest.TestCase):
	
	CODE_EXPR = """1 + 1 + 1 + 1 + ( 1 ) + ( 1 + 1 ) * 5 * 5 * 5 * 5 * ( 5 ) * ( 5 * 5 ) - 6 - 6 - 6 - 6 - ( 6 ) - ( 6 - 6 )"""
	CODE_ALC_BASIC = """alc var_name:int;\n"""
	CODE_ALC_ADV = """alc( static const ) var_name:int = {};\n""".format(CODE_EXPR)

	def test_expression(self) -> None:
		p = Parser()
		l = Lexer()
	
		tokens = l.tokenize(self.CODE_EXPR)
		parsed = p.parse(tokens)
	
		self.assertEqual(
			str(parsed), str(tokens)
		)

	def test_var_dec(self) -> None:
		l = Lexer()
		p = Parser()

		tk:TokenList = l.tokenize(self.CODE_ALC_BASIC)
		parsed = p.parse(tk)
		self.assertEqual(
			str(parsed), self.CODE_ALC_BASIC
		)

		tk2:TokenList = l.tokenize(self.CODE_ALC_ADV)
		parsed2 = p.parse(tk2)
		self.assertEqual(
			str(parsed2), self.CODE_ALC_ADV
		)

class TestCompiler(unittest.TestCase):

	def test_compiler(self) -> None:
		l = Lexer()
		p = Parser()
		c = Compiler()

		code = """
			alc new_var:int;
				
			alc new_var:int = 2 * 5 - (2 + 5 / 4); alc new_var2:int = (2+2+2+2+2+2);
		"""
		expected = """int new_var;
int new_var = 2 * 5 - ( 2 + 5 / 4 );
int new_var2 = ( 2 + 2 + 2 + 2 + 2 + 2 );
""" # The exact formatting of this multiline string is IMPORTANT

		compiled = c.compile( p.parse( l.tokenize(code) ) )
		
		self.assertEqual(compiled, expected)

if __name__ == "__main__":
	unittest.main()
