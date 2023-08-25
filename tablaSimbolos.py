from prettytable import PrettyTable

class TablaSimbolos(object):
    def __init__(self):
        self.tabla = []
        self.simbolos = []
        self.stack = [0]
        self.c_scope = 0
        self.global_scope = 0

        self.function = False

    def in_function(self, function):
        self.function = function

    def enter_class(self):
        self.global_scope += 1
        self.stack[-1] += 1

    def enterScope(self, tipo_token=None):
        self.stack[-1] += 1

    def exitScope(self):
        if len(self.stack) > 1:
            self.stack.pop()

    def current_scope(self):
        if self.function:
            return self.stack[-1]
        else:
            return self.global_scope
    

    def get_simbolo(self, lexema):
        for simbolo in self.tabla:
            if simbolo.lexema == lexema:
                return simbolo
        return None

    def add_simbolo(self, simbolo):
        self.tabla.append(simbolo)
        texto_global = "Global" if simbolo.scope == self.global_scope else "Local"
        texto_global = "Clase" if simbolo.tipo_token == "CLASS" else texto_global
        simbolo.setGlobal(texto_global)
        

    def print_tabla(self):
        print("Tabla de simbolos:")
        x = PrettyTable()
        x.field_names = ["Lexema", "Linea", "Columna", "Tipo de Token", "Scope", "Global"]
        for simbolo in self.tabla:
            x.add_row([simbolo.lexema, simbolo.linea, simbolo.columna, simbolo.tipo_token, simbolo.scope, simbolo.global_])
        print(x)


class Simbolo:
    def __init__(self, lexema, linea, columna, tipo_token, scope):
        self.lexema = lexema
        self.linea = linea
        self.columna = columna
        self.tipo_token = tipo_token
        self.scope = scope
        self.global_ = False

    def __str__(self):
        return f"Lexema: {self.lexema}, Linea: {self.linea}, Columna: {self.columna}, Tipo de Token: {self.tipo_token}, Scope: {self.scope}"

    def setGlobal(self, global_):
        self.global_ = global_
