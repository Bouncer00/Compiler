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
            if self.registers_full():
                self.move_value_from_register_to_memory(len(self.registers) - 1)
            register = self.get_free_register_number()
            self.add_line_of_code("ZERO " + str(register))
            if value == 0:
                return variable

            value = bin(value)[2]
            self.add_line_of_code('INC ' + str(register))
            for b in value:
                self.add_line_of_code('SHL ' + str(register))
                if b == '1':
                    self.add_line_of_code('INC ' + str(register))
            self.store_value_in_register(variable)
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
        operation = cmd[1][0]

        if operation == '>':
            reg_num = self.if_gt(cmd[1], condition_start_line)
        elif operation == '<':
            reg_num = self.if_lt(cmd[1], condition_start_line)
        elif operation == '>=':
            reg_num = self.if_lte(cmd[1], condition_start_line)
        elif operation == '<=':
            reg_num = self.if_gte(cmd[1], condition_start_line)
        elif operation == '=':
            reg_num = self.if_eq(cmd[1], condition_start_line)
        elif operation == '<>':
            reg_num = self.if_neq(cmd[1], condition_start_line)
        else:
            raise CompilerException("Not valid symbol")

        line_number_if_start = self.current_line
        self.add_line_of_code("IF_THEN_ELSE_IF_START")

        for command in cmd[2]:
            self.proceed_by_command_type(command)

        line_number_else_start = self.current_line
        self.add_line_of_code("IF_THEN_ELSE_ELSE_START")

        if self.output_code[line_number_if_start] != "IF_THEN_ELSE_IF_START":
            raise CompilerException("IF_THEN_ELSE_IF_START " + str(line_number_if_start) + " is not valid")

        self.output_code[line_number_if_start] = "JZERO " + str(reg_num) + " " + str(line_number_else_start + 1)
        for command in cmd[3]:
            self.proceed_by_command_type(command)
        line_number_after_else = self.current_line

        if self.output_code[line_number_else_start] != "IF_THEN_ELSE_ELSE_START":
            raise CompilerException("IF_THEN_ELSE_ELSE_START " + str(line_number_else_start) + " is not valid")

        self.output_code[line_number_else_start] = "JUMP " + str(line_number_after_else)
        print "if_then_else", cmd

    def while_loop(self, cmd):
        commands_to_execute = []
        print "While loop", cmd[2]
        condition_statement = cmd[1][0]

        condition = cmd[1]

        variable0 = condition[1]
        variable1 = condition[2]

        if isinstance(variable1, long) and not isinstance(variable0, long):
            if not self.variables_with_registers.has_key(variable0):
                self.move_value_from_memory_to_register(variable0)

        if not isinstance(variable0, long) and not isinstance(variable1, long):
            if not self.variables_with_registers.has_key(variable0):
                self.move_value_from_memory_to_register(variable0)
            if not self.variables_with_memory_cells.has_key(variable1):
                self.move_value_from_register_to_memory(self.variables_with_registers[variable1])

        if isinstance(variable1, long) and not isinstance(variable0, long):
            register = self.get_free_register_number()
            self.iterate_register_to_number(register, variable1)
            memory_cell = self.get_free_memory_cell_index()
            self.iterate_register_to_number(0, memory_cell)
            self.add_line_of_code("STORE " + str(register))
            self.memory_cells[memory_cell] = variable1
            self.variables_with_memory_cells[variable1] = memory_cell

        #put condition assembly command here
        self.add_line_of_code("SUB " + str(self.variables_with_registers[variable0]))
        condition_start_line = self.current_line
        self.add_line_of_code("WHILE_START")
        self.add_line_of_code("ADD " + str(self.variables_with_registers[variable0]))

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

        for command in cmd[2]:
            commands_to_execute += [self.proceed_by_command_type(command)]


        self.iterate_register_to_number(0, self.variables_with_memory_cells[variable1])
        self.add_line_of_code("JUMP " + str(condition_start_line - 1))
        after_jump_line = self.current_line

        self.output_code[condition_start_line] = self.output_code[condition_start_line].replace("WHILE_END", str(after_jump_line))

    def for_loop(self, cmd):
        print "for_loop", cmd

    def read(self, cmd):
        if self.registers_full():
            self.move_value_from_register_to_memory(len(self.registers) - 1)

        register_number = self.get_free_register_number()
        self.read_value_to_register(cmd[1], register_number)
        print "read", cmd

    def write(self, cmd):
        value = cmd[1]
        if isinstance(value, long):
            register = self.get_free_register_number()
            self.zero_register(register)

            if value == 0L:
                return

            value = bin(value)[3:]
            self.add_line_of_code('INC ' + str(register))
            for b in value:
                self.add_line_of_code('SHL ' + str(register))
                if b == '1':
                    self.add_line_of_code('INC ' + str(register))
            self.add_line_of_code('PUT ' + str(register))
            self.zero_register(register)

        else:
            if not self.variables_with_registers.has_key(value):
                self.move_value_from_memory_to_register(value)
            self.add_line_of_code('PUT ' + str(self.variables_with_registers[value]))

        print "write", cmd

    def read_value_to_register(self, value, register_number):
        self.registers[register_number] = value
        # self.registers_ready[register_number] = False
        self.variables_with_registers[value] = register_number
        self.add_line_of_code("GET " + str(register_number))

    def store_value_in_register(self, value):
        value_stored = False
        for i in xrange(1, len(self.registers)):
            if self.registers[i] is None:
                self.registers[i] = value
                self.variables_with_registers[value] = i
                # self.registers_ready[i] = False
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
        for i in range(1, len(self.memory_cells)):
            if self.memory_cells[i] is None:
                return i
        raise CompilerException("No free memory cell")

    def get_free_register_number(self):
        for i in xrange(1, len(self.registers)):
            if self.registers[i] is None:
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
        # self.registers_ready[register_number] = True
        self.add_line_of_code("ZERO " + str(register_number))

    def iterate_register_to_number(self, register_number, number):
        self.zero_register(register_number)
        for i in range(number):
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
                                                             str(self.variables_with_registers[variable0]) + " " + \
                                                             "WHILE_END"

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

    def mul(self, assign_to_var, a, b):
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

    def assign_mul(self, assign):
        assign_to_var = assign[1]
        var0 = assign[2][1]
        var1 = assign[2][2]
        if isinstance(var0, long) and not isinstance(var1, long):
            var0, var1 = var1, var0
        self.mul(assign_to_var, var0, var1)
        if assign_to_var != var0:
            register = self.variables_with_registers[var0]
            self.copy_value_from_register_to_memory(register, assign_to_var)

        print "assign mul", assign

    def assign_div(self, assign):
        assign_to_var = assign[1]
        var0 = assign[2][1]
        var1 = assign[2][2]

        if assign_to_var != var0:
            self.copy_value_from_register_to_memory(self.variables_with_registers[var0], assign_to_var)

        self.div(assign_to_var, var1)

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
            # if not self.variables_with_registers.has_key(var0):
            #     self.move_value_from_memory_to_register(var0)
            if not self.variables_with_memory_cells.has_key(var1):
                if not self.variables_with_registers.has_key(var1):
                    raise CompilerException("Variable " + var1 + " does not exist neither in memory or register")
                register_var1 = self.variables_with_registers[var1]
                self.move_value_from_register_to_memory(var1)
            var0_reg = self.variables_with_registers[var0]
            var1_mem = self.variables_with_memory_cells[var1]
            self.iterate_register_to_number(0, var1_mem)
            self.add_line_of_code("SUB " + str(var0_reg))
            return var0_reg

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

    def registers_full(self):
        for i in range(1, len(self.registers)):
            if self.registers[i] is None:
                return False
        return True


