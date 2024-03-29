#!/usr/bin/python3

from pprint import pprint
import subprocess
import sys

from compiler import compile_program
# from interpreter import interpret_program

from parser import parse_program_from_file
from typechecker import typecheck_program


def print_help():
    print("./huskycat [command] [..file]")
    print("   commands:")
    # print("       - run : interprets the program")
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

    # elif sys.argv[1] == "run":
    #     if len(sys.argv) < 3:
    #         print_help()
    #         print("Error: No file path was provided")

    #     program = parse_program_from_file(sys.argv[2])
    #     typecheck_program(program)

    #     interpret_program(program)

    elif sys.argv[1] == "dump":
        if len(sys.argv) < 3:
            print_help()
            print("Error: No file path was provided")

        program = parse_program_from_file(sys.argv[2])
        typecheck_program(program)

        pprint(program)

    elif sys.argv[1] == "compile":
        if len(sys.argv) < 3:
            print_help()
            print("Error: No file path was provided")

        program = parse_program_from_file(sys.argv[2])
        typecheck_program(program)

        c_code = compile_program(program)

        output_file = f"{sys.argv[2]}.c"
        with open(output_file, "w") as file:
            file.write(c_code)

        subprocess.run(["cc", output_file])
    
    else:
        print_help()
        print("Error: unrecognised command")


sys.exit(main())
