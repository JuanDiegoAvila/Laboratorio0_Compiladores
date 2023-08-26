from prettytable import PrettyTable
from interfaz import custom_print, get_global_terminal

# class TablaSimbolos(object):

#     def __init__(self):
#         self.pila_alcances = [{}]
#         self.indice = 0
#         self.func_index = 0
#         self.class_index = 0
#         self.indice_global = 0
#         self.in_class = False
#         self.in_function = False
#         self.global_terminal = get_global_terminal()


#     def add_simbolo(self, simbolo):
#         if self.in_function:
#             self.pila_alcances[self.func_index][simbolo.lexema] = simbolo
#         else:
#             self.pila_alcances[self.indice][simbolo.lexema] = simbolo

#     def get_simbolo(self, nombre):
#         for alcance in reversed(self.pila_alcances):
#             if nombre in alcance:
#                 return alcance[nombre]
#         return None
    
#     def actualizar_simbolo(self, simbolo, tipo_token):
#         for alcance in reversed(self.pila_alcances):
#             if simbolo.lexema in alcance:
#                 if alcance[simbolo.lexema].linea == simbolo.linea and alcance[simbolo.lexema].columna == simbolo.columna:
#                     alcance[simbolo.lexema].tipo_token = tipo_token
#                     return
    
#     def enterScope(self, function= False, class_= False):
#         self.pila_alcances.append({})

#         if class_:
#             self.indice = 0
        
#         if function:
#             self.func_index = len(self.pila_alcances) -1
#             self.in_function = True

#         else:
#             self.func_index += 1
#             self.indice += 1


#     def exitScope(self, function=False, class_=False):

#         if class_: 
#             self.indice = 0
#             return
        
#         if function:
#             self.in_function = False
#             self.func_index = 0
#         else:
#             self.func_index -= 1
#             self.indice -= 1


#     def current_scope(self):
#         if self.in_function:
#             return self.func_index
#         return self.indice
    
#     def print_tabla(self):
#         custom_print(self.global_terminal, "Tabla de simbolos:")

#         conteo_alcances = 0
#         for tabla in self.pila_alcances:
#             x = PrettyTable()
#             custom_print(self.global_terminal, "Alcance: " + str(conteo_alcances))
#             x.field_names = ["Lexema", "Linea", "Columna", "Tipo de Token", "Global", "Parametro"]
#             for simbolo in tabla.values():
#                 x.add_row([simbolo.lexema, simbolo.linea, simbolo.columna, simbolo.tipo_token, simbolo.global_, simbolo.parametro])
#             custom_print(self.global_terminal, x)
            
#             conteo_alcances += 1
    
class Simbolo:
    def __init__(self, lexema, linea, columna, tipo_token, scope, parametro=False):
        self.lexema = lexema
        self.linea = linea
        self.columna = columna
        self.tipo_token = tipo_token
        self.scope = scope
        self.global_ = False
        self.parametro = parametro

    def __str__(self):
        return f"Lexema: {self.lexema}, Linea: {self.linea}, Columna: {self.columna}, Tipo de Token: {self.tipo_token}, Scope: {self.scope}, Parametro: {self.parametro}"

    def setGlobal(self, global_):
        self.global_ = global_

class Scope:
    def __init__(self, name=""):
        self.name = name
        self.parent = None
        self.children = []
        self.symbols = {}
        self.global_terminal = get_global_terminal()

    def add_symbol(self, name, symbol):
        self.symbols[name] = symbol

    def get_symbol(self, name):
        return self.symbols.get(name, None)

    def enter(self, name):
        new_scope = Scope()
        new_scope.name = name
        new_scope.parent = self
        self.children.append(new_scope)
        return new_scope

    def exit(self):
        return self.parent
    
    def print_scope(self, level=0):
        indent = '  ' * level
        print(f"{indent}Scope {self.name}:")
        
        x = PrettyTable()
        x.field_names = ["Lexema", "Linea", "Columna", "Tipo de Token", "Global", "Parametro"]
        for name, simbolo in self.symbols.items():
            x.add_row([simbolo.lexema, simbolo.linea, simbolo.columna, simbolo.tipo_token, simbolo.global_, simbolo.parametro])
        custom_print(self.global_terminal, x)
        for child in self.children:
            child.print_scope(level+1)


class TablaSimbolos:
    def __init__(self):
        self.conteo_scopes = 0
        self.global_scope = Scope(self.conteo_scopes)
        self.current_scope = self.global_scope

    def enterScope(self):
        self.conteo_scopes += 1
        self.current_scope = self.current_scope.enter(self.conteo_scopes)

    def exitScope(self):
        self.current_scope = self.current_scope.exit()

    def add_simbolo(self, name, simbolo):
        self.current_scope.add_symbol(name, simbolo)

    def getSymbol(self, name):
        temp_scope = self.current_scope
        while temp_scope:
            symbol = temp_scope.get_symbol(name)
            if symbol:
                return symbol
            temp_scope = temp_scope.parent
        return None
    
    def print_tabla(self):
        self.global_scope.print_scope()
    

from graphviz import Digraph

class ScopeVisualizer:
    def __init__(self, tablaSimbolos):
        self.tablaSimbolos = tablaSimbolos
        self.graph = Digraph('Scopes', node_attr={'style': 'filled', 'fillcolor': 'lightyellow'})

    def visualize(self):
        self._add_nodes_and_edges(self.tablaSimbolos.global_scope, None)
        self.graph.render('scope', view=True, format='png')

    def _add_nodes_and_edges(self, current_scope, parent_scope):
        scope_label = f"Scope {current_scope.name}\nSymbols: {', '.join(current_scope.symbols.keys())}"
        self.graph.node(str(current_scope.name), label=scope_label)
        
        if parent_scope:
            self.graph.edge(str(parent_scope.name), str(current_scope.name))

        for child_scope in current_scope.children:
            self._add_nodes_and_edges(child_scope, current_scope)

