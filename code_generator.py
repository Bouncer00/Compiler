from compiler_exceptions import CompilerException
import copy

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
        self.memory_cells = [None] * 10000

    def generate(self):
        print self.ast
        print self.table
        self.zero_registers()
        for command in self.ast:
            self.proceed_by_command_type(command)
        self.add_line_of_code("HALT")
        print "REG", self.registers
        print "MEM", self.memory_cells
        print "REG_VAR", self.variables_with_registers
        print "MEM_VAR", self.variables_with_memory_cells
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
        variable = assign[1]
        value = assign[2]


        if isinstance(value, long):
            register = self.get_free_register_number()
            self.add_line_of_code("RESET " + str(register))
            if value == 0:
                return variable

            value = bin(value)[2]
            self.add_line_of_code('INC ' + str(register))
            for b in value:
                self.add_line_of_code('SHL ' + str(register))
                if b == '1':
                    self.add_line_of_code('INC ' + str(register))
            self.store_value_in_register(variable)
            self.move_value_from_register_to_memory(register)
            return variable

        elif value[0] == "+":
            self.assign_plus(assign)
        elif value[0] == "-":
            self.assign_minus(assign)
        elif value[0] == "*":
            self.assign_mul(assign)
        elif value[0] == "/":
            self.assign_div(assign)
        elif value[0] == "%":
            self.assign_modulo(assign)

        print "assign", assign

    def if_then(self, cmd):
        condition_start_line = self.current_line
        self.add_line_of_code("IF_THEN_START")

        print "if_then", cmd

    def if_then_else(self, cmd):
        condition_start_line = self.current_line
        self.add_line_of_code("IF_THEN_ELSE_START")
        operation = cmd[1][0]

        if operation == '>':
            self.if_gt(cmd[1], condition_start_line)
        elif operation == '<':
            self.if_lt(cmd[1], condition_start_line)
        elif operation == '>=':
            self.if_lte(cmd[1], condition_start_line)
        elif operation == '<=':
            self.if_gte(cmd[1], condition_start_line)
        elif operation == '=':
            self.if_eq(cmd[1], condition_start_line)
        elif operation == '<>':
            self.if_neq(cmd[1], condition_start_line)

        for command in cmd[2]:
            self.proceed_by_command_type(command)

        for command in cmd[3]:
            self.proceed_by_command_type(command)
        print "if_then_else", cmd

    def while_loop(self, cmd):
        commands_to_execute = []
        print "While loop", cmd[2]
        condition_statement = cmd[1][0]

        #put condition assembly command here
        condition_start_line = self.current_line
        self.add_line_of_code("WHILE_START")

        for command in cmd[2]:
            commands_to_execute += [self.proceed_by_command_type(command)]

        if condition_statement == '=':
            self.eq(cmd[1], condition_start_line)
        elif condition_statement == '<>':
            self.neq(cmd[1], condition_start_line)
        elif condition_statement == '>':
            self.gt(cmd[1], condition_start_line)
        elif condition_statement == '<':
            self.lt(cmd[1], condition_start_line)
        elif condition_statement == '>=':
            self.geq(cmd[1], condition_start_line)
        elif condition_statement == '<=':
            self.leq(cmd[1], condition_start_line)


    def for_loop(self, cmd):
        print "for_loop", cmd

    def read(self, cmd):
        register_number = self.get_free_register_number()
        self.read_value_to_register(cmd[1], register_number)
        self.move_value_from_register_to_memory(register_number)
        print "read", cmd

    def write(self, cmd):
        value = cmd[1]
        if isinstance(value, long):
            register = self.get_free_register_number()
            value = bin(value)[2]
            self.add_line_of_code('INC ' + str(register))
            for b in value:
                self.add_line_of_code('SHL ' + str(register))
                if b == '1':
                    self.add_line_of_code('INC ' + str(register))
            self.add_line_of_code('PUT ' + str(register))

        else:
            if not self.variables_with_registers.has_key(value):
                self.move_value_from_memory_to_register(value)
            self.add_line_of_code('PUT ' + str(self.variables_with_registers[value]))

        print "write", cmd

    def read_value_to_register(self, value, register_number):
        self.registers[register_number] = value
        self.registers_ready[register_number] = False
        self.variables_with_registers[value] = register_number
        self.add_line_of_code("GET " + str(register_number))

    def store_value_in_register(self, value):
        value_stored = False
        for i in xrange(1, len(self.registers)):
            if self.registers_ready[i]:
                self.registers[i] = value
                self.variables_with_registers[value] = i
                self.registers_ready[i] = False
                value_stored = True
            if value_stored: break
        if not value_stored:
            raise CompilerException("Cannot find free register")

    def move_value_from_register_to_memory(self, register_number):
        value = self.registers[register_number]
        memory_cell_index = self.get_free_memory_cell_index()
        self.memory_cells[memory_cell_index] = value
        self.iterate_register_to_number(0, memory_cell_index)
        self.add_line_of_code("STORE " + str(register_number))
        self.variables_with_memory_cells[value] = memory_cell_index
        self.memory_cells[memory_cell_index] = value
        self.zero_register(register_number)
        return memory_cell_index

    def copy_value_from_register_to_memory(self, register_number, var_name):
        value = self.registers[register_number]
        memory_cell_index = self.get_free_memory_cell_index()
        self.memory_cells[memory_cell_index] = var_name
        self.iterate_register_to_number(0, memory_cell_index)
        self.add_line_of_code("STORE " + str(register_number))
        self.variables_with_memory_cells[var_name] = memory_cell_index
        self.memory_cells[memory_cell_index] = var_name
        return memory_cell_index

    def get_free_memory_cell_index(self):
        for i in range(len(self.memory_cells)):
            if self.memory_cells[i] is None:
                return i
        raise CompilerException("No free memory cell")

    def get_free_register_number(self):
        for i in xrange(1, len(self.registers)):
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

        value = self.registers[register_number]
        if value is not None:
            del(self.variables_with_registers[value])
        self.registers[register_number] = None
        self.registers_ready[register_number] = True
        self.add_line_of_code("ZERO " + str(register_number))

    def iterate_register_to_number(self, register_number, number):
        self.zero_register(register_number)
        for i in range(number + 1):
            self.add_line_of_code("INC " + str(register_number))

    def get_variable_by_name(self):
        pass


    '''Math operations'''

    def eq(self, condition, condition_start_line):
        pass

    def neq(self, condition, condition_start_line):
        pass

    def leq(self, condition, condition_start_line):
        pass

    def geq(self, condition, condition_start_line):
        pass

    def gt(self, condition, condition_start_line):
        variable0 = condition[1]
        variable1 = condition[2]

        # f.e: a > 0
        if isinstance(variable1, long) and not isinstance(variable0, long):
            if condition[2] == 0L:
                if self.output_code[condition_start_line] == "WHILE_START":
                    self.output_code[condition_start_line] = "JZERO " + \
                                                             str(self.get_variable_by_name_to_reg(variable0)) + " " + \
                                                             str(self.current_line)
                    self.add_line_of_code("JUMP " + str(condition_start_line))
                else:
                    raise CompilerException("Couldnt convert condition statement")

        # f.e: 10 > a
        if isinstance(variable0, long) and not isinstance(variable1, long):
            raise CompilerException("Not yet implemented")

        if not isinstance(variable0, long) and not isinstance(variable1, long):
            raise CompilerException("Not yet implemented")

    def lt(self, condition, commands):
        pass

    def assign_value(self):
        pass

    def get_variable_by_name_to_reg(self, variable_name):
        if not self.variables_with_registers.has_key(variable_name):
            self.move_value_from_memory_to_register(variable_name)
        return self.variables_with_registers[variable_name]

    def move_value_from_memory_to_register(self, variable_name):
        register = self.get_free_register_number()
        self.iterate_register_to_number(0, self.variables_with_memory_cells[variable_name])
        self.add_line_of_code("LOAD " + str(register))
        self.registers[register] = variable_name
        self.variables_with_registers[variable_name] = register
        return register

    def mul(self, a, b):
        if isinstance(a, long) and not isinstance(b, long):
            a,b = b,a

        if not self.variables_with_registers.has_key(a):
            self.move_value_from_memory_to_register(a)

        register_number = self.variables_with_registers[a]
        if isinstance(b, long):
            if b == 2L:
                self.add_line_of_code("SHL " + str(register_number))

    def div(self, a, b):
        if not self.variables_with_registers.has_key(a):
            self.move_value_from_memory_to_register(a)

        register_number = self.variables_with_registers[a]
        if isinstance(b, long):
            if b == 2L:
                self.add_line_of_code("SHR " + str(register_number))

    def registers_full(self):
        for register in self.registers:
            if register is None:
                return False
        return True

    def assign_mul(self, assign):
        assign_to_var = assign[1]
        var0 = assign[2][1]
        var1 = assign[2][2]
        if isinstance(var0, long) and not isinstance(var1, long):
            var0, var1 = var1, var0
        self.mul(var0, var1)
        if assign_to_var != var0:
            register = self.variables_with_registers[var0]
            self.copy_value_from_register_to_memory(register, assign_to_var)

        print "assign mul", assign

    def assign_div(self, assign):
        assign_to_var = assign[1]
        var0 = assign[2][1]
        var1 = assign[2][2]

        self.div(var0, var1)
        
        if assign_to_var != var0:
            self.copy_value_from_register_to_memory(self.variables_with_registers[var0], assign_to_var)

        print "assign div", assign

    def assign_modulo(self, assign):
        pass

    def assign_plus(self, assign):
        pass

    def assign_minus(self, assign):
        pass


    def if_eq(self, command, condition_start_line):
        var0, var1 = command[1], command[2]
        if isinstance(var0, long) and isinstance(var1, long) and var0 == var1:
            if self.output_code[condition_start_line] == "IF_THEN_ELSE_START" or \
                            self.output_code[condition_start_line] == "IF_THEN_START":
                self.output_code.pop(condition_start_line)

        print command

    def if_neq(self, command, condition_start_line):
        var0, var1 = command[1], command[2]
        if isinstance(var0, long) and isinstance(var1, long) and var0 != var1:
            if self.output_code[condition_start_line] == "IF_THEN_ELSE_START" or \
                            self.output_code[condition_start_line] == "IF_THEN_START":
                self.output_code.pop(condition_start_line)
        print command

    def if_gt(self, command, condition_start_line):
        var0, var1 = command[1], command[2]
        if isinstance(var0, long) and isinstance(var1, long) and var0 > var1:
            if self.output_code[condition_start_line] == "IF_THEN_ELSE_START" or \
                            self.output_code[condition_start_line] == "IF_THEN_START":
                self.output_code.pop(condition_start_line)

        elif isinstance(var1, long) and not isinstance(var0, long):
            print "A>NUMBER"

        elif isinstance(var0, long) and not isinstance(var1, long):
            switched_commend = copy.deepcopy(command)
            switched_commend[1] = var1
            switched_commend[2] = var0
            self.if_lt(switched_commend)

        else:
            print "A>B"
            pass
        print command

    def if_lt(self, command, condition_start_line):
        var0, var1 = command[1], command[2]
        if isinstance(var0, long) and isinstance(var1, long) and var0 < var1:
            if self.output_code[condition_start_line] == "IF_THEN_ELSE_START" or \
                            self.output_code[condition_start_line] == "IF_THEN_START":
                self.output_code.pop(condition_start_line)

        print command

    def if_gte(self, command, condition_start_line):
        var0, var1 = command[1], command[2]
        if isinstance(var0, long) and isinstance(var1, long) and var0 >= var1:
            if self.output_code[condition_start_line] == "IF_THEN_ELSE_START" or \
                            self.output_code[condition_start_line] == "IF_THEN_START":
                self.output_code.pop(condition_start_line)
        print command

    def if_lte(self, command, condition_start_line):
        var0, var1 = command[1], command[2]
        if isinstance(var0, long) and isinstance(var1, long) and var0 <= var1:
            if self.output_code[condition_start_line] == "IF_THEN_ELSE_START" or \
                            self.output_code[condition_start_line] == "IF_THEN_START":
                self.output_code.pop(condition_start_line)
        print command

    def if_mod(self, command, condition_start_line):
        var0, var1 = command[1], command[2]
        print command


