class TablaSimbolos(object):
    def __init__(self):
        self.tabla = []
        self.simbolos = []
        self.scope_stack = []
        self.scope = 0

        # cada simbolo debe tener:
        # lexema
        # linea
        # columna
        # token
        # alcance

    def enter_scope(self, scope_name):
        self.scope_stack.append(scope_name)
        self.scope += 1
        return self.scope   

    def exit_scope(self):
        self.scope_stack.pop()
        self.scope -= 1

    def get_simbolo(self, lexema):
        for simbolo in self.tabla:
            if simbolo.lexema == lexema:
                return simbolo
        return None

    def add_simbolo(self, simbolo):
        
        self.tabla.append(simbolo)
        

    # def actualizar_simbolo(self):
    #             return

    def print_tabla(self):
        print("\nTabla de simbolos:")
        # print(self.tabla)
        # print(self.simbolos)
        # print(self.scope_stack)
        # print(self.scope)
        for simbolo in self.tabla:
            print(simbolo)
        print("")

class Simbolo:
    def __init__(self, lexema, linea, columna, tipo_token, scope):
        self.lexema = lexema
        self.linea = linea
        self.columna = columna
        self.tipo_token = tipo_token
        self.scope = scope

    def __str__(self):
        return f"Lexema: {self.lexema}, Linea: {self.linea}, Columna: {self.columna}, Tipo de Token: {self.tipo_token}, Scope: {self.scope}"
