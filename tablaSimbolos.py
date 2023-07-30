class TablaSimbolos(object):
    def __init__(self):
        self.tabla = []

    def get_simbolo(self, lexema):
        for simbolo in self.tabla:
            if simbolo.lexema == lexema:
                return simbolo
        return None

    def add_simbolo(self, lexema, linea, columna, tipo):

        self.tabla.append({
            'lexema': lexema,
            'linea': linea,
            'columna': columna,
            'tipo': tipo
        })

    def print_tabla(self):
        print("Tabla de simbolos:")
        for simbolo in self.tabla:
            print(simbolo)
        print("")
        