from memory import Memory


class Compiler:
    def __init__(self, procedures, main_prog, tokens):
        self.tokens = tokens
        self.procedures = procedures
        self.main_prog = main_prog
        self.commands = main_prog.commands
        self.memory = Memory()
        self.check_semantic_errors()
        self.prepare_memory()
        self.memory.set_program_variable("Pj")
        self.memory.set_program_variable("Pi")
        self.memory.set_program_variable("Pk")
        self.assembly = []
        self.compile_procedures()
        self.compile_main()

    def check_semantic_errors(self):

        procedures = []
        for i in range(len(self.tokens)):
            if self.tokens[i].type == 'PROCEDURE':
                current_proc_usable_vars = []
                procedure = []
                i += 1
                proc = [self.tokens[i].value, self.tokens[i]]
                procedure.append(proc)
                i += 1
                proc_all_args = []
                proc_all_decs = []
                proc_all_used_vars = []
                proc_all_set_vars = []
                if self.tokens[i].type == '(':
                    proc_args = []
                    i += 1
                    while self.tokens[i].type != ')':
                        if self.tokens[i].type == 'IDENTIFIER':
                            if self.tokens[i].value in current_proc_usable_vars:
                                raise Exception(f"Powtorzenie deklaracji zmiennej {self.tokens[i].value}"
                                                f" w sygnaturze funkcji {proc[0]}"
                                                f" | line: {self.tokens[i].lineno}")
                            current_proc_usable_vars.append(self.tokens[i].value)
                            proc_args.append(self.tokens[i].value)
                            proc_args.append(self.tokens[i])
                            proc_all_args.append(proc_args)
                            proc_all_set_vars.append(self.tokens[i].value)
                            proc_args = []
                        i += 1
                i += 2

                if self.tokens[i].type == 'VAR':
                    proc_decs = []
                    i += 1
                    while self.tokens[i].type != 'BEGIN':
                        if self.tokens[i].type == 'IDENTIFIER':
                            if self.tokens[i].value in current_proc_usable_vars:
                                raise Exception(f"Powtorzenie zmiennej {self.tokens[i].value}"
                                                f" w deklaracji zmiennych funkcji {proc[0]}"
                                                f" | line: {self.tokens[i].lineno}")
                            current_proc_usable_vars.append(self.tokens[i].value)
                            proc_decs.append(self.tokens[i].value)
                            proc_decs.append(self.tokens[i])
                            proc_all_decs.append(proc_decs)
                            proc_decs = []
                        i += 1
                procedure.append(proc_all_args)
                procedure.append(proc_all_decs)

                procedures.append(procedure)
                if self.tokens[i].type == 'BEGIN':
                    i += 1
                    while self.tokens[i].type != 'END':
                        if self.tokens[i].type == 'IDENTIFIER':
                            if self.tokens[i - 1].type == 'READ':
                                if self.tokens[i].value not in current_proc_usable_vars:
                                    # print(self.tokens[i].value)
                                    raise Exception(f"Nie można sczytać wartości zmiennej {self.tokens[i].value}"
                                                    f" ponieważ zmienna nie jest zadeklarowana")
                            elif self.tokens[i - 1].type == 'WRITE':
                                # print(proc_all_set_vars)
                                if self.tokens[i].value not in proc_all_set_vars:
                                    raise Exception(f"Zmienna {self.tokens[i].value} nie została zainicjalizowana"
                                                    f" | line : {self.tokens[i].lineno}")
                            if self.tokens[i + 1].type == '(':
                                proc_name_call = self.tokens[i].value
                                proc_is_declared = False
                                proc_call_index = None
                                for obj in range(len(procedures) - 1):
                                    if procedures[obj][0][0] == proc_name_call:
                                        proc_is_declared = True
                                        proc_call_index = obj
                                        break
                                if not proc_is_declared:
                                    raise Exception(f"Procedura {proc_name_call} nie została zainicjalizowana"
                                                    f" | line : {self.tokens[i].lineno}")
                                i += 2
                                proc_call_vars_amount = 0
                                while self.tokens[i].type != ')':
                                    if self.tokens[i].type == 'IDENTIFIER':
                                        proc_all_used_vars.append(self.tokens[i])
                                        proc_all_set_vars.append(self.tokens[i].value)
                                        if self.tokens[i].value in current_proc_usable_vars:
                                            proc_call_vars_amount += 1
                                        else:
                                            raise Exception(f"Nie ma zmiennej {self.tokens[i].value}"
                                                            f" w scopie procedury {procedure[0][0]} "
                                                            f"| line: {self.tokens[i].lineno}")
                                    i += 1
                                if proc_call_vars_amount != len(procedures[proc_call_index][1]):
                                    raise Exception(f"Zła ilość argumentów podanych w wywołaniu procedury "
                                                    f"{procedures[proc_call_index][0][0]} "
                                                    f"| line : {self.tokens[i].lineno}")
                            else:


                                if self.tokens[i+1].type == 'ASSIGN':
                                    proc_all_set_vars.append(self.tokens[i].value)
                                proc_all_used_vars.append(self.tokens[i])
                                if self.tokens[i].value not in current_proc_usable_vars:
                                    raise Exception(f"Nie ma zmiennej {self.tokens[i].value}"
                                                    f" w scopie procedury {procedure[0][0]} "
                                                    f"| line: {self.tokens[i].lineno}")

                        i += 1

                    # print(proc_all_set_vars)
                    # print(proc_all_used_vars)
                    for used in proc_all_used_vars:
                        if used.value not in proc_all_set_vars:
                            raise Exception(f"Użycie nie zainicjalizowanej zmiennej {used.value} "
                                            f"| line : {used.lineno}")

            if self.tokens[i].type == 'PROGRAM':
                procedure = []
                current_proc_usable_vars = []
                proc = ['PROGRAM', self.tokens[i]]
                procedure.append(proc)
                i += 2
                proc_all_decs = []
                proc_decs = []
                proc_all_set_vars = []
                proc_all_used_vars = []
                if self.tokens[i].value == 'VAR':
                    main_decs = []
                    i += 1
                    while self.tokens[i].type != 'BEGIN':
                        if self.tokens[i].type == 'IDENTIFIER':
                            if self.tokens[i].value in current_proc_usable_vars:
                                raise Exception(f"Powtorzenie zmiennej {self.tokens[i].value}"
                                                f" w programie"
                                                f" | line: {self.tokens[i].lineno}")
                            current_proc_usable_vars.append(self.tokens[i].value)
                            main_decs.append(self.tokens[i].value)
                            proc_decs.append(self.tokens[i])
                            proc_all_decs.append(proc_decs)
                            proc_decs = []
                        i += 1
                procedure.append([])
                procedure.append(proc_all_decs)
                procedures.append(procedure)
                if self.tokens[i].type == 'BEGIN':
                    i += 1
                    while self.tokens[i].type != 'END':
                        if self.tokens[i].type == 'IDENTIFIER':
                            if self.tokens[i - 1].type == 'READ':
                                if self.tokens[i].value not in current_proc_usable_vars:
                                    raise Exception(f"Nie można sczytać wartości zmiennej {self.tokens[i].value}"
                                                    f" ponieważ zmienna nie jest zadeklarowana")
                                proc_all_set_vars.append(self.tokens[i].value)
                            elif self.tokens[i - 1].type == 'WRITE':
                                # print(proc_all_set_vars)
                                if self.tokens[i].value not in proc_all_set_vars:
                                    raise Exception(f"Zmienna {self.tokens[i].value} nie została zainicjalizowana"
                                                    f" | line : {self.tokens[i].lineno}")
                            if self.tokens[i + 1].type == '(':
                                proc_name_call = self.tokens[i].value
                                proc_is_declared = False
                                proc_call_index = None
                                for obj in range(len(procedures) - 1):
                                    if procedures[obj][0][0] == proc_name_call:
                                        proc_is_declared = True
                                        proc_call_index = obj
                                        break
                                if not proc_is_declared:
                                    raise Exception(f"Procedura {proc_name_call} nie została zainicjalizowana"
                                                    f" | line : {self.tokens[i].lineno}")
                                i += 2
                                proc_call_vars_amount = 0
                                while self.tokens[i].type != ')':
                                    if self.tokens[i].type == 'IDENTIFIER':
                                        proc_all_used_vars.append(self.tokens[i])
                                        proc_all_set_vars.append(self.tokens[i].value)
                                        if self.tokens[i].value in current_proc_usable_vars:
                                            proc_call_vars_amount += 1
                                        else:
                                            raise Exception(f"Nie ma zmiennej {self.tokens[i].value}"
                                                            f" w scopie procedury {procedure[0][0]} "
                                                            f"| line: {self.tokens[i].lineno}")
                                    i += 1
                                if proc_call_vars_amount != len(procedures[proc_call_index][1]):
                                    raise Exception(f"Zła ilość argumentów podanych w wywołaniu procedury "
                                                    f"{procedures[proc_call_index][0][0]} "
                                                    f"| line : {self.tokens[i].lineno}")
                            else:
                                if self.tokens[i+1].type == 'ASSIGN':
                                    proc_all_set_vars.append(self.tokens[i].value)
                                proc_all_used_vars.append(self.tokens[i])
                                if self.tokens[i].value not in current_proc_usable_vars:
                                    raise Exception(f"Nie ma zmiennej {self.tokens[i].value}"
                                                    f" w scopie procedury {procedure[0][0]} "
                                                    f"| line: {self.tokens[i].lineno}")
                        i += 1
                    for used in proc_all_used_vars:
                        if used.value not in proc_all_set_vars:
                            raise Exception(f"Użycie nie zainicjalizowanej zmiennej {used.value} "
                                            f"| line : {used.lineno}")

    def prepare_memory(self):
        for procedure in self.procedures:
            proc_name = procedure.proc_head[0]
            self.memory.set_procedure(proc_name)
            for arg in procedure.proc_head[1]:
                self.memory.set_procedure_variable_argument(arg, proc_name)
            if procedure.declarations is not None:
                for arg in procedure.declarations:
                    self.memory.set_procedure_variable_internal(arg, proc_name)
            self.memory.set_procedure_starting_line_index(proc_name)
            self.memory.set_procedure_recall_line(proc_name)
        for dec in self.main_prog.declarations:
            self.memory.set_program_variable(dec)

    def compile_procedures(self):
        for procedure in self.procedures:
            self.assembly.append(f"SET {len(self.assembly) + 3}")
            start_index = self.memory.get_procedure_starting_line_index(procedure.proc_head[0])
            self.assembly.append(f"STORE {start_index}")
            j_index = len(self.assembly)
            self.assembly.append(f"JUMP ProcFinish [proc_finish]")
            self.generate_assembly(procedure.commands, procedure.proc_head[0])
            recall_index = self.memory.get_procedure_recall_line(procedure.proc_head[0])
            self.assembly.append(f"JUMPI {recall_index}")
            self.assembly[j_index] = self.assembly[j_index].replace('ProcFinish',
                                                                    str(len(self.assembly)))

    def compile_main(self):
        # self.assembly[0] = f"JUMP {len(self.assembly)}"
        self.generate_assembly(self.commands, "Main")
        self.assembly.append("HALT")
        return self.assembly

    def generate_assembly(self, commands, proc_name):
        for command in commands:
            if command[0] == "assign":
                target = command[1]
                expression = command[2]
                self.calculate_expression(expression, proc_name)

                if proc_name == "Main":
                    index = self.memory.get_variable_memory_index(target, proc_name)
                    self.assembly.append(f"STORE {index}")
                else:
                    var_name = self.memory.get_variable_memory_index(target, proc_name)
                    index = self.memory[var_name]
                    # print(f"VAR NAME: {var_name}")
                    if var_name.startswith("Int_"):
                        self.assembly.append(f"STORE {index}")
                    elif var_name.startswith("Arg_"):
                        self.assembly.append(f"STOREI {index}")
                    else:
                        raise Exception(f"Assign sie wysypalo")
            elif command[0] == "if_else":
                condition_start = len(self.assembly)
                self.check_condition(command[1], proc_name)
                if_start = len(self.assembly)
                self.generate_assembly(command[2], proc_name)
                self.assembly.append(f"JUMP Finish")
                else_start = len(self.assembly)
                self.generate_assembly(command[3], proc_name)
                command_end = len(self.assembly)
                self.assembly[else_start - 1] = self.assembly[else_start - 1].replace('Finish',
                                                                                      str(command_end))
                for i in range(condition_start, if_start):
                    self.assembly[i] = self.assembly[i].replace('Finish', str(else_start))
            elif command[0] == "if":
                condition_start = len(self.assembly)
                self.check_condition(command[1], proc_name)
                command_start = len(self.assembly)
                self.generate_assembly(command[2], proc_name)
                command_end = len(self.assembly)
                for i in range(condition_start, command_start):
                    self.assembly[i] = self.assembly[i].replace('Finish', str(command_end))
            elif command[0] == "while":
                condition_start = len(self.assembly)
                self.check_condition(command[1], proc_name)
                loop_start = len(self.assembly)
                self.generate_assembly(command[2], proc_name)
                self.assembly.append(f"JUMP {condition_start}")
                loop_end = len(self.assembly)
                for i in range(condition_start, loop_start):
                    self.assembly[i] = self.assembly[i].replace('Finish', str(loop_end))
            elif command[0] == "repeat":
                loop_start = len(self.assembly)
                self.generate_assembly(command[2], proc_name)
                condition_start = len(self.assembly)
                self.check_condition(command[1], proc_name)
                condition_end = len(self.assembly)
                for i in range(condition_start, condition_end):
                    self.assembly[i] = self.assembly[i].replace('Finish', str(loop_start))
            elif command[0] == "read":
                if proc_name == "Main":
                    index = self.memory.get_variable_memory_index(command[1], proc_name)
                    self.assembly.append(f"GET {index}")
                else:
                    var_name = self.memory.get_variable_memory_index(command[1], proc_name)
                    index = self.memory[var_name]
                    if var_name.startswith("Int_"):
                        self.assembly.append(f"GET {index}")
                    elif var_name.startswith("Arg_"):
                        self.assembly.append(f"GETI {index}")
                    else:
                        raise Exception(f"Read sie wysypalo")
            elif command[0] == "write":
                if command[1][0] == "const":
                    num = int(command[1][1])
                    self.assembly.append(f"SET {num}")
                    self.assembly.append(f"PUT 0")
                else:
                    if proc_name == "Main":
                        index = self.memory.get_variable_memory_index(command[1][1], proc_name)
                        self.assembly.append(f"PUT {index}")
                    else:
                        var_name = self.memory.get_variable_memory_index(command[1][1], proc_name)
                        index = self.memory[var_name]
                        if var_name.startswith("Int_"):
                            self.assembly.append(f"PUT {index}")
                        elif var_name.startswith("Arg_"):
                            self.assembly.append(f"PUTI {index}")
                        else:
                            raise Exception(f"Write sie wysypalo")
            elif command[0] in self.memory.procedures:
                if command[0] == proc_name:
                    raise Exception(f"Wywołanie rekurencyjne procedury {proc_name} SEM ERR")
                if proc_name == "Main":
                    proc_arg_indexes = []
                    proc_call_indexes = []
                    for proc_arg in self.memory:
                        if proc_arg.startswith(f"Arg_{command[0]}_"):
                            proc_arg_indexes.append(self.memory[proc_arg])
                    for arg in command[1]:
                        proc_call_indexes.append(self.memory[arg])
                    if len(proc_arg_indexes) != len(proc_call_indexes):
                        raise Exception(f"Zła ilość argumentów w wywołaniu funkcji {command[1]} SEM ERR")
                    for i in range(len(proc_call_indexes)):
                        self.assembly.append(f"SET {int(proc_call_indexes[i])}")
                        self.assembly.append(f"STORE {int(proc_arg_indexes[i])}")
                    rec_line = len(self.assembly) + 3
                    recall_index = self.memory.get_procedure_recall_line(command[0])
                    proc_starting_line_index = self.memory.get_procedure_starting_line_index(command[0])
                    self.assembly.append(f"SET {rec_line}")
                    self.assembly.append(f"STORE {recall_index}")
                    self.assembly.append(f"JUMPI {proc_starting_line_index}")
                else:
                    proc_arg_indexes = []
                    proc_call_indexes = []
                    proc_call_names = []
                    for proc_arg in self.memory:
                        if proc_arg.startswith(f"Arg_{command[0]}_"):
                            proc_arg_indexes.append(self.memory[proc_arg])

                    for arg in command[1]:
                        if f"Int_{proc_name}_{arg}" in self.memory:
                            proc_call_indexes.append(self.memory[f"Int_{proc_name}_{arg}"])
                            proc_call_names.append(f"Int_{proc_name}_{arg}")
                        elif f"Arg_{proc_name}_{arg}" in self.memory:
                            proc_call_indexes.append(self.memory[f"Arg_{proc_name}_{arg}"])
                            proc_call_names.append(f"Arg_{proc_name}_{arg}")
                        else:
                            raise Exception(f"nie wiem SEM ERR?")
                    if len(proc_arg_indexes) != len(proc_call_indexes):
                        raise Exception(f"Zła ilość argumentów w wywołaniu funkcji {command[1]} SEM ERR")
                    for i in range(len(proc_call_indexes)):
                        if f"Arg_{proc_name}_" in proc_call_names[i]:
                            self.assembly.append(f"LOAD {int(proc_call_indexes[i])}")
                        else:
                            self.assembly.append(f"SET {int(proc_call_indexes[i])}")
                        self.assembly.append(f"STORE {int(proc_arg_indexes[i])}")
                    rec_line = len(self.assembly) + 3
                    recall_index = self.memory.get_procedure_recall_line(command[0])
                    proc_starting_line_index = self.memory.get_procedure_starting_line_index(command[0])
                    self.assembly.append(f"SET {rec_line}")
                    self.assembly.append(f"STORE {recall_index}")
                    self.assembly.append(f"JUMPI {proc_starting_line_index}")
            else:
                raise Exception(f"Procedura {command[0]} nie została zainincjalizowana SEM ERR")

    def calculate_expression(self, expression, proc_name):
        if proc_name == "Main":
            if expression[0] == "const":
                self.assembly.append(f"SET {expression[1]}")
            elif expression[0] == "load":
                index = self.memory.get_variable_memory_index(expression[1], proc_name)
                self.assembly.append(f"LOAD {index}")
            else:
                if expression[1][0] == "const" and expression[2][0] == "load":
                    cons = int(expression[1][1])
                    index = self.memory.get_variable_memory_index(expression[2][1], proc_name)
                    self.assembly.append(f"SET {cons}")
                    self.assembly.append(f"STORE 1")
                    self.assembly.append(f"LOAD {index}")
                    self.assembly.append(f"STORE 2")
                elif expression[1][0] == "load" and expression[2][0] == "const":
                    index = self.memory.get_variable_memory_index(expression[1][1], proc_name)
                    cons = int(expression[2][1])
                    self.assembly.append(f"LOAD {index}")
                    self.assembly.append(f"STORE 1")
                    self.assembly.append(f"SET {cons}")
                    self.assembly.append(f"STORE 2")
                elif expression[1][0] == "const" and expression[2][0] == "const":
                    cons1 = int(expression[1][1])
                    cons2 = int(expression[2][1])
                    self.assembly.append(f"SET {cons1}")
                    self.assembly.append(f"STORE 1")
                    self.assembly.append(f"SET {cons2}")
                    self.assembly.append(f"STORE 2")
                else:
                    index1 = self.memory.get_variable_memory_index(expression[1][1], proc_name)
                    index2 = self.memory.get_variable_memory_index(expression[2][1], proc_name)
                    self.assembly.append(f"LOAD {index1}")
                    self.assembly.append(f"STORE 1")
                    self.assembly.append(f"LOAD {index2}")
                    self.assembly.append(f"STORE 2")
                if expression[0] == "plus":
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"ADD 2")
                elif expression[0] == "minus":
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"SUB 2")
                elif expression[0] == "times":
                    index_const_1 = self.memory["Pj"]
                    index_helper = self.memory["Pi"]
                    index_2n_val = self.memory["Pk"]
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {index_const_1}")
                    self.assembly.append(f"SET 0 [TIMES]")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"JZERO {len(self.assembly) + 117}")
                    self.assembly.append(f"SUB {index_const_1}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 108}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"JZERO {len(self.assembly) + 113}")
                    self.assembly.append(f"SUB {index_const_1}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 108}")
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"STORE 5")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"JZERO {len(self.assembly) + 19}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"SUB {index_helper}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 5")
                    self.assembly.append(f"ADD {index_2n_val}")
                    self.assembly.append(f"STORE 5")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"ADD {index_const_1}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"STORE 1")
                    self.assembly.append(f"JUMP {len(self.assembly) - 20}")
                    self.assembly.append(f"SET 1")  # X zostało rozłożone na 2^n + rx
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"STORE 6")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"JZERO {len(self.assembly) + 19}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"SUB {index_helper}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 6")
                    self.assembly.append(f"ADD {index_2n_val}")
                    self.assembly.append(f"STORE 6")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"ADD {index_const_1}")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"STORE 2")
                    self.assembly.append(f"JUMP {len(self.assembly) - 20}")
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"ADD 4")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 8}")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD {index_helper}")
                    self.assembly.append(f"SUB {index_const_1}")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"JUMP {len(self.assembly) - 7}")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")  # Obliczone 2^(n+m) i dodane do sumy
                    self.assembly.append(f"LOAD 6")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 8}")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD {index_helper}")
                    self.assembly.append(f"SUB {index_const_1}")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"JUMP {len(self.assembly) - 7}")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")  # Obliczone 2^n * ry
                    self.assembly.append(f"LOAD 5")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 8}")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD {index_helper}")
                    self.assembly.append(f"SUB {index_const_1}")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"JUMP {len(self.assembly) - 7}")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")  # Obliczone 2^m * rx
                    self.assembly.append(f"LOAD 5")
                    self.assembly.append(f"STORE 1")
                    self.assembly.append(f"LOAD 6")
                    self.assembly.append(f"STORE 2")
                    self.assembly.append(f"JUMP {len(self.assembly) - 110}")  # Rekursja
                    self.assembly.append(f"LOAD 2")  # END dla x = 1
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"JUMP {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 1")  # END dla y = 1
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"LOAD 7")  # END
                elif expression[0] == "div":
                    pj = self.memory["Pj"]
                    pi = self.memory["Pi"]
                    pk = self.memory["Pk"]
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {pj}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"JZERO {len(self.assembly) + 74}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"JZERO {len(self.assembly) + 72}")
                    self.assembly.append(f"SUB {pj}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 74}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"SUB 1")
                    self.assembly.append(f"JPOS {len(self.assembly) + 62}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"SUB 2")
                    self.assembly.append(f"JZERO {len(self.assembly) + 73}")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {pk}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"STORE 5")
                    self.assembly.append(f"LOAD 5")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"JZERO {len(self.assembly) + 9}")
                    self.assembly.append(f"STORE 5")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"ADD {pj}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {pk}")
                    self.assembly.append(f"JUMP {len(self.assembly) - 10}")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"ADD {pj}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"STORE {pi}")
                    self.assembly.append(f"LOAD {pi}")
                    self.assembly.append(f"SUB {pk}")
                    self.assembly.append(f"JPOS {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"SUB {pi}")
                    self.assembly.append(f"JPOS {len(self.assembly) + 7}")
                    self.assembly.append(f"STORE {pi}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"ADD {pj}")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"JUMP {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SUB 2")
                    self.assembly.append(f"JPOS {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"SUB 4")
                    self.assembly.append(f"JPOS {len(self.assembly) + 7}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"SUB 2")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"STORE {pk}")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"SUB {pj}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 21}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"JUMP {len(self.assembly) - 33}")
                    self.assembly.append(f"LOAD 1")  # x<y
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"JUMP {len(self.assembly) + 14}")
                    self.assembly.append(f"SET 0")  # JUMP_ZERO
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"JUMP {len(self.assembly) + 10}")
                    self.assembly.append(f"LOAD 1")  # JUMP y=1
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"JUMP {len(self.assembly) + 5}")
                    self.assembly.append(f"SET 0")  # x=y
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"LOAD 7")  # KONIEC
                elif expression[0] == "mod":
                    pj = self.memory["Pj"]
                    pi = self.memory["Pi"]
                    pk = self.memory["Pk"]
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {pj}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"JZERO {len(self.assembly) + 74}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"JZERO {len(self.assembly) + 72}")
                    self.assembly.append(f"SUB {pj}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 74}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"SUB 1")
                    self.assembly.append(f"JPOS {len(self.assembly) + 62}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"SUB 2")
                    self.assembly.append(f"JZERO {len(self.assembly) + 73}")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {pk}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"STORE 5")
                    self.assembly.append(f"LOAD 5")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"JZERO {len(self.assembly) + 9}")
                    self.assembly.append(f"STORE 5")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"ADD {pj}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {pk}")
                    self.assembly.append(f"JUMP {len(self.assembly) - 10}")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"ADD {pj}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"STORE {pi}")
                    self.assembly.append(f"LOAD {pi}")
                    self.assembly.append(f"SUB {pk}")
                    self.assembly.append(f"JPOS {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"SUB {pi}")
                    self.assembly.append(f"JPOS {len(self.assembly) + 7}")
                    self.assembly.append(f"STORE {pi}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"ADD {pj}")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"JUMP {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SUB 2")
                    self.assembly.append(f"JPOS {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"SUB 4")
                    self.assembly.append(f"JPOS {len(self.assembly) + 7}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"SUB 2")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"STORE {pk}")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"SUB {pj}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 21}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"JUMP {len(self.assembly) - 33}")
                    self.assembly.append(f"LOAD 1")  # x<y
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"JUMP {len(self.assembly) + 14}")
                    self.assembly.append(f"SET 0")  # JUMP_ZERO
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"JUMP {len(self.assembly) + 10}")
                    self.assembly.append(f"LOAD 1")  # JUMP y=1
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"JUMP {len(self.assembly) + 5}")
                    self.assembly.append(f"SET 0")  # x=y
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"LOAD 4")  # KONIEC

        else:
            if expression[0] == "const":
                self.assembly.append(f"SET {expression[1]}")
            elif expression[0] == "load":
                var_name = self.memory.get_variable_memory_index(expression[1], proc_name)
                if var_name.startswith("Int_"):
                    index = self.memory[var_name]
                    self.assembly.append(f"LOAD {index}")
                elif var_name.startswith("Arg_"):
                    index = self.memory[var_name]
                    self.assembly.append(f"LOADI {index}")
                else:
                    raise Exception(f"LOAD sie wysypalo SEM ERR")
            else:
                if expression[1][0] == "const" and expression[2][0] == "load":
                    cons = int(expression[1][1])
                    self.assembly.append(f"SET {cons}")
                    self.assembly.append(f"STORE 1")
                    var_name = self.memory.get_variable_memory_index(expression[2][1], proc_name)
                    if var_name.startswith("Int_"):
                        index = self.memory[var_name]
                        self.assembly.append(f"LOAD {index}")
                    elif var_name.startswith("Arg_"):
                        index = self.memory[var_name]
                        self.assembly.append(f"LOADI {index}")
                    else:
                        raise Exception(f"LOAD 2 SEM ERR")
                    self.assembly.append(f"STORE 2")
                elif expression[1][0] == "load" and expression[2][0] == "const":
                    cons = int(expression[2][1])
                    self.assembly.append(f"SET {cons}")
                    self.assembly.append(f"STORE 2")
                    var_name = self.memory.get_variable_memory_index(expression[1][1], proc_name)
                    if var_name.startswith("Int_"):
                        index = self.memory[var_name]
                        self.assembly.append(f"LOAD {index}")
                    elif var_name.startswith("Arg_"):
                        index = self.memory[var_name]
                        self.assembly.append(f"LOADI {index}")
                    else:
                        raise Exception(f"LOAD 3 SEM ERR")
                    self.assembly.append(f"STORE 1")
                elif expression[1][0] == "const" and expression[2][0] == "const":
                    cons1 = int(expression[1][1])
                    cons2 = int(expression[2][1])
                    self.assembly.append(f"SET {cons1}")
                    self.assembly.append(f"STORE 1")
                    self.assembly.append(f"SET {cons2}")
                    self.assembly.append(f"STORE 2")
                else:
                    var_name1 = self.memory.get_variable_memory_index(expression[1][1], proc_name)
                    var_name2 = self.memory.get_variable_memory_index(expression[2][1], proc_name)
                    if var_name1.startswith("Int_"):
                        index = self.memory[var_name1]
                        self.assembly.append(f"LOAD {index}")
                    elif var_name1.startswith("Arg_"):
                        index = self.memory[var_name1]
                        self.assembly.append(f"LOADI {index}")
                    else:
                        raise Exception(f"LOAD 4 SEM ERR")
                    self.assembly.append(f"STORE 1")
                    if var_name2.startswith("Int_"):
                        index = self.memory[var_name2]
                        self.assembly.append(f"LOAD {index}")
                    elif var_name2.startswith("Arg_"):
                        index = self.memory[var_name2]
                        self.assembly.append(f"LOADI {index}")
                    else:
                        raise Exception(f"LOAD 5 SEM ERR")
                    self.assembly.append(f"STORE 2")
                if expression[0] == "plus":
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"ADD 2")
                elif expression[0] == "minus":
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"SUB 2")
                elif expression[0] == "times":
                    index_const_1 = self.memory["Pj"]
                    index_helper = self.memory["Pi"]
                    index_2n_val = self.memory["Pk"]
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {index_const_1}")
                    self.assembly.append(f"SET 0 [TIMES]")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"JZERO {len(self.assembly) + 117}")
                    self.assembly.append(f"SUB {index_const_1}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 108}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"JZERO {len(self.assembly) + 113}")
                    self.assembly.append(f"SUB {index_const_1}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 108}")
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"STORE 5")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"JZERO {len(self.assembly) + 19}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"SUB {index_helper}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 5")
                    self.assembly.append(f"ADD {index_2n_val}")
                    self.assembly.append(f"STORE 5")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"ADD {index_const_1}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"STORE 1")
                    self.assembly.append(f"JUMP {len(self.assembly) - 20}")
                    self.assembly.append(f"SET 1")  # X zostało rozłożone na 2^n + rx
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"STORE 6")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"JZERO {len(self.assembly) + 19}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"SUB {index_helper}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 6")
                    self.assembly.append(f"ADD {index_2n_val}")
                    self.assembly.append(f"STORE 6")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"ADD {index_const_1}")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"STORE 2")
                    self.assembly.append(f"JUMP {len(self.assembly) - 20}")
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"ADD 4")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 8}")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD {index_helper}")
                    self.assembly.append(f"SUB {index_const_1}")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"JUMP {len(self.assembly) - 7}")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")  # Obliczone 2^(n+m) i dodane do sumy
                    self.assembly.append(f"LOAD 6")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 8}")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD {index_helper}")
                    self.assembly.append(f"SUB {index_const_1}")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"JUMP {len(self.assembly) - 7}")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")  # Obliczone 2^n * ry
                    self.assembly.append(f"LOAD 5")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 8}")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {index_2n_val}")
                    self.assembly.append(f"LOAD {index_helper}")
                    self.assembly.append(f"SUB {index_const_1}")
                    self.assembly.append(f"STORE {index_helper}")
                    self.assembly.append(f"JUMP {len(self.assembly) - 7}")
                    self.assembly.append(f"LOAD {index_2n_val}")
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")  # Obliczone 2^m * rx
                    self.assembly.append(f"LOAD 5")
                    self.assembly.append(f"STORE 1")
                    self.assembly.append(f"LOAD 6")
                    self.assembly.append(f"STORE 2")
                    self.assembly.append(f"JUMP {len(self.assembly) - 110}")  # Rekursja
                    self.assembly.append(f"LOAD 2")  # END dla x = 1
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"JUMP {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 1")  # END dla y = 1
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"LOAD 7")  # END
                elif expression[0] == "div":
                    pj = self.memory["Pj"]
                    pi = self.memory["Pi"]
                    pk = self.memory["Pk"]
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {pj}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"JZERO {len(self.assembly) + 74}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"JZERO {len(self.assembly) + 72}")
                    self.assembly.append(f"SUB {pj}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 74}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"SUB 1")
                    self.assembly.append(f"JPOS {len(self.assembly) + 62}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"SUB 2")
                    self.assembly.append(f"JZERO {len(self.assembly) + 73}")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {pk}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"STORE 5")
                    self.assembly.append(f"LOAD 5")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"JZERO {len(self.assembly) + 9}")
                    self.assembly.append(f"STORE 5")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"ADD {pj}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {pk}")
                    self.assembly.append(f"JUMP {len(self.assembly) - 10}")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"ADD {pj}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"STORE {pi}")
                    self.assembly.append(f"LOAD {pi}")
                    self.assembly.append(f"SUB {pk}")
                    self.assembly.append(f"JPOS {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"SUB {pi}")
                    self.assembly.append(f"JPOS {len(self.assembly) + 7}")
                    self.assembly.append(f"STORE {pi}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"ADD {pj}")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"JUMP {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SUB 2")
                    self.assembly.append(f"JPOS {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"SUB 4")
                    self.assembly.append(f"JPOS {len(self.assembly) + 7}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"SUB 2")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"STORE {pk}")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"SUB {pj}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 21}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"JUMP {len(self.assembly) - 33}")
                    self.assembly.append(f"LOAD 1")  # x<y
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"JUMP {len(self.assembly) + 14}")
                    self.assembly.append(f"SET 0")  # JUMP_ZERO
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"JUMP {len(self.assembly) + 10}")
                    self.assembly.append(f"LOAD 1")  # JUMP y=1
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"JUMP {len(self.assembly) + 5}")
                    self.assembly.append(f"SET 0")  # x=y
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"LOAD 7")  # KONIEC
                elif expression[0] == "mod":
                    pj = self.memory["Pj"]
                    pi = self.memory["Pi"]
                    pk = self.memory["Pk"]
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {pj}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"JZERO {len(self.assembly) + 74}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"JZERO {len(self.assembly) + 72}")
                    self.assembly.append(f"SUB {pj}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 74}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"SUB 1")
                    self.assembly.append(f"JPOS {len(self.assembly) + 62}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"SUB 2")
                    self.assembly.append(f"JZERO {len(self.assembly) + 73}")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE {pk}")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"STORE 5")
                    self.assembly.append(f"LOAD 5")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"JZERO {len(self.assembly) + 9}")
                    self.assembly.append(f"STORE 5")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"ADD {pj}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE {pk}")
                    self.assembly.append(f"JUMP {len(self.assembly) - 10}")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"ADD {pj}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"LOAD 1")
                    self.assembly.append(f"STORE {pi}")
                    self.assembly.append(f"LOAD {pi}")
                    self.assembly.append(f"SUB {pk}")
                    self.assembly.append(f"JPOS {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"SUB {pi}")
                    self.assembly.append(f"JPOS {len(self.assembly) + 7}")
                    self.assembly.append(f"STORE {pi}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"ADD {pj}")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"JUMP {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"ADD 0")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SUB 2")
                    self.assembly.append(f"JPOS {len(self.assembly) + 4}")
                    self.assembly.append(f"LOAD 2")
                    self.assembly.append(f"SUB 4")
                    self.assembly.append(f"JPOS {len(self.assembly) + 7}")
                    self.assembly.append(f"LOAD 4")
                    self.assembly.append(f"SUB 2")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"ADD 7")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"LOAD {pk}")
                    self.assembly.append(f"HALF")
                    self.assembly.append(f"STORE {pk}")
                    self.assembly.append(f"LOAD 3")
                    self.assembly.append(f"SUB {pj}")
                    self.assembly.append(f"JZERO {len(self.assembly) + 21}")
                    self.assembly.append(f"STORE 3")
                    self.assembly.append(f"JUMP {len(self.assembly) - 33}")
                    self.assembly.append(f"LOAD 1")  # x<y
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"JUMP {len(self.assembly) + 14}")
                    self.assembly.append(f"SET 0")  # JUMP_ZERO
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"JUMP {len(self.assembly) + 10}")
                    self.assembly.append(f"LOAD 1")  # JUMP y=1
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"SET 0")
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"JUMP {len(self.assembly) + 5}")
                    self.assembly.append(f"SET 0")  # x=y
                    self.assembly.append(f"STORE 4")
                    self.assembly.append(f"SET 1")
                    self.assembly.append(f"STORE 7")
                    self.assembly.append(f"LOAD 4")  # KONIEC

    def check_condition(self, condition, proc_name):
        self.calculate_expression(condition[1], proc_name)
        self.assembly.append(f"STORE 1")
        self.calculate_expression(condition[2], proc_name)
        self.assembly.append(f"STORE 2")
        if condition[0] == "eq":
            self.assembly.append(f"LOAD 1 [EQ]")
            self.assembly.append(f"SUB 2")
            self.assembly.append(f"JZERO {len(self.assembly) + 2}")
            self.assembly.append(f"JUMP Finish")
            self.assembly.append(f"LOAD 2")
            self.assembly.append(f"SUB 1")
            self.assembly.append(f"JZERO {len(self.assembly) + 2}")
            self.assembly.append(f"JUMP Finish [JFINISH_COND]")
        elif condition[0] == "neq":
            self.assembly.append(f"LOAD 1 [NEQ]")
            self.assembly.append(f"SUB 2")
            self.assembly.append(f"JPOS {len(self.assembly) + 5}")
            self.assembly.append(f"LOAD 2")
            self.assembly.append(f"SUB 1")
            self.assembly.append(f"JPOS {len(self.assembly) + 2}")
            self.assembly.append(f"JUMP Finish [JFINISH_COND]")
        elif condition[0] == "ge":
            self.assembly.append(f"LOAD 1 [GE]")
            self.assembly.append(f"SUB 2")
            self.assembly.append(f"JPOS {len(self.assembly) + 2}")
            self.assembly.append(f"JUMP Finish [JFINISH_COND]")
        elif condition[0] == "le":
            self.assembly.append(f"LOAD 2 [LE]")
            self.assembly.append(f"SUB 1")
            self.assembly.append(f"JPOS {len(self.assembly) + 2}")
            self.assembly.append(f"JUMP Finish [JFINISH_COND]")
        elif condition[0] == "geq":
            self.assembly.append(f"LOAD 1 [GEQ]")
            self.assembly.append(f"SUB 2")
            self.assembly.append(f"JPOS {len(self.assembly) + 5}")
            self.assembly.append(f"LOAD 2")
            self.assembly.append(f"SUB 1")
            self.assembly.append(f"JZERO {len(self.assembly) + 2}")
            self.assembly.append(f"JUMP Finish [JFINISH_COND]")
        elif condition[0] == "leq":
            self.assembly.append(f"LOAD 2 [LEQ]")
            self.assembly.append(f"SUB 1")
            self.assembly.append(f"JPOS {len(self.assembly) + 5}")
            self.assembly.append(f"LOAD 1")
            self.assembly.append(f"SUB 2")
            self.assembly.append(f"JZERO {len(self.assembly) + 2}")
            self.assembly.append(f"JUMP Finish [JFINISH_COND]")
