
import os
import click
from pathlib import Path

try:
	from compiler import Compiler
	from parser import Parser
	from lexer import Lexer
except:
	from cclr_py_scripts.compiler import Compiler
	from cclr_py_scripts.parser import Parser
	from cclr_py_scripts.lexer import Lexer
	
def name_from_path(path:str) -> str:
	out_file_n:str = path.replace("/",".")
	while out_file_n.startswith("."):
		out_file_n = out_file_n[1:]
	return out_file_n

def get_script_paths_r(search:str="./") -> list:
	paths:list = []
	for dir_p, dir_n, files in os.walk(search):
		for file_n in files:
			if file_n.endswith(".cclr"):
				paths.append( 
					os.path.join(dir_p, file_n)
				)
	return paths

# =============================================================================
# Command Line Interface
# =============================================================================

BUILD_HR:str = "Recursively builds all .cclr scripts in the	specified folder to .cpp and .h files."
BUILD_HC:str = "The cache folder where all compiled .cpp and .h files are saved."
BUILD_HL:str = "Rather than store the built .cpp and .h files in a __cclrcache__ folder store them in the same directory as their source .cclr files."

@click.group()
def main() -> None:
	pass

@main.command("build")
@click.argument("script", type=click.Path(exists=True))
@click.option("-r", "--recursive", is_flag=True, help=BUILD_HR)
@click.option("-c", "--cache", type=click.Path(exists=False),				\
	default="./__cclr__", show_default=True, help=BUILD_HC )
@click.option("-l", "--localoutput", is_flag=True, help=BUILD_HL)

def _build(script:str, cache:str, recursive:bool, localoutput:bool) -> None:
	build( script, cache, recursive, localoutput)

def build(script:str, cache:str, recursive:bool, localoutput:bool) -> None:
	"""
	Compiles a .cclr script to .cpp and .h files. The .cpp and .h files are then saved to __cclrcache__ in the current directory.
	"""
	s_paths:list = []
	if recursive:
		s_paths = get_script_paths_r(script)
	else:
		s_paths = [script]

	scripts:list = []
	for s_path in s_paths:
		with open(s_path, "r") as file:
			scripts.append( file.read() )

	# Create __cclrcache__
	if not localoutput and not os.path.isdir(cache):
		Path(cache).mkdir(parents=True)
	#	os.mkdir(cache)

	lx = Lexer()
	ps = Parser()
	cm = Compiler()
	for path, script in zip(s_paths, scripts):
		tokens:list = lx.tokenize(script)
		commands:list = ps.parse(tokens)
		cpp_code:str = cm.compile(commands)
		h_code:str = cm.compile(commands)

		# Save
		if localoutput:
			with open(path[:-4]+"cpp", "w") as file:
				file.write(cpp_code)
			with open(path[:-4]+"h", "w") as file:
				file.write(h_code)
			print("Compiled '{}' to '{}'".format(path, path[:-4]+"cpp/h"))
		else:
			out_file_n:str = name_from_path(path)
			out_file_path:str = os.path.join(cache, out_file_n)
			with open(out_file_path[:-4]+"cpp", "w") as file:
				file.write(cpp_code)
			with open(out_file_path[:-4]+"h", "w") as file:
				file.write(h_code)
			print("Compiled '{}' to '{}'".format(path, out_file_path[:-4]+"cpp/h"))

if __name__ == "__main__":
	main()
