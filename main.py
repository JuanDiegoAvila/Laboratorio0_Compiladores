from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from dist.yalpLexer import yalpLexer
from dist.yalpParser import yalpParser
from antlr4 import ParseTreeWalker
from treeListener import *
from dist.yalpListener import yalpListener
from dist.yalpVisitor import yalpVisitor
import pydot
from graphviz import Digraph, Graph
import os
from tree import *
from tablaSimbolos import *
from treeVisitor import TreeVisitor

TAMAÑO_MAXIMO_STRING = 100

ERRORS = False

class CustomLexer(yalpLexer):
    def __init__(self, input):
        super().__init__(input)
        self.errors = False
        self.tablaSimbolos = TablaSimbolos()
        self.scopes = 0

    
    def enterScope(self):
        self.scopes += 1
        self.tablaSimbolos.scope += 1

    def exitScope(self):
        self.scopes -= 1
        self.tablaSimbolos.scope -= 1
        
    def nextToken(self):

        token = super().nextToken()
        
        if token.type == yalpLexer.STRING:
            # verificar le tamaño del string
            if len(token.text) > TAMAÑO_MAXIMO_STRING:
                # EMULAR error sintactico para que no se detenga el programa
                token.type = yalpLexer.ERROR
                self.errors = True
                print(f"Error léxico en la posición {token.line}:{token.column} string {token.text} de tamaño mayor al permitido ({TAMAÑO_MAXIMO_STRING}).")

            # verificar si tiene un salto de linea escapado
            if token.text.count("\n") > 0:
                token.type = yalpLexer.ERROR
                self.errors = True
                print(f"Error léxico en la posición {token.line}:{token.column} string {token.text} con salto de linea no permitido.")
        
        elif token.type == yalpLexer.ERROR:
                self.errors = True
                print(f"Error léxico en la posición {token.line}:{token.column} token {token.text} no reconocido.")

        _token_t = yalpLexer.symbolicNames[token.type]
        # simbolo = Simbolo(token.text, token.line, token.column, _token_t, self.tablaSimbolos.scope)
        # self.tablaSimbolos.add_simbolo(simbolo)
        
        return token
        
class CustomParserErrorListener(ErrorListener):
    def __init__(self):
        self.errors = False

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        expected_tokens = recognizer.getExpectedTokens().toString(recognizer.literalNames, recognizer.symbolicNames)
        offending_token = offendingSymbol.text if offendingSymbol is not None else "no reconocido"
        self.errors = True
        print(f"Error sintáctico en {line}:{column}, token '{offending_token}' no reconocido. Se esperaba uno de los siguientes tokens: {expected_tokens}.")

class Scanner (object):
    def __init__(self, input_file):
        with open(input_file, 'r') as file:
            self.input_text = file.read()
        
        self.input_stream = InputStream(self.input_text)
        self.lexer = CustomLexer(self.input_stream)
        self.stream = CommonTokenStream(self.lexer)
        self.stream.fill()

class Parser (object):
    def __init__(self):
        self.scanner = Scanner("entrada.txt")
        self.parseTokens()

    # def Tree(self):
    #     os.system('antlr4-parse ./gramatica/yalp.g4 program -gui ./entrada.txt')
    
    def parseTokens(self):
        stream = self.scanner.stream
        token_stream = stream

        parser = yalpParser(token_stream)

        parser.removeErrorListeners()

        errorListener = CustomParserErrorListener()
        parser.addErrorListener(errorListener)
        

        tree = parser.program()
                
        #Por si no funciona el arbol: 
        if self.scanner.lexer.errors == False and errorListener.errors == False:
            visitor = TreeVisitor(self.scanner.lexer)
            grafo = visitor.visitar(tree)
            visitor.visit(tree)
            # symbol_table_visitor = SymbolTableVisitor()
            # walker = ParseTreeWalker()
            # walker.walk(symbol_table_visitor, tree)

            # grafo.render('grafo', view=True, format='png')

            print(self.scanner.lexer.tablaSimbolos.print_tabla())

                

# Llamar a la función para el scanner
parser = Parser()
