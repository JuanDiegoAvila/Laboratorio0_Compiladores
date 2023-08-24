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
            #print("Nodo terminal", node.getText())
            return node.getText()
        else:
            class_name = type(node).__name__
            #print("node_no terminal: ", node.getText())
            rule_name = class_name.split('.')[1] if '.' in class_name else class_name
            rule_name = rule_name[:-7] if rule_name.endswith('Context') else rule_name
            return rule_name
        
    def enterClass(self, ctx):
        self.lexer.enterScope()

    def visitProgram(self, ctx: yalpParser.ProgramContext):
        for class_ctx in ctx.class_():
            self.visit(class_ctx)

    def visitClass(self, ctx: yalpParser.ClassContext):
        class_name = ctx.TYPE()[0].getText()

        self.lexer.enterScope()
        self.tablaSimbolos.add_simbolo(Simbolo(class_name, ctx.start.line, ctx.start.column, "CLASS", self.tablaSimbolos.scope))

        # Visitar otras partes de la declaración de la clase
        for feature_ctx in ctx.feature():
            self.visit(feature_ctx)

        
        self.lexer.exitScope()

    # Implementar más métodos visit para otras reglas gramaticales

    def visitFeature(self, ctx: yalpParser.FeatureContext):
        feature_name = ctx.ID().getText()
        self.lexer.enterScope()
        
        # Determine si es una función o atributo
        token_type = "FUNCTION" if ctx.LPAR() else "ATTRIBUTE"
        self.tablaSimbolos.add_simbolo(Simbolo(feature_name, ctx.start.line, ctx.start.column, token_type, self.tablaSimbolos.scope))

        # Visitar otras partes de la declaración de la función o atributo
        if ctx.expr():
            self.visitExpr(ctx.expr())
        
        for formal_ctx in ctx.formal():
            self.visit(formal_ctx)

        self.lexer.exitScope()

  
    # def visitFormal(self, ctx: yalpParser.FormalContext):
    #     if ctx.ID():
    #         formal_name = ctx.ID().getText()

    #         self.tablaSimbolos.add_simbolo(Simbolo(formal_name, ctx.start.line, ctx.start.column, "FORMAL", self.tablaSimbolos.scope))

    #     if ctx.TYPE():
    #         formal_type = ctx.TYPE().getText()

    #         self.tablaSimbolos.add_simbolo(Simbolo(formal_type, ctx.start.line, ctx.start.column, "TYPE", self.tablaSimbolos.scope))

    # def visitExpr(self, ctx: yalpParser.ExprContext):
    #     if ctx.ID():
    #         for id in ctx.ID():
    #             self.tablaSimbolos.add_simbolo(Simbolo(id.getText(), ctx.start.line, ctx.start.column, "VAR", self.tablaSimbolos.scope))
        
    #     if ctx.TYPE():
    #         for type in ctx.TYPE():
    #             self.tablaSimbolos.add_simbolo(Simbolo(type.getText(), ctx.start.line, ctx.start.column, "TYPE", self.tablaSimbolos.scope))

    #     if ctx.STRING():
    #         self.tablaSimbolos.add_simbolo(Simbolo(ctx.STRING().getText(), ctx.start.line, ctx.start.column, "STRING", self.tablaSimbolos.scope))
    
    #     if ctx.ASSIGN():
    #         for assign in ctx.ASSIGN():
    #             self.tablaSimbolos.add_simbolo(Simbolo(assign.getText(), ctx.start.line, ctx.start.column, "ASSIGN", self.tablaSimbolos.scope))
        
    #     # Continúa visitando las subexpresiones
    #     for subexpr_ctx in ctx.expr():
    #         self.visit(subexpr_ctx)

    def visitExpr(self, ctx: yalpParser.ExprContext):
        self.handle_context(ctx)

    def visitFormal(self, ctx: yalpParser.FormalContext):
        self.handle_context(ctx)

    def handle_context(self, ctx):
        for child_ctx in ctx.getChildren():
            if isinstance(child_ctx, TerminalNode):
                token = child_ctx.getSymbol()
                print("\nToken: ", ctx.getToken(token.type, 0))
                print("- start", ctx.getPayload().start)
                print("- end", ctx.getPayload())
                self.visitTerminal(child_ctx)
            else:
                self.handle_context(child_ctx)

    def visitTerminal(self, node: TerminalNode):
        token = node.getSymbol()
        token_type = self.lexer.symbolicNames[token.type]
        print("token_type:", token_type)
        #print("token_text:", token.text)
        #print("token_line", token.line)
        #print("token_column", token.column)
        self.tablaSimbolos.add_simbolo(Simbolo(token.text, token.line, token.column, token_type, self.tablaSimbolos.scope))





