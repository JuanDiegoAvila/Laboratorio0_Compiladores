
from dist.yalpParser import yalpParser
from dist.yalpListener import yalpListener
from dist.yalpLexer import yalpLexer
from tablaSimbolos import Simbolo, TablaSimbolos
from antlr4 import TerminalNode

class SymbolTableVisitor(yalpListener):
    def __init__(self):
        self.tablaSimbolos = TablaSimbolos()
        self.current_scope = self.tablaSimbolos.scope

    def enterClass(self, ctx: yalpParser.ClassContext):
        for ctx_class in ctx.TYPE():
            class_name = ctx_class.getText()
            self.current_scope = self.tablaSimbolos.enter_scope(class_name)
            self.tablaSimbolos.add_simbolo(Simbolo(class_name, ctx.start.line, ctx.start.column, "CLASS", self.current_scope))

    def exitClass(self, ctx: yalpParser.ClassContext):
        self.tablaSimbolos.exit_scope()

    def enterFeature(self, ctx: yalpParser.FeatureContext):
        feature_name = ctx.ID().getText()
        token_type = "FUNCTION" if ctx.LPAR() else "ATTRIBUTE"
        self.tablaSimbolos.add_simbolo(Simbolo(feature_name, ctx.start.line, ctx.start.column, token_type, self.current_scope))

    # Aquí puedes agregar más métodos enter/exit para otros contextos

    def visitFormal(self, ctx: yalpParser.FormalContext):
        formal_name = ctx.ID().getText()
        self.tablaSimbolos.add_simbolo(Simbolo(formal_name, ctx.start.line, ctx.start.column, "FORMAL", self.current_scope))

    def visitExpr(self, ctx: yalpParser.ExprContext):
        self.handle_terminal_node(ctx.ID())
        self.handle_terminal_node(ctx.DIGIT())
        self.handle_terminal_node(ctx.STRING())
        self.handle_terminal_node(ctx.TRUE())
        self.handle_terminal_node(ctx.FALSE())

        type_node = ctx.TYPE()
        if type_node is not None:
            self.handle_terminal_node(type_node)

        for child in ctx.children:
            if isinstance(child, TerminalNode):
                self.handle_terminal_node(child)

        # ... (manejo de otras producciones de la gramática)

    def handle_terminal_node(self, node: TerminalNode):
        token = node.getSymbol()
        token_type = yalpLexer.symbolicNames[token.type]
        self.tablaSimbolos.add_simbolo(Simbolo(token.text, token.line, token.column, token_type, self.current_scope))