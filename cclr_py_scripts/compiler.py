
from cclr_py_scripts.commands import *
from enum import IntEnum, auto
from typing import Dict
from tqdm import tqdm

class Compiler:

	def compile( self, commands:list ) -> str:
		compiled:str = ""

		command:Command
		for command in tqdm(commands, desc="Compile C++ files", unit="command"):
			if command.type == CmdTypes.VAR_DECLATION:
				cmd_options:Command = command.cmd_options
				cmd_name:Command = command.cmd_name
				cmd_type:Command = command.cmd_type
				cmd_asignment:Command = command.cmd_asignment

				if not cmd_options.is_empty():
					dec_option:str = ""
					for dec_option in cmd_options.value.keys:
						compiled += dec_option + " "

				if not cmd_type.is_empty():
					compiled += cmd_type.value + " "
				else:
					assert(False)

				if not cmd_name.is_empty():
					compiled += cmd_name.value
				else:
					assert(False)

				if not cmd_asignment.is_empty():
					compiled += " = " + str(cmd_asignment.right)

				compiled += ";\n"

		return compiled

