import logging
import ply.lex as lex

from compiler_exceptions import CompilerException


class Lexer(object):
    tokens = (
        'VAR', 'BEGIN', 'END',
        'IF', 'THEN', 'ELSE', 'ENDIF',
        'WHILE', 'DO', 'ENDWHILE',
        'FOR', 'DOWNTO', 'FROM', 'TO', 'ENDFOR',
        'READ', 'WRITE',
        'SKIP',
        'LBRACKET', 'RBRACKET',
        'ASSIGN',
        'SEMICOLON',
        'PIDENTIFIER',
        'NUMBER',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
        'EQ', 'NEQ', 'LT', 'GT', 'LEQ', 'GEQ'
    )

    t_VAR = r'VAR'
    t_BEGIN = r'BEGIN'
    t_END = r'END'

    t_IF = r'IF'
    t_THEN = r'THEN'
    t_ELSE = r'ELSE'
    t_ENDIF = r'ENDIF'

    t_WHILE = r'WHILE'
    t_DO = r'DO'
    t_ENDWHILE = r'ENDWHILE'

    t_FOR = r'FOR'
    t_DOWNTO = r'DOWNTO'
    t_FROM = r'FROM'
    t_TO = r'TO'
    t_ENDFOR = r'ENDFOR'

    t_READ = r'READ'
    t_WRITE = r'WRITE|PUT'

    t_SKIP = r'SKIP'

    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'

    t_ASSIGN = r':='
    t_SEMICOLON = r';'
    t_PIDENTIFIER = r'[_a-z]+'

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MODULO = r'%'

    t_EQ = r'='
    t_NEQ = r'<>'
    t_LT = r'<'
    t_GT = r'>'
    t_LEQ = r'<='
    t_GEQ = r'>='

    t_ignore = ' \t\r'

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_NUMBER(self, t):
        r'\d+'
        t.value = long(t.value)
        return t

    def t_comment(self, t):
        r'\{[^\}]*\}'
        pass

    def t_error(self, t):
        logging.error('In line %d', t.lexer.lineno)
        logging.error('Unknown symbols "%s"', t.value.split(' ', 1))
        raise CompilerException()

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def tokenize(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if tok:
                yield tok
            else:
                break