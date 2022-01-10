
import unittest
from cclr_py_scripts.lexer import Lexer, TokenList
from cclr_py_scripts.parser import Parser
from cclr_py_scripts.compiler import Compiler
from cclr_py_scripts.commands import *

cclr1:str = """
alc thing:stuff;
if 5;
	alc something:else;
"""
cpp1:str = """
stuff thing;
if (5):
	else:something;
"""

cclr2:str = """
alc new_var:int;
alc new_var:int = 2 * 5 - (2 + 5 / 4); alc new_var2:int = (2+2+2+2+2+2);
"""
cpp2:str = """int new_var;
int new_var = 2 * 5 - ( 2 + 5 / 4 );
int new_var2 = ( 2 + 2 + 2 + 2 + 2 + 2 );
"""

cclr3:str = """
if 5;
	if 6;
		alc num:int;
elif 7*9;
	alc is_true:bool;
elif 856;
	alc is_true2:bool;
else;
	if 99;
		alc story:str;
"""
cpp3:str = """
if (5):
{
	if (6):
	{
		int num;
	}
}
elif (7 * 9):
{
	bool is_true;
}
elif (856):
{
	bool is_true2;
}
else:
{
	if (99):
	{
		str story;
	}
}
"""

# Tuples containing (tokens:0, parsed:1, compiled:2, souce:3, and expected_compiled:4)

results1:tuple = (TokenList(),list(), "", cclr1, cpp1)
results2:tuple = (TokenList(),list(), "", cclr2, cpp2)
results3:tuple = (TokenList(),list(), "", cclr3, cpp3)


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
			str(l.tokenize("hello my_name 2isa tes5t ____hi _yo___")),
			"hello my_name 2 isa tes5t ____hi _yo___" )

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
	
		a = str(parsed)
		b = str(tokens)
		self.assertEqual(
			a, b
		)

	def test_if_statement(self) -> None:
		l:Lexer = Lexer()
		p:Parser = Parser()
		code = """if 1+2; 
	alc st:int;"""
		p.tokens = l.tokenize(code)
		parsed = p.p_ifblk_start()
		print(parsed)

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

class TestCompiler(): #TestCompiler(unittest.TestCase):

	cclr1:str = """
alc thing:stuff;
if 5;
	alc something:dat;
"""
	cpp1:str = """
stuff thing;
if (5):
{
	dat something;
}
"""
	clr2:str = """
alc new_var:int;
alc new_var:int = 2 * 5 - (2 + 5 / 4); alc new_var2:int = (2+2+2+2+2+2);
"""
	cpp2:str = """
int new_var;
int new_var = 2 * 5 - ( 2 + 5 / 4 );
int new_var2 = ( 2 + 2 + 2 + 2 + 2 + 2 );
"""
	clr3:str = """
if 5;
	if 6;
		alc num:int;
elif 7*9;
	alc is_true:bool;
elif 856;
	alc is_true2:bool;
else;
	if 99;
		alc story:str;
"""
	cpp3:str = """
if (5):
{
	if (6):
	{
		int num;
	}
}
elif (7 * 9):
{
	bool is_true;
}
elif (856):
{
	bool is_true2;
}
else:
{
	if (99):
	{
		str story;
	}
}
"""

	def test_compiler(self) -> None:
		l = Lexer()
		p = Parser()
		c = Compiler()
		
		compiled = c.compile( p.parse( l.tokenize(self.cclr1) ) )
		self.assertEqual(compiled, self.cpp1)

	def test_compiler2(self) -> None:
		l = Lexer()
		p = Parser()
		c = Compiler()

		compiled = c.compile( p.parse( l.tokenize(self.clr2) ) )
		print(f"compile '{compiled}'")
		self.assertEqual(compiled, self.cpp2)

	def test_if_elif_else(self) -> None:
		l = Lexer()
		p = Parser()
		c = Compiler()

		compiled = c.compile( p.parse( l.tokenize(self.clr3) ) )
		self.assertEqual(compiled, self.cpp3)

if __name__ == "__main__":
	unittest.main()
