from antlr4.tree.Tree import TerminalNode
from graphviz import Digraph
from dist.yalpParser import yalpParser
from dist.yalpLexer import yalpLexer
from dist.yalpVisitor import yalpVisitor
from tablaSimbolos import *

class TreeVisitor(yalpVisitor):
    def __init__(self, lexer):
        super().__init__()
        self.lexer = lexer
        self.tablaSimbolos = lexer.tablaSimbolos
        self.graph = Digraph()
        self.id = 0
        self.scope_counter = 0
        self.errors = []
        self.nativas = False

    def visitar(self, tree):
        label = self.getNodeLabel(tree)

        # obtener el tipo de la label
        if isinstance(tree, TerminalNode):
            token_type = self.lexer.symbolicNames[tree.getSymbol().type]
            if token_type == "ERROR":
                label = f"Error: {tree.getText()}"

        self.graph.node(str(self.id), label)
        padre = self.id
        self.id += 1

        if not isinstance(tree, TerminalNode):  
            for c in tree.children:  
                self.graph.edge(str(padre), str(self.id))
                self.visitar(c)

        return self.graph

    def getNodeLabel(self, node):
        if isinstance(node, TerminalNode):
            return node.getText()
        else:
            class_name = type(node).__name__
            rule_name = class_name.split('.')[1] if '.' in class_name else class_name
            rule_name = rule_name[:-7] if rule_name.endswith('Context') else rule_name
            return rule_name

    def visit(self, ctx):
        if not self.nativas:
            self.crear_nativas()
            self.nativas = True

        return super().visit(ctx)
    
    def crear_nativas(self):
        self.tablaSimbolos.add_simbolo("Object", Simbolo("Object", 0, 0, "CLASS", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
        
        self.tablaSimbolos.add_simbolo("abort", Simbolo("abort", 0, 0, "Object", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
        self.tablaSimbolos.exitScope()
        
        self.tablaSimbolos.add_simbolo("type_name", Simbolo("type_name", 0, 0, "String", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.add_simbolo("copy", Simbolo("copy", 0, 0, "Object", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.add_simbolo("String", Simbolo("String", 0, 0, "CLASS", self.tablaSimbolos.current_scope, hereda = "Object"))
        self.tablaSimbolos.enterScope()

        self.tablaSimbolos.add_simbolo("length", Simbolo("length", 0, 0, "Int", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.add_simbolo("concat", Simbolo("concat", 0, 0, "String", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
        # agregar parametro str de tipo String
        self.tablaSimbolos.add_simbolo("str", Simbolo("str", 0, 0, "String", self.tablaSimbolos.current_scope, True))
        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.add_simbolo("substr", Simbolo("substr", 0, 0, "String", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
        # agregar parametro i de tipo Int
        self.tablaSimbolos.add_simbolo("i", Simbolo("i", 0, 0, "Int", self.tablaSimbolos.current_scope, True))
        # agregar parametro l de tipo Int
        self.tablaSimbolos.add_simbolo("l", Simbolo("l", 0, 0, "Int", self.tablaSimbolos.current_scope, True))
        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.exitScope()
        
        self.tablaSimbolos.add_simbolo("IO", Simbolo("IO", 0, 0, "CLASS", self.tablaSimbolos.current_scope, hereda = "Object"))
        self.tablaSimbolos.enterScope()

        self.tablaSimbolos.add_simbolo("out_string", Simbolo("out_string", 0, 0, "SELF_TYPE", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
        # agregar parametro str de tipo String
        self.tablaSimbolos.add_simbolo("str", Simbolo("str", 0, 0, "String", self.tablaSimbolos.current_scope, True))
        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.add_simbolo("out_int", Simbolo("out_int", 0, 0, "SELF_TYPE", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
        # agregar parametro i de tipo Int
        self.tablaSimbolos.add_simbolo("i", Simbolo("i", 0, 0, "Int", self.tablaSimbolos.current_scope, True))
        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.add_simbolo("in_string", Simbolo("in_string", 0, 0, "String", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.add_simbolo("in_int", Simbolo("in_int", 0, 0, "Int", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.add_simbolo("Int", Simbolo("Int", 0, 0, "CLASS", self.tablaSimbolos.current_scope, hereda = "Object"))
        self.tablaSimbolos.enterScope()
        self.tablaSimbolos.exitScope()
        
        self.tablaSimbolos.add_simbolo("Boolean", Simbolo("Boolean", 0, 0, "CLASS", self.tablaSimbolos.current_scope, hereda = "Object"))
        self.tablaSimbolos.enterScope()
        self.tablaSimbolos.exitScope()
        
    def visitProgram(self, ctx: yalpParser.ProgramContext):
        self.scope_counter = 0
        for class_ctx in ctx.class_():
            self.visit(class_ctx)

    def visitClass(self, ctx: yalpParser.ClassContext):
        class_name = ctx.TYPE()[0].getText()
        parent_class_name = None
        if ctx.INHERITS():
            parent_class_name = ctx.TYPE()[1].getText()
            if not self.tablaSimbolos.get_simbolo(parent_class_name):
                self.errors.append(f"Error semántico: La clase '{parent_class_name}' no ha sido declarada.")
            
            if class_name == "SELF_TYPE":
                self.errors.append(f"Error semántico: La clase '{class_name}' no se puede llamar 'SELF_TYPE'.")

            if parent_class_name == class_name:
                self.errors.append(f"Error semántico: La clase '{class_name}' no puede heredar de sí misma.")
            
            if parent_class_name == "Int" or parent_class_name == "String" or parent_class_name == "Bool":
                self.errors.append(f"Error semántico: La clase '{class_name}' no puede heredar de la clase '{parent_class_name}'.")
            
            if class_name == "Main":
                self.errors.append(f"Error semántico: La clase '{class_name}' no puede heredar de otra clase.")

        if self.tablaSimbolos.get_simbolo(class_name):
            self.errors.append(f"Error semántico: La clase '{class_name}' ha sido declarada más de una vez.")
        else:
            self.tablaSimbolos.add_simbolo(class_name, Simbolo(class_name, ctx.start.line, ctx.start.column, "CLASS", self.tablaSimbolos.current_scope, hereda=parent_class_name))
        
        self.tablaSimbolos.enterScope()

        for feature_ctx in ctx.feature():
            self.visit(feature_ctx)
        
        self.tablaSimbolos.exitScope()

    def visitFeature(self, ctx: yalpParser.FeatureContext):
        token_type = "FUNCTION" if ctx.LPAR() else "ATTRIBUTE"

        if token_type == "ATTRIBUTE" and ctx.ID() is not None and ctx.TYPE() is not None:

            variable_name = ctx.ID().getText()
            variable_type = ctx.TYPE().getText()

            if not self.tablaSimbolos.get_classes(variable_type):
                error = f"Error semántico: El tipo {variable_type} no ha sido declarado."
                if error not in self.errors:
                    self.errors.append(error)

            if variable_name == "self":
                line = ctx.start.line
                column = ctx.start.column
                self.errors.append(f"Error semántico: No se puede declarar un atributo o función con el nombre 'self' en la línea {line} y columna {column}.")

            if self.tablaSimbolos.get_simbolo(variable_name):
                self.errors.append(f"Error semántico: El atributo '{variable_name}' ya ha sido declarado en este ámbito.")
            else:
                self.tablaSimbolos.add_simbolo(variable_name, Simbolo(variable_name, ctx.start.line, ctx.start.column, variable_type, self.tablaSimbolos.current_scope))
    
        else:
            
            feature_name = ctx.ID().getText()
            type_feature = ctx.TYPE().getText() if ctx.TYPE() is not None else None

            if not self.tablaSimbolos.get_classes(type_feature):
                error = f"Error semántico: El tipo {type_feature} no ha sido declarado."
                if error not in self.errors:
                    self.errors.append(error)

            if feature_name == "self":
                line = ctx.start.line
                column = ctx.start.column
                self.errors.append(f"Error semántico: No se puede declarar un atributo o función con el nombre 'self' en la línea {line} y columna {column}.")

            
            if self.tablaSimbolos.get_simbolo(feature_name):
                self.errors.append(f"Error semántico: El atributo/función '{feature_name}' ya ha sido declarado en este ámbito.")
            else:
                self.tablaSimbolos.add_simbolo(feature_name, Simbolo(feature_name, ctx.start.line, ctx.start.column, type_feature, self.tablaSimbolos.current_scope, funcion=True))
            
        if token_type == "FUNCTION":
            self.tablaSimbolos.enterScope()

        if ctx.expr():
            self.visit(ctx.expr())
        
        for formal_ctx in ctx.formal():
            self.visit(formal_ctx)
        # self.handle_context(ctx)
            
        if token_type == "FUNCTION":
            self.tablaSimbolos.exitScope()
                
    def visitExpr(self, ctx: yalpParser.ExprContext):

        if ctx.IF():
            self.tablaSimbolos.enterScope()
            
            if ctx.ELSE():
                self.tablaSimbolos.enterScope()
                
                # self.handle_context(ctx)
                self.tablaSimbolos.exitScope()

            
            self.handle_context(ctx)
            
            self.tablaSimbolos.exitScope()

        elif ctx.WHILE():
            self.tablaSimbolos.enterScope()
            
            self.handle_context(ctx)

            self.tablaSimbolos.exitScope()
        
        elif ctx.LET():
            self.tablaSimbolos.enterScope()
            
            if ctx.ID() is not None and ctx.TYPE() is not None:
                ids = ctx.ID()
            
                tipos = ctx.TYPE()

                for id_node, tipo_node in zip(ids, tipos):

                    variable_name = id_node.getText()
                    variable_type = tipo_node.getText()

                    # verificar si la variable ya ha sido declarada en este alcance
                    if self.tablaSimbolos.get_simbolo(variable_name):
                        self.errors.append(f"Error semántico: La variable '{variable_name}' ya ha sido declarada en este alcance.")
                    
                    else:
                        # Crear un nuevo símbolo para esta variable y agregarlo a la tabla de símbolos
                        simbolo = Simbolo(variable_name, ctx.start.line, ctx.start.column, variable_type, self.tablaSimbolos.current_scope)
                        self.tablaSimbolos.add_simbolo(variable_name, simbolo)
            
        
            self.handle_context(ctx)

            self.tablaSimbolos.exitScope()

        else:
            v = self.handle_context(ctx) 
            return v

    def visitFormal(self, ctx: yalpParser.FormalContext):
        
        if ctx.ID() is not None and ctx.TYPE() is not None:

            if isinstance(ctx.ID(), list) and isinstance(ctx.TYPE(), list):

                ids = ctx.ID()
                tipos = ctx.TYPE()

                for id_node, tipo_node in zip(ids, tipos):

                    if not self.tablaSimbolos.get_classes(variable_type):
                        error = f"Error semántico: El tipo {variable_type} no ha sido declarado."
                        if error not in self.errors:
                            self.errors.append(error)
                    else:
                        

                        variable_name = id_node.getText()
                        variable_type = tipo_node.getText()

                        # verificar si la variable ya ha sido declarada en este alcance
                        if self.tablaSimbolos.get_current_scope_simbolo(variable_name):
                            self.errors.append(f"Error semántico: El parámetro '{variable_name}' ya ha sido declarado en este ámbito.")
                        else:
                            simbolo = Simbolo(variable_name, ctx.start.line, ctx.start.column, variable_type, self.tablaSimbolos.current_scope, True)
                            self.tablaSimbolos.add_simbolo(variable_name, simbolo)
                    
                        # regresar el arreglo de tipos
                        return [tipo.getText() for tipo in tipos]
                    
            else:

                variable_name = ctx.ID().getText()
                variable_type = ctx.TYPE().getText()

                if not self.tablaSimbolos.get_classes(variable_type):
                    error = f"Error semántico: El tipo {variable_type} no ha sido declarado."
                    if error not in self.errors:
                        self.errors.append(error)
                else:

                    #verificar si la variable ya ha sido declarada en este alcance
                    if self.tablaSimbolos.get_current_scope_simbolo(variable_name):
                        self.errors.append(f"Error semántico: El parámetro {variable_name} ya ha sido declarado en este ámbito.")
                    else:
                        simbolo = Simbolo(variable_name, ctx.start.line, ctx.start.column, variable_type, self.tablaSimbolos.current_scope, True)
                        self.tablaSimbolos.add_simbolo(variable_name, simbolo)
                    
                    # regresar el tipo
                    return [variable_type]
            
    def handle_context(self, ctx, formal=False):
        for child_ctx in ctx.getChildren():
            if isinstance(child_ctx, TerminalNode):
                self.visitTerminal(child_ctx, formal)
            
            else:
                self.visit(child_ctx)

    def visitTerminal(self, node: TerminalNode, formal=False):
        token = node.getSymbol()
        token_type = self.lexer.symbolicNames[token.type]
    
