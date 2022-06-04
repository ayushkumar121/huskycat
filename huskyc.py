#!/usr/bin/python3

import subprocess
import sys
import copy

from compiler import compiler_program

from parser import parse_program_from_file
from typechecker import typecheck_program

def print_help():
    print("./huskycat [command] [..file]")
    print("   commands:")
    print("       - compile : compiles the given file to c code")
    print("       - dump : prints the intermeddiate representation")
    print("       - help : prints this menu")

def main() -> int:
    if len(sys.argv) < 2:
        print_help()
        print("Error: No command line arguments were provided")
        return 1
    
    if sys.argv[1] == "help":
        print_help()

    elif sys.argv[1] == "dump":
        if len(sys.argv) < 3:
            print_help()
            print("Error: No file path was provided")
        
        program = parse_program_from_file(sys.argv[2])
        for op in program.operations:
            print(f"{op.file}:{op.line}", op.type, op.oprands, op.types)
    
    elif sys.argv[1] == "compile":
        if len(sys.argv) < 3:
            print_help()
            print("Error: No file path was provided")
        
        program = parse_program_from_file(sys.argv[2])
        typecheck_program(copy.deepcopy(program))        

        c_code = compiler_program(program)

        output_file = f"{sys.argv[2]}.c"
        with open(output_file, "w") as file:
           file.write(c_code)
        
        subprocess.run(["cc", output_file])
    else:
        print_help()
        print("Error: unrecognised command")

sys.exit(main())