
import os
import click
from cclr.compiler import Compiler, Parser, Lexer

# =============================================================================
# Command Line Interface
# =============================================================================

@click.group()
def main() -> None:
	pass

@main.command("build")
@click.argument("script", type=click.Path(exists=True))
@click.option("-s", "--script", type=click.Path(exists=True), default="", help="Builds the specified .cclr script to .cpp and .h files.")
@click.option("-r", "--recursive", type=click.Path(exists=True), default="", help="Recursively builds all .cclr scripts in the specified folder to .cpp and .h files.")
@click.option("-w", "--workspace", type=click.Path(exists=True), default="./", help="The folder where __cclrcache__ will be stored. (Defaults to current directory)")
@click.option("-l", "--localoutput", type=bool, default=False, help="Rather than store the built .cpp and .h files in a __cclrcache__ folder store them in the same directory as their source .cclr files.")
def build( script:str, workspace:str="./", recursive:str="./", localoutput:bool=False ) -> None:
	"""
	Compiles a .cclr script to .cpp and .h files. The .cpp and .h files are then saved to __cclrcache__ in the current directory.
	"""
	assert(script.endswith(".cclr"))

	dir, file_name = os.path.split(script)
	cache_dir:str = os.path.join(workspace, "__cclrcach__")
	out_cpp:str = file_name[0:-4]+"cpp"
	out_h:str = file_name[0:-4]+"h"

	source_code:int = ""
	with open(os.path.join(".",script), "r") as file:
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
	main()