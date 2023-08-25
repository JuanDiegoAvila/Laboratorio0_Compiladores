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
        return super().visit(ctx)

    def visitProgram(self, ctx: yalpParser.ProgramContext):
        for class_ctx in ctx.class_():
            self.visit(class_ctx)

    def visitClass(self, ctx: yalpParser.ClassContext):
        class_name = ctx.TYPE()[0].getText()

        self.tablaSimbolos.add_simbolo(Simbolo(class_name, ctx.start.line, ctx.start.column, "CLASS", self.tablaSimbolos.current_scope()))
        self.tablaSimbolos.enter_class()

        for feature_ctx in ctx.feature():
            self.visit(feature_ctx)

    def visitFeature(self, ctx: yalpParser.FeatureContext):
        feature_name = ctx.ID().getText()
        token_type = "FUNCTION" if ctx.LPAR() else "ATTRIBUTE"
        
        self.tablaSimbolos.add_simbolo(Simbolo(feature_name, ctx.start.line, ctx.start.column, token_type, self.tablaSimbolos.current_scope()))

        if token_type == "FUNCTION":
            self.tablaSimbolos.in_function(True)
            self.tablaSimbolos.enterScope()
            
        if ctx.expr():
            self.visitExpr(ctx.expr())
        
        for formal_ctx in ctx.formal():
            self.visit(formal_ctx)

        if token_type == "FUNCTION":
            self.tablaSimbolos.in_function(False)

        self.tablaSimbolos.exitScope()

    def visitExpr(self, ctx: yalpParser.ExprContext):
        self.handle_context(ctx)

    def visitFormal(self, ctx: yalpParser.FormalContext):
        self.handle_context(ctx)

    def handle_context(self, ctx):
        for child_ctx in ctx.getChildren():
            if isinstance(child_ctx, TerminalNode):
                self.visitTerminal(child_ctx)
            else:
                self.handle_context(child_ctx)

    def visitTerminal(self, node: TerminalNode):
        token = node.getSymbol()

        token_type = self.lexer.symbolicNames[token.type]

        if token_type == "LBRACE":
            self.tablaSimbolos.enterScope()
        elif token_type == "RBRACE":
            self.tablaSimbolos.exitScope()

        if token_type == "LPAR" or token_type == "RPAR" or token_type == "LBRACE" or token_type == "RBRACE" or token_type == "SEMICOLON":
            return

        # # SISTEMA DE TIPOS
        # if token_type == "TRUE" or token_type == "FALSE":
        #     token_type = "BOOLEAN"
        # elif token_type == "DIGIT":
        #     token_type = "INT"


        self.tablaSimbolos.add_simbolo(Simbolo(token.text, token.line, token.column, token_type, self.tablaSimbolos.current_scope()))





