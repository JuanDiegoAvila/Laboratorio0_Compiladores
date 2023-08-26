from antlr4.tree.Tree import TerminalNode
from dist.yalpParser import yalpParser
from dist.yalpLexer import yalpLexer
from tablaSimbolos import *
from treeVisitor import TreeVisitor

class SemanticVisitor(TreeVisitor):
    def __init__(self, lexer):
        super().__init__(lexer)
        self.tablaSimbolos = lexer.tablaSimbolos
        self.errors = []

    def postorder_visit(self, node):

        if not isinstance(node, TerminalNode):
            for child in node.children:
                self.postorder_visit(child)

        method_name = 'visit' + type(node).__name__
        visit_method = getattr(self, method_name, self.generic_visit)
        return visit_method(node)

    def generic_visit(self, node):
        # Generic visit method to handle nodes without a specific visit method
        pass

    def visitClass(self,  ctx: yalpParser.ClassContext):
        class_name = ctx.TYPE()[0].getText()

        if self.tablaSimbolos.get_simbolo(class_name):
            self.errors.append(f"Error: La clase '{class_name}' ya ha sido declarada.")
        else:
            self.tablaSimbolos.add_simbolo(Simbolo(class_name, ctx.start.line, ctx.start.column, "CLASS", self.tablaSimbolos.scope))

    def visitFeature(self, ctx: yalpParser.FeatureContext):
        attr_name = ctx.ID().getText()

        token_type = "FUNCTION" if ctx.TYPE() else "ATTRIBUTE"

        if self.tablaSimbolos.get_simbolo(attr_name):
            self.errors.append(f"Error: El atributo/funcion '{attr_name}' ya ha sido declarado en este ámbito.")
        else:
            self.tablaSimbolos.add_simbolo(Simbolo(attr_name, ctx.start.line, ctx.start.column, token_type, self.tablaSimbolos.scope))

    def visitFormal(self, ctx: yalpParser.FormalContext):
        formal_name = ctx.ID().getText()

        if self.tablaSimbolos.get_simbolo(formal_name):
            self.errors.append(f"Error: El parametro '{formal_name}' ya ha sido declarado en este ámbito.")
        else:
            self.tablaSimbolos.add_simbolo(Simbolo(formal_name, ctx.start.line, ctx.start.column, "PARAMETER", self.tablaSimbolos.scope))

    # def visitExpr(self, ctx: yalpParser.ExprContext):
    # TODO: Implement the type checking rules here
    # For instance, you could add methods like visitIntType, visitStringType, visitBoolType, etc. to handle the different types
    # and their default values, casting rules, etc.
    
    # TODO: Implement the assignment rules here
    # You can add methods like visitAssignment to check the type compatibility between the left-hand and right-hand side of assignments
    

    # TODO: Implement method call and return value rules
    # You can add methods like visitMethodCall to check the argument types, return types, etc.
    
    # TODO: Implement control structure rules
    # For example, you can add methods like visitIfStatement, visitWhileStatement to check the types used in these structures are as expected

    # TODO: Implement special classes rule
    # This could be done during the initialization or as a separate check after the tree traversal

    def get_errors(self):
        return self.errors
