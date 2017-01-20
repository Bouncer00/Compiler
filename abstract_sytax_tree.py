from itertools import chain


class AST:

    def __init__(self, parse_tree):
        self.parse_tree = parse_tree
        _, self.declarations, self.code_commands = parse_tree
        self.ast = []
        self.iter_no = 0

    def create(self):
        self.ast.extend(self.go_thorught_commands(self.code_commands))
        return self.ast, self.create_symtab(self.declarations)

    def go_thorught_commands(self, commands):
        parsed_commands = []
        for command in commands:
            parsed_commands.append(self.proceed_by_command_type(command))
        return parsed_commands

    def proceed_by_command_type(self, command):
        command_type = command[0]

        if command_type == "int" or command_type == "int[]":
            return self.value(command)
        elif command_type == "assign":
            return self.assign(command)
        elif command_type == "if_then":
            return self.if_then(command)
        elif command_type == "if_else":
            return self.if_else(command)
        elif command_type == "while_loop":
            return self.while_loop(command)
        elif command_type == "for_loop":
            return self.for_loop(command)
        elif command_type == "read":
            return self.read(command)
        elif command_type == "write":
            return self.write(command)
        elif command_type == "skip":
            pass

    def identifier(self, identifier):
        if identifier[0] == "int": return identifier[1]
        elif identifier[0] == "int[]":
            if isinstance(identifier[1], str):
                return (identifier[1], identifier[2][1])
            return self.identifier(identifier[1])

    def value(self, value):
        if isinstance(value, long): return value
        elif value[0] == "int": return value[1]
        elif value[0] == "int[]": return (value[1], self.value(value[2]))
        return self.identifier(value)

    def assign(self, assign):
        return "assign", self.value(assign[1]), self.expression(assign[2])

    def expression(self, expression):
        if(len(expression) == 2):
            return expression[1]
        return expression[1], self.value(expression[2]), self.value(expression[3])

    def condition(self, condition):
        return condition[1], self.value(condition[2]), self.value(condition[3])

    def if_then(self, command):
        return "if_then", self.condition(command[1]), self.go_thorught_commands(command[2])

    def if_else(self, command):
        return "if_then_else", self.condition(command[1]), self.go_thorught_commands(command[2]), self.go_thorught_commands(command[3])

    def while_loop(self, command):
        return "while_loop", self.condition(command[1]), self.go_thorught_commands(command[2])

    def for_loop(self, command):
        self.iter_no += 1
        return "for_loop", self.value(command[1]), self.value(command[2]), self.value(command[3]), self.go_thorught_commands(command[4])

    def read(self, command):
        return "read", self.value(command[1])

    def write(self, command):
        return "write", self.value(command[1])

    def create_symtab(self, declarations):
        symtab = [t[:len(t) - 1] for t in declarations]
        memory = {}
        cell_iter = 0
        for symbol in symtab:
            if symbol[0] == "int":
                memory[symbol[1]] = cell_iter
                cell_iter += 1
            elif symbol[0] == "int[]":
                for i in range(symbol[2]):
                    s = list(symbol)
                    s[2] = i
                    memory[(s[1], i)] = cell_iter
                    cell_iter += 1
        print "Symtab", symtab
        print "Memory", memory
        return symtab, memory
        # tables = [t[1:] for t in symtab if t[0] == 'int[]']
        # print "Tables", tables
        # integers = [t[1] for t in symtab if t[0] == 'int']
        # print "Integers", integers
        #
        # def f(x):
        #     return '@' + str(x)
        #
        # def g(x):
        #     return '#' + str(x)
        #
        # helpers = list(chain.from_iterable((f(x), g(x))
        #                                    for x in xrange(self.iter_no)))
        #
        # print "Helpers", helpers
        # integers.extend(helpers)
        #
        # k = 0
        # symtab = {}
        # for name in integers:
        #     symtab[name] = k
        #     k += 1
        # for name, size in tables:
        #     symtab[name] = k
        #     k += size
        #
        # return symtab
