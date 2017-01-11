from itertools import chain

from compiler_exceptions import CompilerException


class Analyzer2(object):
    def __init__(self, parse_tree):
        self.declarations = parse_tree[1]
        self.code_commands = parse_tree[2]
        self.global_variables = set([a[:2] for a in self.declarations])
        self.initialized_variables = set()
        self.global_variables_names_with_types = {var[1]: var[0] for var in self.global_variables}
        # print parse_tree

    def analyze(self):
        in_scope_variables = set()
        self.redeclaration([])
        if self.code_commands:
            for command in self.code_commands:
                self.proceed_by_command_type(command, in_scope_variables)

    def redeclaration(self, already_declared):
        for declaration in self.declarations:
            if declaration[1] in already_declared:
                print "Redeclaration of:", declaration[1], "in line", declaration[2]
            else:
                already_declared.append(declaration[1])

    def proceed_by_command_type(self, command, in_scope_variables):
        command_type = command[0]

        if command_type == "int" or command_type == "int[]":
            self.value(command, in_scope_variables)
        elif command_type == "assign":
            self.assign(command, in_scope_variables)
        elif command_type == "if_then":
            self.if_then(command, in_scope_variables)
        elif command_type == "if_else":
            self.if_else(command, in_scope_variables)
        elif command_type == "while_loop":
            self.while_loop(command, in_scope_variables)
        elif command_type == "for_loop":
            self.for_loop(command, in_scope_variables)
        elif command_type == "read":
            self.read(command, in_scope_variables)
        elif command_type == "write":
            self.write(command, in_scope_variables)
        elif command_type == "skip":
            pass


    def value(self, value, in_scope_variables, is_r_value=True):
        if isinstance(value, long):
            return

        if value[0] == 'int[]':
            self.value(value[2], in_scope_variables)

        if self.global_variables_names_with_types.has_key(value[1]):
            if self.global_variables_names_with_types[value[1]] != value[0]:
                print 'In line', value[-1]
                print'Wrong type of variable', value[0], value[1]
                raise CompilerException()
            
        v = value[:2]
        if not (v in self.global_variables or v in in_scope_variables):
            print 'In line', value[-1]
            print'Undeclared variable', value[0], value[1]
            raise CompilerException()

        if is_r_value and v not in self.initialized_variables and v[0] == 'int':
            print 'In line ', value[-1]
            print 'Uninitialized variable', value[0], value[1]
            raise CompilerException()
        else:
            self.initialized_variables.add(v)

    def operation(self, op, in_scope_variables):
        if len(op) == 2:
            self.value(op[1], in_scope_variables)
        else:
            self.value(op[2], in_scope_variables)
            self.value(op[3], in_scope_variables)

    def assign(self, assign, in_scope_variables):
        if assign[1][:2] in in_scope_variables:
            print 'In line ', assign[1][-1]
            print 'Assignment to iterator ', assign[1][1]
            raise CompilerException()
        self.operation(assign[2], in_scope_variables)
        self.value(assign[1], in_scope_variables, is_r_value=False)

    def if_then(self, c, in_scope_variables):
        self.operation(c[1], in_scope_variables)
        self.proceed_by_command_type(c[2], in_scope_variables)

    def if_else(self, c, in_scope_variables):
        self.operation(c[1], in_scope_variables)
        self.proceed_by_command_type(c[2], in_scope_variables)
        self.proceed_by_command_type(c[3], in_scope_variables)

    def while_loop(self, c, in_scope_variables):
        self.operation(c[1], in_scope_variables)
        self.proceed_by_command_type(c[2], in_scope_variables)

    def for_loop(self, c, in_scope_variables):
        self.value(c[2], in_scope_variables)
        self.value(c[3], in_scope_variables)
        it = c[1][:2]
        in_scope_variables = set(in_scope_variables)
        in_scope_variables.add(it)
        self.initialized_variables.add(c[1])
        self.proceed_by_command_type(c[4], in_scope_variables)

    def read(self, c, in_scope_variables):
        self.value(c[1], in_scope_variables, is_r_value=False)

    def write(self, c, in_scope_variables):
        self.value(c[1], in_scope_variables)

