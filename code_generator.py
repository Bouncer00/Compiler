from compiler_exceptions import CompilerException
import operator

class CodeGenerator:

    def __init__(self, abstract_syntax_tree, table):
        self.ast = abstract_syntax_tree
        self.sym_tab = table[0]
        self.memory = table[1]
        self.numbers = table[2]
        self.output_code = []
        self.current_line = 0
        self.variables_with_registers = {}
        self.registers = [None, None, None, None, None]

    def generate(self):
        print self.ast
        self.store_numbers_in_memory()
        for command in self.ast:
            self.proceed_by_command_type(command)
        self.add_line_of_code("HALT")
        print "REG", self.registers
        print "MEM", self.memory
        print "REG_VAR", self.variables_with_registers
        return self.output_code

    def store_numbers_in_memory(self):
        for number in self.numbers:
            self.iterate_register_to_number(0, self.memory[number])
            self.iterate_register_to_number(1, number)
            self.add_line_of_code("STORE 1")
        self.zero_register(0)
        self.zero_register(1)

    def store_value_in_register(self, value, register):
        self.registers[register] = value
        self.variables_with_registers[value] = register

    def proceed_by_command_type(self, command):
        if command is None:
            return

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
        elif command_type == "for_down":
            self.for_down(command)
        elif command_type == "for_up":
            self.for_up(command)
        elif command_type == "read":
            self.read(command)
        elif command_type == "write":
            self.write(command)
        elif command_type == "skip":
            return

        # self.zero_not_needed_registers()


    def value(self, value):
        print "value", value

    def operation(self, op):
        print "operation", op

    def assign(self, assign):
        variable = assign[1]
        value = assign[2]

        if isinstance(value, long):
            if self.variables_with_registers.has_key(variable):
                register = self.variables_with_registers[variable]
            else:
                register = self.get_free_register_number()
            self.add_line_of_code("ZERO " + str(register))
            if value == 0:
                if isinstance(variable, tuple):
                    self.iterate_register_to_number_array(0, variable)
                else:
                    self.iterate_register_to_number(0, self.memory[variable])
                self.add_line_of_code("STORE " + str(register))
                return variable

            value = bin(value)[3:]
            self.add_line_of_code('INC ' + str(register))
            for b in value:
                self.add_line_of_code('SHL ' + str(register))
                if b == '1':
                    self.add_line_of_code('INC ' + str(register))
            self.store_value_in_register(variable, register)
            if isinstance(variable, tuple):
                self.iterate_register_to_number_array(0, variable)
            else:
                self.iterate_register_to_number(0, self.memory[variable])
            self.add_line_of_code("STORE " + str(register))

            return variable

        # elif not isinstance(variable, long) and not isinstance(value, long):
        #     pass


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
        elif not isinstance(variable, long) and not isinstance(value, long):
            self.move_value_from_memory_to_register(value)
            if variable != value:
                self.copy_value_from_register_to_memory(self.variables_with_registers[value], variable)

        print "assign", assign

    def if_then(self, cmd):
        condition_statement = cmd[1][0]

        # variable0 = cmd[1][1]
        # variable1 = cmd[1][2]
        #
        # if isinstance(variable1, long) and not isinstance(variable0, long):
        #     self.move_value_from_memory_to_register(variable0)
        #
        # elif not isinstance(variable0, long) and not isinstance(variable1, long):
        #     self.move_value_from_memory_to_register(variable0)

        condition_start_line = None

        if condition_statement == '=':
            condition_start_line, number_of_commands_ = self.eq(cmd[1])
        elif condition_statement == '<>':
            condition_start_line, number_of_commands_ = self.neq(cmd[1])
        elif condition_statement == '>':
            condition_start_line, number_of_commands_ = self.gt(cmd[1])
        elif condition_statement == '<':
            condition_start_line, number_of_commands_ = self.lt(cmd[1])
        elif condition_statement == '>=':
            condition_start_line, number_of_commands_ = self.geq(cmd[1])
        elif condition_statement == '<=':
            condition_start_line, number_of_commands_ = self.leq(cmd[1])

        for command in cmd[2]:
            self.proceed_by_command_type(command)

        after_jump_line = self.current_line

        if condition_start_line is not None:
            self.output_code[condition_start_line] = self.output_code[condition_start_line].replace("END",
                                                                                                str(after_jump_line))

    def if_then_else(self, cmd):
        condition_statement = cmd[1][0]

        variable0 = cmd[1][1]
        variable1 = cmd[1][2]


        # if isinstance(variable1, long) and not isinstance(variable0, long):
        #     self.move_value_from_memory_to_register(variable0)
        #
        # elif not isinstance(variable0, long) and not isinstance(variable1, long):
        #     self.move_value_from_memory_to_register(variable0)


        condition_start_line = None

        if condition_statement == '=':
            condition_start_line, number_of_commands_ = self.eq(cmd[1])
        elif condition_statement == '<>':
            condition_start_line, number_of_commands_ = self.neq(cmd[1])
        elif condition_statement == '>':
            condition_start_line, number_of_commands_ = self.gt(cmd[1])
        elif condition_statement == '<':
            condition_start_line, number_of_commands_ = self.lt(cmd[1])
        elif condition_statement == '>=':
            condition_start_line, number_of_commands_ = self.geq(cmd[1])
        elif condition_statement == '<=':
            condition_start_line, number_of_commands_ = self.leq(cmd[1])

        for command in cmd[2]:
            self.proceed_by_command_type(command)

        # self.iterate_register_to_number(0, self.memory[variable1])
        # self.add_line_of_code("JUMP " + str(condition_start_line - 1))
        after_jump_line = self.current_line + 1

        if condition_start_line is not None:
            self.output_code[condition_start_line] = self.output_code[condition_start_line].replace("END",
                                                                                                str(after_jump_line))

        self.add_line_of_code("START")
        line_number_else_start = self.current_line - 1

        for command in cmd[3]:
            self.proceed_by_command_type(command)
        # self.add_line_of_code("ADD " + str(self.variables_with_registers[variable0]))
        line_number_after_else = self.current_line

        if self.output_code[line_number_else_start] != "START":
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
        condition_start = self.current_line

        if isinstance(variable1, long) and not isinstance(variable0, long):
            self.move_value_from_memory_to_register(variable0)

        # elif isinstance(variable0, long) and not isinstance(variable1, long):
        #     self.move_value_from_register_to_memory(variable1)

        elif not isinstance(variable0, long) and not isinstance(variable1, long):
            self.move_value_from_memory_to_register(variable0)

        condition_start_line = 0
        number_of_commands = 0

        if condition_statement == '=':
            condition_start_line, number_of_commands = self.eq(cmd[1])
        elif condition_statement == '<>':
            condition_start_line, number_of_commands = self.neq(cmd[1])
        elif condition_statement == '>':
            condition_start_line, number_of_commands = self.gt(cmd[1])
        elif condition_statement == '<':
            condition_start_line, number_of_commands = self.lt(cmd[1])
        elif condition_statement == '>=':
            condition_start_line, number_of_commands = self.geq(cmd[1])
        elif condition_statement == '<=':
            condition_start_line, number_of_commands = self.leq(cmd[1])

        for command in cmd[2]:
            commands_to_execute += [self.proceed_by_command_type(command)]

        self.iterate_register_to_number(0, self.memory[variable1])
        self.add_line_of_code("JUMP " + str(condition_start))
        after_jump_line = self.current_line

        self.output_code[condition_start_line] = self.output_code[condition_start_line].replace("END", str(after_jump_line))

    def for_down(self, cmd):
        iterator = cmd[1]
        start = cmd[2]
        end = cmd[3]
        self.move_value_from_memory_to_register(start)
        self.assign(("", iterator, start))

        for_start_line = self.current_line
        self.move_value_from_memory_to_register(iterator)
        self.iterate_register_to_number(0, self.memory[end])
        self.add_line_of_code("INC " + str(self.variables_with_registers[iterator]))
        self.add_line_of_code("SUB " + str(self.variables_with_registers[iterator]))
        jzero_start = self.current_line
        self.add_line_of_code("JZERO " + str(self.variables_with_registers[iterator]) + " END")
        self.move_value_from_memory_to_register(iterator)

        for command in cmd[4]:
            self.proceed_by_command_type(command)

        self.move_value_from_memory_to_register(iterator)
        self.add_line_of_code("DEC " + str(self.variables_with_registers[iterator]))
        self.move_value_from_register_to_memory(self.variables_with_registers[iterator])
        self.add_line_of_code("JUMP " + str(for_start_line))
        after_jzero_line = self.current_line
        self.output_code[jzero_start] = self.output_code[jzero_start].replace("END", str(after_jzero_line))
        print "for_down", cmd

    def for_up(self, cmd):
        iterator = cmd[1]
        start = cmd[2]
        end = cmd[3]
        self.move_value_from_memory_to_register(start)
        self.assign(("", iterator, start))

        for_start_line = self.current_line
        self.move_value_from_memory_to_register(end)
        self.iterate_register_to_number(0, self.memory[iterator])
        self.add_line_of_code("SUB " + str(self.variables_with_registers[end]))
        jzero_start = self.current_line
        self.add_line_of_code("JZERO " + str(self.variables_with_registers[end]) + " END")
        # self.move_value_from_memory_to_register(iterator)
        for command in cmd[4]:
            self.proceed_by_command_type(command)

        self.move_value_from_memory_to_register(iterator)
        self.add_line_of_code("INC " + str(self.variables_with_registers[iterator]))
        self.move_value_from_register_to_memory(self.variables_with_registers[iterator])
        self.add_line_of_code("JUMP " + str(for_start_line))
        after_jzero_line = self.current_line
        self.output_code[jzero_start] = self.output_code[jzero_start].replace("END", str(after_jzero_line))
        print "for_up", cmd

    def read(self, cmd):
        register_number = self.get_free_register_number()
        self.read_value_to_register(cmd[1], register_number)
        self.move_value_from_register_to_memory(register_number)
        print "read", cmd

    def write(self, cmd):
        value = cmd[1]
        if isinstance(value, long):
            register = 0
            self.zero_register(register)

            if value != 0L:
                value = bin(value)[3:]
                self.add_line_of_code('INC ' + str(register))
                for b in value:
                    self.add_line_of_code('SHL ' + str(register))
                    if b == '1':
                        self.add_line_of_code('INC ' + str(register))
            self.add_line_of_code('PUT ' + str(register))
            self.zero_register(register)

        else:
            self.move_value_from_memory_to_register(value)
            self.add_line_of_code('PUT ' + str(self.variables_with_registers[value]))

        print "write", cmd

    def read_value_to_register(self, value, register_number):
        self.registers[register_number] = value
        self.variables_with_registers[value] = register_number
        self.add_line_of_code("GET " + str(register_number))

    # def move_value_from_register_to_memory(self, register_number):
    #     value = self.registers[register_number]
    #     memory_cell_index = self.memory[value]
    #     self.iterate_register_to_number(0, memory_cell_index)
    #     self.add_line_of_code("STORE " + str(register_number))
    #     return memory_cell_index

    def move_value_from_register_to_memory(self, register_number):
        var_name = self.registers[register_number]
        if isinstance(var_name, tuple):
            self.iterate_register_to_number_array(0, self.memory[var_name])
        else:
            self.iterate_register_to_number(0, self.memory[var_name])
        self.add_line_of_code("STORE " + str(register_number))
        return self.memory[var_name]

    def copy_value_from_register_to_memory_array(self, register_number, var_name):
        number_of_commands = 0
        start_of_array_memory = self.memory[var_name]
        number_of_commands += self.iterate_register_to_number(0, start_of_array_memory)
        self.add_line_of_code("STORE " + str(register_number))
        return number_of_commands

    def copy_value_from_register_to_memory(self, register_number, var_name):
        if isinstance(var_name, tuple):
            self.iterate_register_to_number_array(0, var_name)
        else:
            self.iterate_register_to_number(0, self.memory[var_name])
        self.add_line_of_code("STORE " + str(register_number))

    def copy_value_from_memory_to_register(self, register_number, var_name):
        if isinstance(var_name, tuple):
            self.iterate_register_to_number_array(0, self.memory[var_name])
        else:
            self.iterate_register_to_number(0, self.memory[var_name])
        self.add_line_of_code("LOAD " + str(register_number))

    def get_free_register_number(self):

        for i in xrange(1, len(self.registers)):
            if self.registers[i] == 0 or self.registers[i] is None or isinstance(self.registers[i], long):
                return i

        numbers = []
        for i in xrange(len(self.registers)):
            if isinstance(self.registers[i], long):
                numbers.append(i)
        if len(numbers) > 0:
            for number in numbers:
                self.zero_register(number)
        else:
            self.zero_registers()

        for i in xrange(1, len(self.registers)):
            if self.registers[i] == 0 or self.registers[i] is None or isinstance(self.registers[i], long):
                return i

    def add_line_of_code(self, code_line):
        self.output_code += [code_line]
        self.current_line += 1

    def zero_not_needed_registers(self):
        numbers = []
        for i in xrange(len(self.registers)):
            if isinstance(self.registers[i], long):
                numbers.append(i)
        if len(numbers) > 0:
            for number in numbers:
                self.zero_register(number)
        else:
            self.zero_registers()


    def zero_registers(self):
        for i in xrange(len(self.registers)):
            self.zero_register(i)

    def zero_register(self, register_number):
        if register_number > len(self.registers) - 1:
            raise CompilerException("Trying to zero not existing register", register_number)
        self.registers[register_number] = 0
        self.add_line_of_code("ZERO " + str(register_number))

    def iterate_register_to_number(self, register_number, number):
        number_of_commands = 0
        self.add_line_of_code("ZERO " + str(register_number))
        number_of_commands += 1
        if number == 0:
            return number
        value = bin(number)[3:]
        self.add_line_of_code('INC ' + str(register_number))
        number_of_commands += 1
        for b in value:
            self.add_line_of_code('SHL ' + str(register_number))
            number_of_commands += 1
            if b == '1':
                self.add_line_of_code('INC ' + str(register_number))
                number_of_commands += 1
        self.registers[register_number] = number
        return number_of_commands

    def iterate_register_to_number_array(self, register, variable):
        # if(register == 0):
        if(register !=0):
            raise CompilerException("Register cannot be != 0")
        number_of_commands = 0
        start_of_array_memory = self.memory[(variable[0]), 0]
        iterator = variable[1]
        self.move_value_from_memory_to_register(iterator)
        number_of_commands += self.iterate_register_to_number(0, self.memory[iterator])
        number_of_commands += self.iterate_register_to_number(4, start_of_array_memory)
        self.add_line_of_code("ADD " + str(4))
        number_of_commands += 1
        self.add_line_of_code("COPY " + str(4))
        number_of_commands += 1
        self.zero_register(4)
        number_of_commands += 1
        return number_of_commands


    # else:
        #     raise CompilerException("Not yet implemented")
        #     print variable


    def get_variable_by_name(self):
        pass


    '''Math operations'''

    def eq(self, condition):
        variable0 = condition[1]
        variable1 = condition[2]

        number_of_commands = 0

        if isinstance(variable0, long) and isinstance(variable1, long):
            if variable0 == variable1:
                return False, False

        self.move_value_from_memory_to_register(variable0)

        if isinstance(variable1, tuple):
            number_of_commands += self.iterate_register_to_number_array(0, variable1)
        else:
            number_of_commands += self.iterate_register_to_number(0, self.memory[variable1])

        self.add_line_of_code("SUB " + str(self.variables_with_registers[variable0]))
        condition_start_line0 = self.current_line
        self.add_line_of_code("JZERO " + str(self.variables_with_registers[variable0]) + " END")
        jump0_line = self.current_line
        self.add_line_of_code("JUMP END")

        second_check_line = self.current_line
        self.move_value_from_memory_to_register(variable1)

        if isinstance(variable0, tuple):
            number_of_commands += self.iterate_register_to_number_array(0, variable0)
        else:
            number_of_commands += self.iterate_register_to_number(0, self.memory[variable0])

        self.add_line_of_code("SUB " + str(self.variables_with_registers[variable1]))
        condition_start_line1 = self.current_line
        self.add_line_of_code("JZERO " + str(self.variables_with_registers[variable1]) + " END")

        self.output_code[condition_start_line0] = self.output_code[condition_start_line0].replace("END", str(
            second_check_line))
        self.output_code[condition_start_line1] = self.output_code[condition_start_line1].replace("END", str(self.current_line))

        return jump0_line, number_of_commands

    def neq(self, condition):
        variable0 = condition[1]
        variable1 = condition[2]

        number_of_commands = 0

        if isinstance(variable0, long) and isinstance(variable1, long):
            if variable0 != variable1:
                return False, False

        self.move_value_from_memory_to_register(variable0)

        if isinstance(variable1, tuple):
            number_of_commands += self.iterate_register_to_number_array(0, variable1)
        else:
            number_of_commands += self.iterate_register_to_number(0, self.memory[variable1])

        self.add_line_of_code("SUB " + str(self.variables_with_registers[variable0]))
        condition_start_line0 = self.current_line
        self.add_line_of_code("JZERO " + str(self.variables_with_registers[variable0]) + " END")
        jump0_line = self.current_line
        self.add_line_of_code("JUMP AFTER_SECOND_COND")

        second_check_line = self.current_line
        self.move_value_from_memory_to_register(variable1)

        if isinstance(variable0, tuple):
            number_of_commands += self.iterate_register_to_number_array(0, variable0)
        else:
            number_of_commands += self.iterate_register_to_number(0, self.memory[variable0])

        self.add_line_of_code("SUB " + str(self.variables_with_registers[variable1]))
        condition_start_line1 = self.current_line
        self.add_line_of_code("JZERO " + str(self.variables_with_registers[variable1]) + " END")

        self.output_code[condition_start_line0] = self.output_code[condition_start_line0].replace("END", str(second_check_line))
        self.output_code[jump0_line] = self.output_code[jump0_line].replace("AFTER_SECOND_COND", str(self.current_line))

        return condition_start_line1, number_of_commands

    def leq(self, condition):
        variable0 = condition[1]
        variable1 = condition[2]

        number_of_commands = 0

        if isinstance(variable0, long) and isinstance(variable1, long):
            if variable0 > variable1:
                return False, False

        self.move_value_from_memory_to_register(variable1)

        if isinstance(variable1, tuple):
            number_of_commands += self.iterate_register_to_number_array(0, variable0)
        else:
            number_of_commands += self.iterate_register_to_number(0, self.memory[variable0])

        self.add_line_of_code("INC " + str(self.variables_with_registers[variable1]))
        self.add_line_of_code("SUB " + str(self.variables_with_registers[variable1]))
        condition_start_line0 = self.current_line
        self.add_line_of_code("JZERO " + str(self.variables_with_registers[variable1]) + " END")
        return condition_start_line0, number_of_commands

    def geq(self, condition):
        variable0 = condition[1]
        variable1 = condition[2]

        number_of_commands = 0

        if isinstance(variable0, long) and isinstance(variable1, long):
            if variable0 > variable1:
                return False, False

        self.move_value_from_memory_to_register(variable0)

        if isinstance(variable1, tuple):
            number_of_commands += self.iterate_register_to_number_array(0, variable1)
        else:
            number_of_commands += self.iterate_register_to_number(0, self.memory[variable1])

        self.add_line_of_code("INC " + str(self.variables_with_registers[variable0]))
        self.add_line_of_code("SUB " + str(self.variables_with_registers[variable0]))
        condition_start_line0 = self.current_line
        self.add_line_of_code("JZERO " + str(self.variables_with_registers[variable0]) + " END")
        return condition_start_line0, number_of_commands

    def gt(self, condition):
        variable0 = condition[1]
        variable1 = condition[2]

        number_of_commands = 0

        if isinstance(variable0, long) and isinstance(variable1, long):
            if variable0 > variable1:
                return False, False

        self.move_value_from_memory_to_register(variable0)

        if isinstance(variable1, tuple):
            number_of_commands += self.iterate_register_to_number_array(0, variable1)
        else:
            number_of_commands += self.iterate_register_to_number(0, self.memory[variable1])

        self.add_line_of_code("SUB " + str(self.variables_with_registers[variable0]))
        condition_start_line0 = self.current_line
        self.add_line_of_code("JZERO " + str(self.variables_with_registers[variable0]) + " END")
        return condition_start_line0, number_of_commands


    # def gt(self, condition):
    #     variable0 = condition[1]
    #     variable1 = condition[2]
    #
    #     if isinstance(variable0, tuple) and not isinstance(variable1, tuple):
    #         pass
    #     elif not isinstance(variable0, tuple) and isinstance(variable1, tuple):
    #         pass
    #
    #     # f.e: a > 0
    #     elif isinstance(variable1, long) and not isinstance(variable0, long):
    #         # self.move_value_from_memory_to_register(variable0)
    #
    #         number_of_commands = 0
    #         self.zero_register(0)
    #         number_of_commands += 1
    #         number_of_commands += self.iterate_register_to_number(0, self.memory[condition[2]])
    #         self.add_line_of_code("SUB " + str(self.variables_with_registers[variable0]))
    #         condition_start_line = self.current_line
    #         self.add_line_of_code("JZERO " + str(self.variables_with_registers[variable0]) + " END")
    #         self.move_value_from_memory_to_register(variable0)
    #         # if self.output_code[condition_start_line] == "START":
    #         #     self.output_code[condition_start_line] = "JZERO " + \
    #         #                                              str(self.variables_with_registers[variable0]) + " " + \
    #         #                                              "END"
    #         # self.add_line_of_code("ADD " + str(self.variables_with_registers[variable0]))
    #
    #             # else:
    #             #     raise CompilerException("Couldnt convert condition statement")
    #
    #         return condition_start_line, number_of_commands + 3
    #
    #     # f.e: 10 > a
    #     elif isinstance(variable0, long) and not isinstance(variable1, long):
    #         raise CompilerException("Not yet implemented")
    #
    #     elif isinstance(variable0, long) and isinstance(variable1, long):
    #         pass
    #
    #     elif not isinstance(variable0, long) and not isinstance(variable1, long):
    #         var0_reg = self.variables_with_registers[variable0]
    #         var1_mem = self.memory[variable1]
    #         self.zero_register(0)
    #         number_of_commands = self.iterate_register_to_number(0, var1_mem)
    #         self.add_line_of_code("SUB " + str(var0_reg))
    #         condition_start_line = self.current_line
    #         self.add_line_of_code("JZERO " + str(self.variables_with_registers[variable0]) + " END")
    #         self.move_value_from_memory_to_register(variable0)
    #
    #
    #         return condition_start_line, number_of_commands
    #
    #     else:
    #         raise CompilerException("WTF")

    def lt(self, condition):
        variable0 = condition[1]
        variable1 = condition[2]

        number_of_commands = 0

        if isinstance(variable0, long) and isinstance(variable1, long):
            if variable0 > variable1:
                return False, False

        self.move_value_from_memory_to_register(variable1)

        if isinstance(variable1, tuple):
            number_of_commands += self.iterate_register_to_number_array(0, variable0)
        else:
            number_of_commands += self.iterate_register_to_number(0, self.memory[variable0])

        self.add_line_of_code("SUB " + str(self.variables_with_registers[variable1]))
        condition_start_line0 = self.current_line
        self.add_line_of_code("JZERO " + str(self.variables_with_registers[variable1]) + " END")
        return condition_start_line0, number_of_commands

    def get_variable_by_name_to_reg(self, variable_name):
        if not self.variables_with_registers.has_key(variable_name):
            self.move_value_from_memory_to_register(variable_name)
        return self.variables_with_registers[variable_name]

    def move_value_from_memory_to_register(self, variable_name):
        number_of_commands = 0
        if isinstance(variable_name, tuple) and variable_name[0].endswith("copy_name"):
            if self.variables_with_registers.has_key(variable_name):
                register = self.variables_with_registers[variable_name]
            else:
                register = self.get_free_register_number()
            self.zero_register(0)
            number_of_commands += 1
            number_of_commands += self.iterate_register_to_number(0, self.memory[variable_name])
            self.add_line_of_code("LOAD " + str(register))
            number_of_commands += 1
            self.registers[register] = variable_name
            self.variables_with_registers[variable_name] = register
            return number_of_commands

        elif isinstance(variable_name, tuple):
            if self.variables_with_registers.has_key(variable_name):
                register = self.variables_with_registers[variable_name]
            else:
                register = self.get_free_register_number()
            number_of_commands += self.iterate_register_to_number_array(0, variable_name)
            self.add_line_of_code("LOAD " + str(register))
            number_of_commands += 1
            self.registers[register] = variable_name
            self.variables_with_registers[variable_name] = register

        else:
            if self.variables_with_registers.has_key(variable_name):
                register = self.variables_with_registers[variable_name]
            else:
                register = self.get_free_register_number()
            self.zero_register(0)
            number_of_commands += 1
            number_of_commands += self.iterate_register_to_number(0, self.memory[variable_name])
            self.add_line_of_code("LOAD " + str(register))
            number_of_commands += 1
            self.registers[register] = variable_name
            self.variables_with_registers[variable_name] = register
            return number_of_commands

    def get_free_memory_cell(self):
        return max(self.memory.iteritems(), key=operator.itemgetter(1))[1] + 1

    def mul(self, a, b):
        if isinstance(a, long) and not isinstance(b, long):
            a,b = b,a

        # if not self.variables_with_registers.has_key(a):
        #     self.move_value_from_memory_to_register(a)

        register_number = self.variables_with_registers[a]
        if isinstance(b, long):
            if b == 2L:
                self.add_line_of_code("SHL " + str(register_number))

    def div(self, a, b):
        register_number = self.variables_with_registers[a]
        if isinstance(b, long):
            if b == 2L:
                self.add_line_of_code("SHR " + str(register_number))

    def assign_mul(self, assign):
        assign_to_var = assign[1]
        var0 = assign[2][1]
        var1 = assign[2][2]

        if isinstance(var1, long):
            var0, var1 = var1, var0

        var0_copy_name = "assign_mul_var0_copy_name"
        var1_copy_name = "assign_mul_var1_copy_name"

        self.memory[var0_copy_name] = self.get_free_memory_cell()
        self.memory[var1_copy_name] = self.get_free_memory_cell()

        self.move_value_from_memory_to_register(var0)
        self.copy_value_from_register_to_memory(self.variables_with_registers[var0], var0_copy_name)

        self.move_value_from_memory_to_register(var1)
        self.copy_value_from_register_to_memory(self.variables_with_registers[var1], var1_copy_name)

        self.move_value_from_memory_to_register(assign_to_var)
        self.add_line_of_code("ZERO " + str(self.variables_with_registers[assign_to_var]))

        jzero_line_start = self.current_line
        self.move_value_from_memory_to_register(var0_copy_name)
        jzero_inst_line = self.current_line
        self.add_line_of_code("JZERO " + str(self.variables_with_registers[var0_copy_name]) + " END")
        jodd_line = self.current_line
        self.add_line_of_code("JODD " + str(self.variables_with_registers[var0_copy_name]) + " ADDING")
        multi_line = self.current_line
        self.add_line_of_code("JUMP " + "SHIFT")

        add_line = self.current_line
        self.iterate_register_to_number(0, self.memory[var1_copy_name])
        self.add_line_of_code("ADD " + str(self.variables_with_registers[assign_to_var]))
        self.move_value_from_register_to_memory(self.variables_with_registers[assign_to_var])

        shift_line = self.current_line
        self.move_value_from_memory_to_register(var0_copy_name)
        self.add_line_of_code("SHR " + str(self.variables_with_registers[var0_copy_name]))
        self.move_value_from_register_to_memory(self.variables_with_registers[var0_copy_name])

        self.move_value_from_memory_to_register(var1_copy_name)
        self.add_line_of_code("SHL " + str(self.variables_with_registers[var1_copy_name]))
        self.move_value_from_register_to_memory(self.variables_with_registers[var1_copy_name])

        self.add_line_of_code("JUMP " + str(jzero_line_start))

        self.output_code[jodd_line] = self.output_code[jodd_line].replace("ADDING", str(add_line))
        self.output_code[multi_line] = self.output_code[multi_line].replace("SHIFT", str(shift_line))
        self.output_code[jzero_inst_line] = self.output_code[jzero_inst_line].replace("END", str(self.current_line))

        return jzero_inst_line

    # def assign_mul(self, assign):
    #     assign_to_var = assign[1]
    #     var0 = assign[2][1]
    #     var1 = assign[2][2]
    # 
    #     if isinstance(var1, long):
    #         var0, var1 = var1, var0
    # 
    #     self.move_value_from_memory_to_register(assign_to_var)
    #     self.add_line_of_code("ZERO " + str(self.variables_with_registers[assign_to_var]))
    # 
    #     jzero_line_start = self.current_line
    #     self.move_value_from_memory_to_register(var0)
    #     jzero_inst_line = self.current_line
    #     self.add_line_of_code("JZERO " + str(self.variables_with_registers[var0]) + " END")
    #     jodd_line = self.current_line
    #     self.add_line_of_code("JODD " + str(self.variables_with_registers[var0]) + " ADDING")
    #     multi_line = self.current_line
    #     self.add_line_of_code("JUMP " + "SHIFT")
    # 
    #     add_line = self.current_line
    #     self.iterate_register_to_number(0, self.memory[var1])
    #     self.add_line_of_code("ADD " + str(self.variables_with_registers[assign_to_var]))
    #     self.move_value_from_register_to_memory(self.variables_with_registers[assign_to_var])
    # 
    #     shift_line = self.current_line
    #     self.move_value_from_memory_to_register(var0)
    #     self.add_line_of_code("SHR " + str(self.variables_with_registers[var0]))
    #     self.move_value_from_register_to_memory(self.variables_with_registers[var0])
    # 
    #     self.move_value_from_memory_to_register(var1)
    #     self.add_line_of_code("SHL " + str(self.variables_with_registers[var1]))
    #     self.move_value_from_register_to_memory(self.variables_with_registers[var1])
    # 
    #     self.add_line_of_code("JUMP " + str(jzero_line_start))
    # 
    #     self.output_code[jodd_line] = self.output_code[jodd_line].replace("ADDING", str(add_line))
    #     self.output_code[multi_line] = self.output_code[multi_line].replace("SHIFT", str(shift_line))
    #     self.output_code[jzero_inst_line] = self.output_code[jzero_inst_line].replace("END", str(self.current_line))

    #    return jzero_inst_line

    # def assign_div(self, assign):
    #     assign_to_var = assign[1]
    #     var0 = assign[2][1]
    #     var1 = assign[2][2]
    #     d = self.memory[assign_to_var]
    #     a = self.memory[var0]
    #     b = self.memory[var1]
    #     c_name = 'temporary_div_variable_c'
    #     d_name = 'temporary_div_variable_d'
    #     self.memory[c_name] = self.get_free_memory_cell()
    #     self.memory[d_name] = self.get_free_memory_cell()
    #     self.move_value_from_memory_to_register(c_name)
    #     self.add_line_of_code("ZERO " + str(self.variables_with_registers[c_name]))
    #     self.move_value_from_register_to_memory(self.variables_with_registers[c_name])
    #     self.registers[self.variables_with_registers[c_name]] = None
    #     del self.variables_with_registers[c_name]
    #     self.move_value_from_memory_to_register(d_name)
    #     self.add_line_of_code("ZERO " + str(self.variables_with_registers[d_name]))
    #     self.move_value_from_register_to_memory(self.variables_with_registers[d_name])
    #     self.registers[self.variables_with_registers[d_name]] = None
    #     del self.variables_with_registers[d_name]
    #
    #     self.move_value_from_memory_to_register(var0)
    #     self.add_line_of_code("JZERO " + str(self.variables_with_registers[var0]) + " END")
        # self.move_value_from_register_to_memory()



    # def assign_mul(self, assign):
    #     assign_to_var = assign[1]
    #     var0 = assign[2][1]
    #     var1 = assign[2][2]
    #     # if isinstance(var0, long) and not isinstance(var1, long):
    #     #     var0, var1 = var1, var0
    #
    #     if not isinstance(var0, long) and isinstance(var1, long):
    #         self.move_value_from_memory_to_register(var0)
    #         if assign_to_var != var0:
    #             self.copy_value_from_register_to_memory(self.variables_with_registers[var0], assign_to_var)
    #
    #     elif isinstance(var0, long) and not isinstance(var1, long):
    #         self.move_value_from_memory_to_register(var1)
    #         if assign_to_var != var1:
    #             self.copy_value_from_register_to_memory(self.variables_with_registers[var1], assign_to_var)
    #
    #     self.move_value_from_memory_to_register(assign_to_var)
    #
    #     if isinstance(var0, long) and not isinstance(var1, long):
    #         self.mul(assign_to_var, var0)
    #     elif not isinstance(var0, long) and isinstance(var1, long):
    #         self.mul(assign_to_var, var1)
    #     elif assign_to_var == var0:
    #         self.mul(assign_to_var, var1)
    #     elif assign_to_var == var1:
    #         self.mul(assign_to_var, var0)
    #
    #     self.move_value_from_register_to_memory(self.variables_with_registers[assign_to_var])
    #
    #     print "assign mul", assign

    def assign_div(self, assign):
        assign_to_var = assign[1]
        var0 = assign[2][1]
        var1 = assign[2][2]

        if isinstance(var0, long) and isinstance(var1, long):
            result = var0 // var1
            self.iterate_register_to_number(0, self.memory[assign_to_var])
            self.iterate_register_to_number(1, result)
            self.add_line_of_code("STORE 1")

        # TODO: check if this type of division if proper, commented below one works with program0.imp
        elif not isinstance(var0, long) and isinstance(var1, long):
            self.move_value_from_memory_to_register(var0)
            if assign_to_var != var0:
                self.copy_value_from_register_to_memory(self.variables_with_registers[var0], assign_to_var)
            self.move_value_from_memory_to_register(assign_to_var)
            self.div(assign_to_var, var1)
            self.move_value_from_register_to_memory(self.variables_with_registers[assign_to_var])

        elif isinstance(var0, long) and not isinstance(var1, long):
            self.move_value_from_memory_to_register(var1)
            if assign_to_var != var1:
                self.copy_value_from_register_to_memory(self.variables_with_registers[var1], assign_to_var)
            self.move_value_from_memory_to_register(assign_to_var)
            self.div(assign_to_var, var1)
            self.move_value_from_register_to_memory(self.variables_with_registers[assign_to_var])

        elif not isinstance(var0, long) and not isinstance(var1, long):
            self.move_value_from_memory_to_register(var0)
            if assign_to_var != var0:
                self.copy_value_from_register_to_memory(self.variables_with_registers[var0], assign_to_var)
            self.div(assign_to_var, var1)
            self.move_value_from_register_to_memory(self.variables_with_registers[assign_to_var])

        # self.move_value_from_memory_to_register(var0)
        # if assign_to_var != var0:
        #     self.copy_value_from_register_to_memory(self.variables_with_registers[var0], assign_to_var)

        # self.move_value_from_memory_to_register(assign_to_var)
        #
        # self.div(assign_to_var, var1)
        #
        # self.move_value_from_register_to_memory(self.variables_with_registers[assign_to_var])

        print "assign div", assign

    def assign_modulo(self, assign):
        assign_to_var = assign[1]
        var0 = assign[2][1]
        var1 = assign[2][2]

        if isinstance(var0, long) and isinstance(var1, long):
            result = var0 % var1
            self.iterate_register_to_number(0, self.memory[assign_to_var])
            self.iterate_register_to_number(1, result)
            self.add_line_of_code("STORE 1")

        pass

    def assign_plus(self, assign):
        assign_to_var = assign[1]
        var0 = assign[2][1]
        var1 = assign[2][2]

        if isinstance(var0, long) and isinstance(var1, long):
            result = var0 + var1
            if isinstance(assign_to_var, tuple):
                self.iterate_register_to_number_array(0, assign_to_var)
            else:
                self.iterate_register_to_number(0, self.memory[assign_to_var])
            self.iterate_register_to_number(1, result)
            self.add_line_of_code("STORE 1")

        else:
            self.move_value_from_memory_to_register(var0)
            if isinstance(var1, tuple):
                self.iterate_register_to_number_array(0, var1)
            else:
                self.iterate_register_to_number(0, self.memory[var1])
            self.add_line_of_code("ADD " + str(self.variables_with_registers[var0]))
            self.copy_value_from_register_to_memory(self.variables_with_registers[var0], assign_to_var)

    def assign_minus(self, assign):
        assign_to_var = assign[1]
        var0 = assign[2][1]
        var1 = assign[2][2]

        if isinstance(var0, long) and isinstance(var1, long):
            result = var0 - var1
            if isinstance(assign_to_var, tuple):
                self.iterate_register_to_number_array(0, assign_to_var)
            else:
                self.iterate_register_to_number(0, self.memory[assign_to_var])
            self.iterate_register_to_number(1, result)
            self.add_line_of_code("STORE 1")

        else:
            self.move_value_from_memory_to_register(var0)
            if isinstance(var1, tuple):
                self.iterate_register_to_number_array(0, var1)
            else:
                self.iterate_register_to_number(0, self.memory[var1])
            self.add_line_of_code("SUB " + str(self.variables_with_registers[var0]))
            self.copy_value_from_register_to_memory(self.variables_with_registers[var0], assign_to_var)

    def registers_full(self):
        for i in range(1, len(self.registers)):
            if self.registers[i] is None:
                return False
        return True


