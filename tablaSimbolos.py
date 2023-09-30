from prettytable import PrettyTable
from interfaz import custom_print, get_global_terminal

class Simbolo:
    def __init__(self, lexema, linea, columna, tipo_token, scope, parametro=False, hereda=None, funcion=False):
        self.nativesizes = {'Boolean':1, 'Int':4, 'String':256}
        self.lexema = lexema
        self.linea = linea
        self.columna = columna
        self.tipo_token = tipo_token
        self.scope = scope
        self.global_ = False
        self.parametro = parametro
        self.hereda = hereda
        self.funcion = funcion
        self.size = 0
        self.offset = 0

        if self.tipo_token == 'CLASS':
            if self.tipo_token in self.nativesizes:
                self.size = self.nativesizes[self.tipo_token]
            if self.lexema in self.nativesizes:
                self.size = self.nativesizes[self.lexema]


            

    def __str__(self):
        return f"Lexema: {self.lexema}, Linea: {self.linea}, Columna: {self.columna}, Tipo de Token: {self.tipo_token}, Scope: {self.scope}, Parametro: {self.parametro}, Hereda: {self.hereda}, Funcion: {self.funcion}, Tamaño (bytes): {self.size}, Offset: {self.offset}"

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

    #Permite obtener el scope del algun simbolo entre los hijos
    def get_symbol_scope(self, symbol):
        if self.children:
            keys = list(self.symbols.keys())
            functions= [key for key,value in self.symbols.items() if value.funcion==True]
            idx = keys.index(symbol.lexema)
            if symbol.lexema in functions:
                idx = functions.index(symbol.lexema)
            for child in range(len(self.children)):
                if child==idx:
                    return (self.children[child], symbol.hereda)
        return None 

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
        custom_print(self.global_terminal, f"\n{indent}Scope {self.name}:")
        
        x = PrettyTable()
        x.field_names = ["Lexema", "Linea", "Columna", "Tipo de Token", "Global", "Parametro", "Hereda", "Funcion", "Tamaño (bytes)", "Offset"]
        for name, simbolo in self.symbols.items():
            x.add_row([simbolo.lexema, simbolo.linea, simbolo.columna, simbolo.tipo_token, simbolo.global_, simbolo.parametro, simbolo.hereda, simbolo.funcion, simbolo.size, simbolo.offset])
        custom_print(self.global_terminal, x)
        for child in self.children:
            child.print_scope(level+1)

class TablaSimbolos:
    def __init__(self):
        self.conteo_scopes = 0
        self.index_scopes = 0
        self.global_scope = Scope(self.conteo_scopes)
        self.current_scope = self.global_scope
        self.all_scopes = [self.global_scope]
        self.actual_scope = 0
    
    def get_enterScope(self):
        if self.index_scopes == 0:
            self.index_scopes = 16
        else:
            self.index_scopes += 1

        
        for scope in self.all_scopes:
            if scope.name == self.index_scopes:                
                self.current_scope = scope
                
                return scope
    
    def get_scope_simbolo(self, name, class_name):

        if self.current_scope:
            for scope in self.all_scopes:
                if scope.name == self.current_scope.name:
                    temp_scope = scope
                    while temp_scope:
                        symbol = temp_scope.get_symbol(name)
                        
                        if symbol:
                            return symbol, False
                        
                        if temp_scope.parent:
                            temp_scope = temp_scope.parent
                        else:
                            break

        hereda = temp_scope.symbols[class_name].hereda
        if hereda:
            for children in temp_scope.children:
                for simbols in children.symbols:
                    if children.symbols[simbols].lexema == name:

                        # agregar el atributo heredado al scope con el que se encontro el simbolo
                        return children.symbols[simbols], True
        
        return None, False
    
    def get_exitScope(self):
        self.current_scope = self.current_scope.exit()
        # self.index_scopes = self.current_scope.name

    def enterScope(self):
        self.conteo_scopes += 1
        self.current_scope = self.current_scope.enter(self.conteo_scopes)
        self.all_scopes.append(self.current_scope)

    def exitScope(self):
        self.current_scope = self.current_scope.exit()

    def add_simbolo(self, name, simbolo):
        self.current_scope.add_symbol(name, simbolo)

    def update_simbol(self, simbol):
        existe = False
        for name, simbolo in self.current_scope.symbols.items():
            if simbolo.lexema == simbol.lexema and simbolo.linea == simbol.linea and simbolo.columna == simbol.columna:
                simbolo.tipo_token = simbol.tipo_token
                simbolo.parametro.append(simbol.parametro)
                simbolo.hereda = simbol.hereda
                existe = True
                return
        
        if not existe:
            self.current_scope.add_symbol(simbol.lexema, simbol)

    def get_simbolo(self, name):
        temp_scope = self.current_scope

        while temp_scope:
            symbol = temp_scope.get_symbol(name)
            if symbol:
                return symbol
            temp_scope = temp_scope.parent
        return None
    
    def get_current_scope_simbolo(self, name):
        temp_scope = self.current_scope
        symbol = temp_scope.get_symbol(name)
        if symbol:
            return temp_scope
        
        return None
    
    def print_tabla(self):
        self.global_scope.print_scope()
    
    def get_classes(self, tipo):
        classes = []
        for scope in self.all_scopes:
            for name, simbolo in scope.symbols.items():
                if simbolo.tipo_token == "CLASS":
                    classes.append(simbolo.lexema)
        return tipo in classes

from graphviz import Digraph

class ScopeVisualizer:
    def __init__(self, tablaSimbolos):
        self.tablaSimbolos = tablaSimbolos
        self.graph = Digraph('Scopes', node_attr={'style': 'filled', 'fillcolor': 'lightyellow'})

    def visualize(self):
        self._add_nodes_and_edges(self.tablaSimbolos.global_scope, None)
        self.graph.render('./grafos/scope', view=True, format='png')

    def _add_nodes_and_edges(self, current_scope, parent_scope):
        scope_label = f"Scope {current_scope.name}\nSimbolos: {', '.join(current_scope.symbols.keys())}"
        self.graph.node(str(current_scope.name), label=scope_label)
        
        if parent_scope:
            self.graph.edge(str(parent_scope.name), str(current_scope.name))

        for child_scope in current_scope.children:
            self._add_nodes_and_edges(child_scope, current_scope)

