from sly import *

comment_start_line = 0

class CompilerLexer(Lexer):
    tokens = {PROCEDURE, IS, VAR, IDENTIFIER, BEGIN, END, PROGRAM, IF, THEN, ELSE, ENDIF, WHILE, DO,
              ENDWHILE, REPEAT, UNTIL, READ, WRITE, ASSIGN, PLUS, MINUS, TIMES, DIV, MOD, EQ, NEQ, GE, LE, GEQ, LEQ, NUMBER}
    literals = {',', ';', '(', ')'}
    ignore = ' \t'
    ignore_comment = r'\[([^]]|\n)*\]'

    @_(r'\n+')
    def newline(self, t):
        self.lineno += len(t.value)

    PROCEDURE = r"PROCEDURE"
    IS = r"IS"
    VAR = r"VAR"
    BEGIN = r"BEGIN"
    PROGRAM = r"PROGRAM"
    IF = r"IF"
    THEN = r"THEN"
    ELSE = r"ELSE"
    ENDIF = r"ENDIF"
    WHILE = r"WHILE"
    DO = r"DO"
    ENDWHILE = r"ENDWHILE"
    REPEAT = r"REPEAT"
    UNTIL = r"UNTIL"
    READ = r"READ"
    WRITE = r"WRITE"
    ASSIGN = r":="
    GEQ = r">="
    LEQ = r"<="
    PLUS = r"\+"
    MINUS = r"-"
    TIMES = r"\*"
    DIV = r"/"
    MOD = r"%"
    EQ = r"="
    NEQ = r"!="
    GE = r">"
    LE = r"<"
    END = r"END"

    NUMBER = r"\d+"
    IDENTIFIER = r"[_a-z]+"

    # @_(r'\d+')
    # def NUMBER(self, t):
    #     t.value = int(t.value)
    #     return t

    def error(self, t):
        raise Exception(f"Nierozpoznany symbol '{t.value[0]} | line: {self.lineno}'")

    def get_line(self):
        return self.lineno
