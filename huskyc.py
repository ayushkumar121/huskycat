#!/usr/bin/python3

import subprocess
import sys

from compiler import compiler_program
from interpreter import interpret_program

from parser import parse_program_from_file

def print_help():
    print("./huskycat [command] [..file]")
    print("   commands:")
    print("       - run : interprets the given file")
    print("       - compile : compiles the given file to c code")
    print("       - help : prints this menu")

def main() -> int:
    if len(sys.argv) < 2:
        print_help()
        print("Error: No command line arguments were provided")
        return 1
    
    if sys.argv[1] == "help":
        print_help()
    
    if sys.argv[1] == "run":
        if len(sys.argv) < 3:
            print_help()
            print("Error: No file path was provided")
        
        program = parse_program_from_file(sys.argv[2])
        interpret_program(program)
    
    if sys.argv[1] == "compile":
        if len(sys.argv) < 3:
            print_help()
            print("Error: No file path was provided")
        
        program = parse_program_from_file(sys.argv[2])
        c_code = compiler_program(program)

        output_file = f"{sys.argv[2]}.c"
        with open(output_file, "w") as file:
           file.write(c_code)
        
        subprocess.run(["cc", output_file])

sys.exit(main())