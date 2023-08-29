from antlr4.tree.Tree import TerminalNode
from dist.yalpParser import yalpParser
from dist.yalpLexer import yalpLexer
from tablaSimbolos import *
from treeVisitor import TreeVisitor
from dist.yalpVisitor import yalpVisitor

# class SemanticVisitor(TreeVisitor):
#     def __init__(self, lexer):
#         super().__init__(lexer)
#         self.tablaSimbolos = lexer.tablaSimbolos
#         self.errors = []

    # def postorder_visit(self, node):

    #     if not isinstance(node, TerminalNode):
    #         for child in node.children:
    #             self.postorder_visit(child)

    #     method_name = 'visit' + type(node).__name__
    #     visit_method = getattr(self, method_name, self.generic_visit)
    #     return visit_method(node)

    # def generic_visit(self, node):
    #     # Generic visit method to handle nodes without a specific visit method
    #     pass

    # def visitClass(self,  ctx: yalpParser.ClassContext):
    #     class_name = ctx.TYPE()[0].getText()

    #     if self.tablaSimbolos.get_simbolo(class_name):
    #         self.errors.append(f"Error: La clase '{class_name}' ya ha sido declarada.")
    #     else:
    #         self.tablaSimbolos.add_simbolo(Simbolo(class_name, ctx.start.line, ctx.start.column, "CLASS", self.tablaSimbolos.scope))

    # def visitFeature(self, ctx: yalpParser.FeatureContext):
    #     attr_name = ctx.ID().getText()

    #     token_type = "FUNCTION" if ctx.TYPE() else "ATTRIBUTE"

    #     if self.tablaSimbolos.get_simbolo(attr_name):
    #         self.errors.append(f"Error: El atributo/funcion '{attr_name}' ya ha sido declarado en este ámbito.")
    #     else:
    #         self.tablaSimbolos.add_simbolo(Simbolo(attr_name, ctx.start.line, ctx.start.column, token_type, self.tablaSimbolos.scope))

    # def visitFormal(self, ctx: yalpParser.FormalContext):
    #     formal_name = ctx.ID().getText()

    #     if self.tablaSimbolos.get_simbolo(formal_name):
    #         self.errors.append(f"Error: El parametro '{formal_name}' ya ha sido declarado en este ámbito.")
    #     else:
    #         self.tablaSimbolos.add_simbolo(Simbolo(formal_name, ctx.start.line, ctx.start.column, "PARAMETER", self.tablaSimbolos.scope))

    # # def visitExpr(self, ctx: yalpParser.ExprContext):
    # # TODO: Implement the type checking rules here
    # # For instance, you could add methods like visitIntType, visitStringType, visitBoolType, etc. to handle the different types
    # # and their default values, casting rules, etc.
    
    # # TODO: Implement the assignment rules here
    # # You can add methods like visitAssignment to check the type compatibility between the left-hand and right-hand side of assignments
    

    # # TODO: Implement method call and return value rules
    # # You can add methods like visitMethodCall to check the argument types, return types, etc.
    
    # # TODO: Implement control structure rules
    # # For example, you can add methods like visitIfStatement, visitWhileStatement to check the types used in these structures are as expected

    # # TODO: Implement special classes rule
    # # This could be done during the initialization or as a separate check after the tree traversal

    # def get_errors(self):
    #     return self.errors

