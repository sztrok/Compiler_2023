from sly import *
from lexer import CompilerLexer
from compiler import *


class Procedure:
    def __init__(self, proc_head, declarations, commands):
        self.proc_head = proc_head
        self.declarations = declarations
        self.commands = commands


class Program:
    def __init__(self, declarations, commands):
        self.declarations = declarations
        self.commands = commands


class CompilerParser(Parser):
    lexer = CompilerLexer
    tokens = CompilerLexer.tokens
    procedures_arr = []
    main_obj = None
    is_declared = {}
    is_set = {}
    is_used = {}
    line_no = 1

    @_('procedures main')
    def program_all(self, p):
        return self.procedures_arr, self.main_obj

    @_('procedures PROCEDURE proc_head IS VAR declarations BEGIN commands END')
    def procedures(self, p):
        self.line_no += 1
        new_proc = Procedure(p[2], p[5], p[7])
        for dec in new_proc.declarations:
            self.is_declared[dec] = True
        for dec in new_proc.proc_head[1]:
            self.is_declared[dec] = True
            self.is_set[dec] = True
        self.procedures_arr.append(new_proc)
        self.is_declared = {}
        self.is_set = {}
        self.is_used = {}

    @_('procedures PROCEDURE proc_head IS BEGIN commands END')
    def procedures(self, p):
        self.line_no += 1
        new_proc = Procedure(p[2], None, p[5])
        for dec in new_proc.proc_head[1]:
            self.is_declared[dec] = True
            self.is_set[dec] = True
        self.procedures_arr.append(new_proc)
        self.is_declared = {}
        self.is_set = {}
        self.is_used = {}

    @_('')
    def procedures(self, p):
        pass

    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        self.line_no += 2
        new_main = Program(p[3], p[5])
        for dec in new_main.declarations:
            self.is_declared[dec] = True
        self.main_obj = new_main

    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        self.line_no += 2
        new_main = Program(None, p[3])
        self.main_obj = new_main

    @_('IDENTIFIER "(" declarations ")"')
    def proc_head(self, p):
        self.line_no += 1
        for dec in p[2]:
            self.is_set[dec] = True
        return p[0], p[2]

    @_('declarations "," IDENTIFIER')
    def declarations(self, p):
        self.line_no += 1
        return p[0] + [p[2]]

    @_('IDENTIFIER')
    def declarations(self, p):
        return [p[0]]

    @_('commands command')
    def commands(self, p):
        return p[0] + [p[1]]

    @_('command')
    def commands(self, p):
        return [p[0]]

    @_('IDENTIFIER ASSIGN expression ";"')
    def command(self, p):
        self.line_no += 1
        self.is_set[p[0]] = True
        return "assign", p[0], p[2]

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        self.line_no += 3
        resp = "if_else", p[1], p[3], p[5]
        return resp

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        self.line_no += 2
        resp = "if", p[1], p[3]
        return resp

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        self.line_no += 2
        resp = "while", p[1], p[3]
        return resp

    @_('REPEAT commands UNTIL condition ";"')
    def command(self, p):
        self.line_no += 2
        return "repeat", p[3], p[1]

    @_('READ IDENTIFIER ";"')
    def command(self, p):
        self.line_no += 1
        self.is_set[p[1]] = True
        return "read", p[1]

    @_('WRITE value ";"')
    def command(self, p):
        self.line_no += 1
        return "write", p[1]

    @_('proc_head ";"')
    def command(self, p):
        self.line_no += 1
        return p[0]

    @_('value')
    def expression(self, p):
        self.line_no += 1
        return p[0]

    @_('value PLUS value')
    def expression(self, p):
        self.line_no += 1
        return "plus", p[0], p[2]

    @_('value MINUS value')
    def expression(self, p):
        self.line_no += 1
        return "minus", p[0], p[2]

    @_('value TIMES value')
    def expression(self, p):
        self.line_no += 1
        return "times", p[0], p[2]

    @_('value DIV value')
    def expression(self, p):
        self.line_no += 1
        return "div", p[0], p[2]

    @_('value MOD value')
    def expression(self, p):
        self.line_no += 1
        return "mod", p[0], p[2]

    @_('value EQ value')
    def condition(self, p):
        return "eq", p[0], p[2]

    @_('value NEQ value')
    def condition(self, p):
        return "neq", p[0], p[2]

    @_('value GE value')
    def condition(self, p):
        return "ge", p[0], p[2]

    @_('value LE value')
    def condition(self, p):
        return "le", p[0], p[2]

    @_('value GEQ value')
    def condition(self, p):
        return "geq", p[0], p[2]

    @_('value LEQ value')
    def condition(self, p):
        return "leq", p[0], p[2]

    @_('NUMBER')
    def value(self, p):
        return "const", p[0]

    @_('IDENTIFIER')
    def value(self, p):
        self.is_used[p[0]] = True
        # if p[0] not in self.is_set:
        #     print(f"WARNING: USING {p[0]} BEFORE SET")
        return "load", p[0]

    def error(self, token):
        print(f"Błąd składni: '{token.value}' | token: {token}")
