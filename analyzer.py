class Analyzer:

    def __init__(self, parse_tree):
        self.parse_tree = parse_tree
        _, self.declarations, self.commands = self.parse_tree
        # self.declared_names = [declaration[1] for declaration in self.declarations]
        self.global_variables = []
        self.used_variables = []
        self.declared_variables = [declaration[1] for declaration in self.declarations]
        self.initialised_variables = []

    def analyze(self):
        self.undeclared_variables()
        self.redeclaration()
        self.initialised_variables(self.commands)

    def undeclared_variables(self):
        for command in self.commands:
            if command[0] == "read" or command[0] == "write":
                self.check_read_write(command)
            # self.check_command(command)
            # if command[0] == "int" and command[1] not in already_declared:
            #     print "Variable", command[1], "in line", command[2], "not declared"
        # print(already_declared)

    def redeclaration(self):
        already_declared = []
        for declaration in self.declarations:
            if declaration[1] in already_declared:
                print "Redeclaration of:", declaration[1], "in line", declaration[2]
            already_declared.append(declaration[1])

    def initialised_variables(self, commands):
        for command in commands:
            if command[0] == "assign" or command[0] == "read":
                self.initialised_variables.append(command[1][1])
                print command
            if isinstance(command, tuple) and len(command) != 3:
                self.initialised_variables(command)

    def check_command(self, command):
        print command
        print command[1]
        if len(command) > 3:
            print command[3]

    def check_read_write(self, command):
        if command[1][1] not in self.already_declared:
            print "Variable", command[1][1], "in line", command[1][2], "not declared"