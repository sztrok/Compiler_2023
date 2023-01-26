# from memory import Memory
import sys

from parser import CompilerLexer, CompilerParser
from compiler import Compiler

source_file = sys.argv[1]
output_file = sys.argv[2]

lexer = CompilerLexer()
parser = CompilerParser()

with open(source_file, 'r') as line:
    text = line.read()

procedures, main_prog = parser.parse(lexer.tokenize(text))
comp = Compiler(procedures, main_prog)
assembly = comp.assembly
with open(output_file, 'w') as destination:
    for line in assembly:
        print(line, file=destination)