class SemanticVisitor(yalpVisitor):
    
    def __init__(self, lexer, tablaSimbolos):
        super().__init__()
        self.lexer = lexer
        self.tablaSimbolos = tablaSimbolos
        self.scope_counter = 0
        self.errors = []

    def visit(self, ctx):
        return super().visit(ctx)

    def visitProgram(self, ctx: yalpParser.ProgramContext):
        self.scope_counter = 0
        for class_ctx in ctx.class_():
            self.visit(class_ctx)
    


    def visitClass(self, ctx: yalpParser.ClassContext):
        class_name = ctx.TYPE()[0].getText()

        scope = self.tablaSimbolos.get_enterScope()
        hay_main = False

        for feature_ctx in ctx.feature():
            feature = self.visit(feature_ctx)

            # verificar si hay un metodo main en la clase Main
            if class_name == "Main" and feature == "main":
                hay_main = True

                # verificar que el metodo main no tenga parametros
                if feature_ctx.formal():
                    self.errors.append(f"No debe haber parametros en el metodo main")

        if not hay_main and "Main" == class_name:
            self.errors.append(f"No se encontro el metodo main dentro de la clase Main")

        self.tablaSimbolos.get_exitScope()

        return class_name

    def visitFeature(self, ctx: yalpParser.FeatureContext):
        token_type = "FUNCTION" if ctx.LPAR() else "ATTRIBUTE"

        feature_name = ctx.ID().getText()

        if token_type == "FUNCTION":
            scope = self.tablaSimbolos.get_enterScope()
            
        if ctx.expr():
            self.visit(ctx.expr())
        
        for formal_ctx in ctx.formal():
            self.visit(formal_ctx)
            
        if token_type == "FUNCTION":
            self.tablaSimbolos.get_exitScope()

        return feature_name

                
    def visitExpr(self, ctx: yalpParser.ExprContext):
            
        if ctx.LET():
            scope_let = self.tablaSimbolos.get_exitScope()
            
            # ver operaciones dentro del let


            self.tablaSimbolos.get_exitScope()

        if ctx.IF():
            scope_if = self.tablaSimbolos.get_exitScope()
            self.tablaSimbolos.get_exitScope()

        if ctx.ELSE():
            scope_else = self.tablaSimbolos.get_exitScope()
            # ... procesar ELSE
            self.tablaSimbolos.get_exitScope()

        if ctx.WHILE():
            scope_while = self.tablaSimbolos.get_exitScope()
            # ... procesar WHILE
            self.tablaSimbolos.get_exitScope()


    # def visitFormal(self, ctx: yalpParser.FormalContext):
        
        # if ctx.ID() is not None and ctx.TYPE() is not None:

        #     if isinstance(ctx.ID(), list) and isinstance(ctx.TYPE(), list):

        #         ids = ctx.ID()
        #         tipos = ctx.TYPE()

        #         for id_node, tipo_node in zip(ids, tipos):

        #             variable_name = id_node.getText()
        #             variable_type = tipo_node.getText()

        #             # verificar si la variable ya ha sido declarada en este alcance
        #             if self.tablaSimbolos.get_simbolo(variable_name):
        #                 self.errors.append(f"Error: El parametro '{variable_name}' ya ha sido declarado en este ámbito.")
        #             else:
        #                 simbolo = Simbolo(variable_name, ctx.start.line, ctx.start.column, variable_type, self.tablaSimbolos.current_scope, True)
        #                 self.tablaSimbolos.add_simbolo(variable_name, simbolo)
                
        #     else:
        #         variable_name = ctx.ID().getText()
        #         variable_type = ctx.TYPE().getText()
        #         #verificar si la variable ya ha sido declarada en este alcance
        #         if self.tablaSimbolos.get_simbolo(variable_name):
        #             self.errors.append(f"Error: El parametro '{variable_name}' ya ha sido declarado en este ámbito.")
        #         else:
        #             simbolo = Simbolo(variable_name, ctx.start.line, ctx.start.column, variable_type, self.tablaSimbolos.current_scope, True)
        #             self.tablaSimbolos.add_simbolo(variable_name, simbolo)
    
    def handle_context(self, ctx, formal=False):
        for child_ctx in ctx.getChildren():
            if isinstance(child_ctx, TerminalNode):
                self.visitTerminal(child_ctx, formal)
            else:
                self.handle_context(child_ctx, formal)
        
    def visitTerminal(self, node: TerminalNode, formal=False):
        token = node.getSymbol()
        token_type = self.lexer.symbolicNames[token.type]