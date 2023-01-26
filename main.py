# from memory import Memory
import sys

from parser import CompilerLexer, CompilerParser
from compiler import Compiler

def test(a):
    if a == 0:
        return "ERROR"

source_file = sys.argv[1]
output_file = sys.argv[2]

lexer = CompilerLexer()
parser = CompilerParser()

with open(source_file, 'r') as line:
    text = line.read()

tokens = lexer.tokenize(text)

tok = []

for token in tokens:
    tok.append(token)

tokens = lexer.tokenize(text)
procedures, main_prog = parser.parse(tokens)
tokens = lexer.tokenize(text)
comp = Compiler(procedures, main_prog, tok)
assembly = comp.assembly
with open(output_file, 'w') as destination:
    for line in assembly:
        print(line, file=destination)
