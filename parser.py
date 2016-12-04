import logging

import ply.yacc as yacc

from lexer import Lexer
from compiler_exceptions import CompilerException


class Parser(object):
    
    def p_program(self, p):
        'program : VAR vdeclarations BEGIN commands END'
        p[0] = ('code', p[2], p[4])

    def p_vdeclarations_int(self, p):
        'vdeclarations : vdeclarations PIDENTIFIER'
        p[0] = p[1] if p[1] else []
        p[0].append(('int', p[2], p.lineno(2)))

    def p_vdeclarations_table(self, p):
        'vdeclarations : vdeclarations PIDENTIFIER LBRACKET NUMBER RBRACKET'
        p[0] = p[1] if p[1] else []
        p[0].append(('int[]', p[2], p[4], p.lineno(2)))

    def p_vdeclarations_empty(self, p):
        'vdeclarations : empty'
        p[0] = []

    def p_commands(self, p):
        'commands : commands command'
        p[0] = p[1] if p[1] else []
        p[0].append(p[2])

    def p_commands_empty(self, p):
        'commands : empty'
        pass

    def p_command_assign(self, p):
        'command : identifier ASSIGN expression SEMICOLON'
        p[0] = ('assign', p[1], p[3])

    def p_command_if_then(self, p):
        'command : IF condition THEN commands ENDIF'
        p[0] = ('if_then', p[2], p[4])

    def p_command_if_else(self, p):
        'command : IF condition THEN commands ELSE commands ENDIF'
        p[0] = ('if_else', p[2], p[4], p[6])

    def p_command_while(self, p):
        'command : WHILE condition DO commands ENDWHILE'
        p[0] = ('while', p[2], p[4])

    def p_command_for_up(self, p):
        'command : FOR PIDENTIFIER FROM value TO value DO commands ENDFOR'
        i = ('int', p[2], p.lineno(2))
        p[0] = ('for_up', i, p[4], p[6], p[8])

    def p_command_for_down(self, p):
        'command : FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR'
        i = ('int', p[2], p.lineno(2))
        p[0] = ('for_down', i, p[4], p[6], p[8])

    def p_command_read(self, p):
        'command : READ identifier SEMICOLON'
        p[0] = ('read', p[2])

    def p_command_put(self, p):
        'command : WRITE value SEMICOLON'
        p[0] = ('write', p[2])

    def p_command_skip(self, p):
        'command : SKIP SEMICOLON'
        p[0] = ('skip')

    # expression
    def p_expression_value(self, p):
        'expression   : value'
        p[0] = ('expression', p[1])

    def p_expression(self, p):
        '''expression : value PLUS value
                      | value MINUS value
                      | value TIMES value
                      | value DIVIDE value
                      | value MODULO value'''
        p[0] = ('expression', p[2], p[1], p[3])

    # condition
    def p_condition(self, p):
        '''condition : value EQ value
                     | value NEQ value
                     | value LT value
                     | value GT value
                     | value LEQ value
                     | value GEQ value'''
        p[0] = ('condition', p[2], p[1], p[3])

    # value
    def p_value(self, p):
        '''value : NUMBER
                 | identifier'''
        p[0] = p[1]

    # identifier
    def p_identifier_var(self, p):
        'identifier : PIDENTIFIER'
        p[0] = ('int', p[1], p.lineno(1))

    def p_identifier_table_id(self, p):
        'identifier : PIDENTIFIER LBRACKET PIDENTIFIER RBRACKET'
        i = ('int', p[3], p.lineno(3))
        p[0] = ('int[]', p[1], i, p.lineno(1))

    def p_identifier_table_num(self, p):
        'identifier : PIDENTIFIER LBRACKET NUMBER RBRACKET'
        p[0] = ('int[]', p[1], p[3], p.lineno(1))

    def p_empty(self, p):
        'empty : '
        pass

    def p_error(self, p):
        print('W linii %d', p.lineno)
        print('Nieznany symbol "%s"', p.value)
        raise CompilerException()

    def __init__(self):
        self.lexer = Lexer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, write_tables=0, debug=False)

    def parse(self, data):
        if data:
            return self.parser.parse(data, self.lexer.lexer, 0, 0, None)
        else:
            logging.error("Input file is empty")
            raise CompilerException()