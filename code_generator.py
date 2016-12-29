class CodeGenerator:

    def __init__(self, parse_tree):
        _, self.declarations, self.code_commands = parse_tree
        # (type, name, number, is_register - if True number is register number otherwise number is memory cell number)
        self.variables_memory = [(declaration[0], declaration[1], None, False) for declaration in self.declarations]
        self.output_code = []

    def generate(self):
        pass


    def proceed_by_command_type(self, command, in_scope_variables):
        command_type = command[0]

        if command_type == "value":
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
        pass

    def operation(self, op, in_scope_variables):
        pass

    def assign(self, assign, in_scope_variables):
        pass

    def if_then(self, cmd, in_scope_variables):
        pass

    def if_else(self, cmd, in_scope_variables):
        pass

    def while_loop(self, cmd, in_scope_variables):
        pass

    def for_loop(self, cmd, in_scope_variables):
        pass

    def read(self, cmd, in_scope_variables):
        pass

    def write(self, cmd, in_scope_variables):
        pass

    def write_code(self, code):
        self.output_code.append(code)
