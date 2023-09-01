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
        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.add_simbolo("substr", Simbolo("substr", 0, 0, "String", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.exitScope()
        
        self.tablaSimbolos.add_simbolo("IO", Simbolo("IO", 0, 0, "CLASS", self.tablaSimbolos.current_scope, hereda = "Object"))
        self.tablaSimbolos.enterScope()

        self.tablaSimbolos.add_simbolo("out_string", Simbolo("out_string", 0, 0, "SELF_TYPE", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
        self.tablaSimbolos.exitScope()

        self.tablaSimbolos.add_simbolo("out_int", Simbolo("out_int", 0, 0, "SELF_TYPE", self.tablaSimbolos.current_scope))
        self.tablaSimbolos.enterScope()
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
        
        self.tablaSimbolos.add_simbolo("Bool", Simbolo("Bool", 0, 0, "CLASS", self.tablaSimbolos.current_scope, hereda = "Object"))
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
            
            if parent_class_name == class_name:
                self.errors.append(f"Error semántico: La clase '{class_name}' no puede heredar de si misma.")

            if class_name == "Main":
                self.errors.append(f"Error semántico: La clase '{class_name}' no puede heredar de otra clase.")

        if self.tablaSimbolos.get_simbolo(class_name):
            self.errors.append(f"Error semántico: La clase '{class_name}' ha sido declarada mas de una vez.")
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

            if self.tablaSimbolos.get_simbolo(variable_name):
                self.errors.append(f"Error semántico: El atributo '{variable_name}' ya ha sido declarado en este ámbito.")
            else:
                self.tablaSimbolos.add_simbolo(variable_name, Simbolo(variable_name, ctx.start.line, ctx.start.column, variable_type, self.tablaSimbolos.current_scope))
    
        else:
            feature_name = ctx.ID().getText()
            type_feature = ctx.TYPE().getText()

        
            if self.tablaSimbolos.get_simbolo(feature_name):
                self.errors.append(f"Error semántico: El atributo/funcion '{feature_name}' ya ha sido declarado en este ámbito.")
            else:
                self.tablaSimbolos.add_simbolo(feature_name, Simbolo(feature_name, ctx.start.line, ctx.start.column, type_feature, self.tablaSimbolos.current_scope))
            
        if token_type == "FUNCTION":
            self.tablaSimbolos.enterScope()
        
        if ctx.expr():
            self.visit(ctx.expr())
        
        for formal_ctx in ctx.formal():
            self.visit(formal_ctx)
            
        if token_type == "FUNCTION":
            self.tablaSimbolos.exitScope()
                
    def visitExpr(self, ctx: yalpParser.ExprContext):
            
        if ctx.LET():
            self.tablaSimbolos.enterScope()
            self.tablaSimbolos.exitScope()

        if ctx.IF():
            self.tablaSimbolos.enterScope()

            if ctx.ELSE():
                self.tablaSimbolos.enterScope()
                # ... procesar ELSE
                self.tablaSimbolos.exitScope()
            
            
            self.tablaSimbolos.exitScope()


        if ctx.WHILE():
            self.tablaSimbolos.enterScope()
            # ... procesar WHILE
            self.tablaSimbolos.exitScope()

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

        else:
            if ctx.ID():
                for id_node in ctx.ID():
                    variable_name = id_node.getText()

    def visitFormal(self, ctx: yalpParser.FormalContext):
        
        if ctx.ID() is not None and ctx.TYPE() is not None:

            if isinstance(ctx.ID(), list) and isinstance(ctx.TYPE(), list):

                ids = ctx.ID()
                tipos = ctx.TYPE()

                for id_node, tipo_node in zip(ids, tipos):

                    variable_name = id_node.getText()
                    variable_type = tipo_node.getText()

                    # verificar si la variable ya ha sido declarada en este alcance
                    if self.tablaSimbolos.get_simbolo(variable_name):
                        self.errors.append(f"Error semántico: El parametro '{variable_name}' ya ha sido declarado en este ámbito.")
                    else:
                        simbolo = Simbolo(variable_name, ctx.start.line, ctx.start.column, variable_type, self.tablaSimbolos.current_scope, True)
                        self.tablaSimbolos.add_simbolo(variable_name, simbolo)
                
                # regresar el arreglo de tipos
                return [tipo.getText() for tipo in tipos]
            else:

                variable_name = ctx.ID().getText()
                variable_type = ctx.TYPE().getText()
                #verificar si la variable ya ha sido declarada en este alcance
                if self.tablaSimbolos.get_simbolo(variable_name):
                    self.errors.append(f"Error semántico: El parametro '{variable_name}' ya ha sido declarado en este ámbito.")
                else:
                    simbolo = Simbolo(variable_name, ctx.start.line, ctx.start.column, variable_type, self.tablaSimbolos.current_scope, True)
                    self.tablaSimbolos.add_simbolo(variable_name, simbolo)

                # regresar el tipo
                return variable_type
            
    def handle_context(self, ctx, formal=False):
        for child_ctx in ctx.getChildren():
            if isinstance(child_ctx, TerminalNode):
                self.visitTerminal(child_ctx, formal)
                
            else:
                self.handle_context(child_ctx, formal)
        
    def visitTerminal(self, node: TerminalNode, formal=False):
        token = node.getSymbol()
        token_type = self.lexer.symbolicNames[token.type]
        
        # if token_type in ["LET", "ELSE", "WHILE", "IF"]:
        #     # self.in_function = True
        #     # self.tablaSimbolos.enterScope()
        #    # # self.in_function = False
        #     self.tablaSimbolos.enterScope()
        #     self.tablaSimbolos.add_simbolo(Simbolo(token.text, token.line, token.column, token_type, self.tablaSimbolos.current_scope))
            
        
        # if token_type in ["FI", "POOL"]:
        #     self.tablaSimbolos.exitScope()

        # if token_type == "LBRACE":
        #    self.tablaSimbolos.enterScope()
        # elif token_type == "RBRACE":
        #     self.tablaSimbolos.exitScope()

        # if token_type == "LPAR" or token_type == "RPAR" or token_type == "LBRACE" or token_type == "RBRACE" or token_type == "SEMICOLON":
        #     return 

        # # SISTEMA DE TIPOS
        # if token_type == "TRUE" or token_type == "FALSE":
        #     token_type = "BOOLEAN"
        # elif token_type == "DIGIT":
        #     token_type = "INT"

        # if formal and token_type == "ID":
        #     self.tablaSimbolos.add_simbolo(Simbolo(token.text, token.line, token.column, "Parametro", self.tablaSimbolos.current_scope))
        
        # else:
        #     self.tablaSimbolos.add_simbolo(Simbolo(token.text, token.line, token.column, token_type, self.tablaSimbolos.current_scope))

    def visitErrorNode(self, node):
        print("Error semántico: ", node.getText())
        return ['Indefinido']
    
    # def process_tokens(self, tokens, tablaSimbolos):
    #     skip_next = False 
    #     for token in tokens:
            
    #         if token is None:
    #             continue

    #         if isinstance(token, list):
    #             tablaSimbolos.enterScope()
    #             self.process_tokens(token, tablaSimbolos)
    #             tablaSimbolos.exitScope()
    #         else:
    #             tablaSimbolos.print_tabla()
    #             input()
    #             if token['text'] == ':' and not skip_next:
    #                 skip_next = True
    #                 continue
    #             if skip_next:
    #                 last_symbol_key = list(tablaSimbolos.pila_alcances[-1])[-1]
    #                 last_symbol = tablaSimbolos.pila_alcances[-1][last_symbol_key]

    #                 tablaSimbolos.actualizar_simbolo(last_symbol, token['text'])
    #                 skip_next = False
                    
    #                 continue
                
    #             # Add the token as a symbol to the symbol table
    #             tablaSimbolos.add_simbolo(Simbolo(token['text'], token['line'], token['column'], token['type'], tablaSimbolos.current_scope))




