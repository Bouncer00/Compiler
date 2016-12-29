from itertools import chain

class Analyzer:

    def __init__(self, parse_tree):
        self.parse_tree = parse_tree
        _, self.declarations, self.commands = self.parse_tree
        # self.declared_names = [declaration[1] for declaration in self.declarations]
        self.global_variables = []
        self.used_variables = []
        self.declared_variables = [declaration[1] for declaration in self.declarations]
        self.alread_inicialised = []

    def analyze(self):
        self.undeclared_variables(self.commands, self.declared_variables)
        self.redeclaration([])
        self.initialised_variables(self.commands)
        self.check_for_unincialised(self.commands)

    def undeclared_variables(self, commands, declared_variables):
        for command in commands:
            # if command[0] == "read" or command[0] == "write" or command[0] == "assign":
            print command
            if  isinstance(command, tuple):
                if isinstance(command[2], int) and command[1] not in self.declared_variables:
                    print "Variable", command[1], "in line", command[2], "not declared"
                self.undeclared_variables(command, declared_variables)
            # if isinstance(command, tuple) and len(command) != 3:
            #     if not command[0].__str__().startswith("for"):
            #         self.undeclared_variables(command, declared_variables)

                    # self.check_command(command)
            # if command[0] == "int" and command[1] not in already_declared:
            #     print "Variable", command[1], "in line", command[2], "not declared"
        # print(already_declared)

    def redeclaration(self, already_declared):
        for declaration in self.declarations:
            if declaration[1] in already_declared:
                print "Redeclaration of:", declaration[1], "in line", declaration[2]
            already_declared.append(declaration[1])

    def initialised_variables(self, commands):
        for command in commands:
            if isinstance(command, tuple) and (command[0] == "assign" or command[0] == "read"):
                self.alread_inicialised.append(command[1][1])
                print "Initialized", command
            if isinstance(command, tuple) and len(command) != 3:
                self.initialised_variables(command)

    def check_command(self, command):
        pass
        # print command
        # print command[1]
        # if len(command) > 3:
        #     print command[3]

    def check_for_unincialised(self, commands):
        for command in commands:
            if isinstance(command, tuple) and command[0] =="assign" and len(command) > 2:
                self.check_for_unincialised(command[1])
                self.check_for_unincialised(command[2])

            if self.is_variable(command) and command[1] not in self.alread_inicialised:
                print command[1], "in line", command[2], "not initialised"
                print command

            if isinstance(command, tuple) and len(command) != 3:
                if not command[0].__str__().startswith("for"):
                    self.check_for_unincialised(command)

    def is_variable(self, command):
        return isinstance(command, tuple) and len(command) == 3 and isinstance(command[2], int)

    # def check_assign(self, variables, error_str):

