class MemoryCell:
    def __init__(self, memory_offset):
        self.memory_offset = memory_offset


class Memory(dict):
    def __init__(self):
        super().__init__()
        self.memory_offset = 8
        self.procedures = []

    def set_program_variable(self, identifier):
        if identifier in self:
            raise Exception(f"Redeklaracja {identifier}")
        self[identifier] = self.memory_offset
        self.memory_offset += 1

    def set_procedure_variable_argument(self, identifier, proc_name):
        new_arg = "Arg_" + proc_name + "_" + identifier
        if new_arg in self:
            raise Exception(f"Redeklaracja parametru formalnego procedury {proc_name} : {identifier}")
        self[new_arg] = self.memory_offset
        self.memory_offset += 1

    def set_procedure_variable_internal(self, identifier, proc_name):
        new_arg = "Int_" + proc_name + "_" + identifier
        if new_arg in self:
            raise Exception(f"Redeklaracja argumentu wewnętrznego procedury {proc_name} : {identifier}")
        self[new_arg] = self.memory_offset
        self.memory_offset += 1

    def set_procedure(self, proc_name):
        if proc_name in self.procedures:
            raise Exception(f"Redeklaracja procedury o nazwie {proc_name}")
        self.procedures.append(proc_name)

    def set_procedure_starting_line_index(self, proc_name):
        new_arg = f"Start_{proc_name}"
        for arg in self:
            if arg.startswith(f"Start_{proc_name}"):
                raise Exception(f"Start line dla procedury {proc_name} jest juz zapisany")
        self[new_arg] = self.memory_offset
        self.memory_offset += 1

    def set_procedure_recall_line(self, proc_name):
        new_arg = f"Recall_{proc_name}"
        if new_arg in self:
            raise Exception(f"Recall line dla procedury {proc_name} jest juz zapisany")
        self[new_arg] = self.memory_offset
        self.memory_offset += 1

    def procedure_is_declared(self, proc_name):
        if proc_name in self.procedures:
            return True
        else:
            return False

    def get_program_variable_mem_index(self, identifier):
        if identifier in self:
            # print(self[identifier])
            return self[identifier]
        else:
            raise Exception(f"Zmienna {identifier} nie zostala zadeklarowana")

    def get_procedure_variable_argument(self, identifier, proc_name):
        new_arg = "Arg_" + proc_name + "_" + identifier
        if new_arg in self and self.procedure_is_declared(proc_name):
            return self[new_arg]
        else:
            raise Exception(f"Argument formalny {identifier} funkcji {proc_name} nie zostal zadeklarowany")

    def get_procedure_variable_internal(self, identifier, proc_name):
        new_arg = "Int_" + proc_name + "_" + identifier
        if new_arg in self and self.procedure_is_declared(proc_name):
            return self[new_arg]
        else:
            raise Exception(f"Zmienna wewnetrzna {identifier} funkcji {proc_name} nie zostala zadeklarowana")

    def get_variable_memory_index(self, identifier, proc_name):
        # print(f"IDENT: {identifier}")
        if proc_name != "Main" and self.procedure_is_declared(proc_name):
            ids = []
            for variables in self:
                # print(f"VAR: {variables}")
                if variables.endswith(f"_{proc_name}_{identifier}"):
                    ids.append(variables)
            if len(ids) == 0:
                raise Exception(f"Zmienna {identifier} procedury {proc_name} nie istnieje")
            elif len(ids) == 1:
                return ids[0]
            else:
                raise Exception(f"Kilka deklaracji zmiennej {identifier} w procedurze {proc_name}")
        elif proc_name == "Main":
            return self.get_program_variable_mem_index(identifier)
        else:
            raise Exception(f"Procedura {proc_name} nie jest zainicjalizowana")

    def get_procedures(self):
        return self.procedures

    def get_procedure_starting_line_index(self, proc_name):
        for arg in self:
            if arg.startswith(f"Start_{proc_name}"):
                return self[arg]
        raise Exception(f"Starting line funkcji {proc_name} nie zostal zadeklarowany")

    def get_procedure_recall_line(self, proc_name):
        for arg in self:
            if arg.startswith(f"Recall_{proc_name}"):
                return self[arg]
        raise Exception(f"Recall line funkcji {proc_name} nie zostal zadeklarowany")