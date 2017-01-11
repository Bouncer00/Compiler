from compiler_exceptions import CompilerException


class CodeGenerator:

    def __init__(self, abstract_syntax_tree, table):
        self.ast = abstract_syntax_tree
        self.table = table
        self.output_code = []
        self.current_line = 0
        self.variables_with_memory_cells = {}
        self.variables_with_registers = {}
        self.registers = [None, None, None, None, None]
        self.registers_ready = [False, False, False, False, False]
        self.memory_cells = []

    def generate(self):
        print self.ast
        print self.table
        self.zero_register(0)
        for command in self.ast:
            self.proceed_by_command_type(command)
        return self.output_code


    def proceed_by_command_type(self, command):
        command_type = command[0]

        if command_type == "value":
            self.value(command)
        elif command_type == "assign":
            self.assign(command)
        elif command_type == "if_then":
            self.if_then(command)
        elif command_type == "if_then_else":
            self.if_then_else(command)
        elif command_type == "while_loop":
            self.while_loop(command)
        elif command_type == "for_loop":
            self.for_loop(command)
        elif command_type == "read":
            self.read(command)
        elif command_type == "write":
            self.write(command)
        elif command_type == "skip":
            pass

    def value(self, value):
        print "value", value

    def operation(self, op):
        print "operation", op

    def assign(self, assign):
        print "assign", assign

    def if_then(self, cmd):
        print "if_then", cmd

    def if_then_else(self, cmd):
        print "if_then_else", cmd

    def while_loop(self, cmd):
        print "while_loop", cmd

    def for_loop(self, cmd):
        print "for_loop", cmd

    def read(self, cmd):
        register_number = self.get_free_register_number()
        self.read_value_to_register(cmd[1], register_number)
        print "read", cmd

    def write(self, cmd):
        print "write", cmd

    def read_value_to_register(self, value, register_number):
        value_read = False
        self.registers[register_number] = value
        self.registers_ready = False
        self.add_line_of_code("GET " + str(register_number))

    def store_value_in_register(self, value):
        value_stored = False
        for i in xrange(len(self.registers)):
            if self.registers_ready[i]:
                self.registers[i] = value
                self.registers_ready = False
                value_stored = True
        if not value_stored:
            raise CompilerException("Cannot find free register")

    def move_value_from_register_to_memory(self, register_number):
        value = self.registers[register_number]
        memory_cell_index = self.get_free_memory_cell_index()
        self.memory_cells[memory_cell_index] = value
        self.iterate_register_to_number(0, memory_cell_index)
        self.add_line_of_code("STORE" + str(register_number))

    def get_free_memory_cell_index(self):
        return len(self.memory_cells)

    def get_free_register_number(self):
        for i in xrange(len(self.registers)):
            if self.registers_ready[i]:
                return i
        raise CompilerException("No free register")

    def add_line_of_code(self, code_line):
        self.output_code += [code_line]
        self.current_line += 1

    def zero_registers(self):
        for i in xrange(len(self.registers)):
            self.zero_register(i)

    def zero_register(self, register_number):
        if register_number > len(self.registers) - 1:
            raise CompilerException("Trying to zero not existing register", register_number)
        self.registers[register_number] = None
        self.registers_ready[register_number] = True
        self.add_line_of_code("ZERO " + str(register_number))

    def iterate_register_to_number(self, register_number, number):
        self.zero_register(register_number)
        for i in range(number):
            self.add_line_of_code("INC " + str(register_number))
