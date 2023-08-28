from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from dist.yalpLexer import yalpLexer
from dist.yalpParser import yalpParser
from tree import *
from tablaSimbolos import *
#from semanticVisitor import SemanticVisitor
from PruebasCodigo.pruebaSemanticVisitor import SemanticVisitor

from treeVisitor import TreeVisitor
import interfaz as interfaz
# import tkinter as tk
# from tkinter import filedialog, Text, Menu, Scrollbar, font

TAMAÑO_MAXIMO_STRING = 100

ERRORS = False

class CustomLexer(yalpLexer):
    def __init__(self, input):
        super().__init__(input)
        self.errors = False
        self.global_terminal = get_global_terminal()
        self.tablaSimbolos = TablaSimbolos()
        self.scopes = 0
        
    def nextToken(self):

        token = super().nextToken()
        
        if token.type == yalpLexer.STRING:
            # verificar le tamaño del string
            if len(token.text) > TAMAÑO_MAXIMO_STRING:
                # EMULAR error sintactico para que no se detenga el programa
                token.type = yalpLexer.ERROR
                self.errors = True
                mensaje = f"Error léxico en la posición {token.line}:{token.column} string {token.text} de tamaño mayor al permitido ({TAMAÑO_MAXIMO_STRING})."
                custom_print(self.global_terminal, mensaje, is_error=True)

            # verificar si tiene un salto de linea escapado
            if token.text.count("\n") > 0:
                token.type = yalpLexer.ERROR
                self.errors = True
                mensaje = f"Error léxico en la posición {token.line}:{token.column} string {token.text} con salto de linea no permitido."
                custom_print(self.global_terminal, mensaje, is_error=True)
        elif token.type == yalpLexer.ERROR:
                self.errors = True
                mensaje = f"Error léxico en la posición {token.line}:{token.column} token {token.text} no reconocido."
                custom_print(self.global_terminal, mensaje, is_error=True)
        _token_t = yalpLexer.symbolicNames[token.type]
        # simbolo = Simbolo(token.text, token.line, token.column, _token_t, self.tablaSimbolos.scope)
        # self.tablaSimbolos.add_simbolo(simbolo)
        
        return token
        
class CustomParserErrorListener(ErrorListener):
    def __init__(self):
        self.errors = False
        self.global_terminal = get_global_terminal()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        expected_tokens = recognizer.getExpectedTokens().toString(recognizer.literalNames, recognizer.symbolicNames)
        offending_token = offendingSymbol.text if offendingSymbol is not None else "no reconocido"
        self.errors = True
        mensaje = f"Error sintáctico en {line}:{column}, token '{offending_token}' no reconocido. Se esperaba uno de los siguientes tokens: {expected_tokens}."
        custom_print(self.global_terminal, mensaje, is_error=True)

class Scanner (object):
    def __init__(self, input_file):
        with open(input_file, 'r') as file:
            self.input_text = file.read()
        
        self.input_stream = InputStream(self.input_text)
        self.lexer = CustomLexer(self.input_stream)
        self.stream = CommonTokenStream(self.lexer)
        self.stream.fill()

class Parser (object):
    def __init__(self, input_file):
        self.scanner = Scanner(input_file)
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
                
        #Por si funciona el arbol: 
        if self.scanner.lexer.errors == False and errorListener.errors == False:
            
            analisis_semantico(tree, self.scanner.lexer.tablaSimbolos, self.scanner.lexer)
       
def analisis_semantico(tree, tablaSimbolos, lexer):
    visitor = TreeVisitor(lexer)
    grafo = visitor.visitar(tree)
    visitor.visit(tree)

    if visitor.errors != []:
        for error in visitor.errors:
            terminal = get_global_terminal()
            custom_print(terminal, error, is_error=True)
        return

    # grafo.render('./grafos/grafo', view=True, format='png')
    tablaSimbolos.print_tabla()
    
    # ScopeVisualizer(tablaSimbolos).visualize()
    semanticVisitor = SemanticVisitor(lexer, tablaSimbolos)
    semanticVisitor.visit(tree) 

    if semanticVisitor.errors != []:
        for error in semanticVisitor.errors:
            terminal = get_global_terminal()
            custom_print(terminal, error, is_error=True)
        return




# Llamar a la función para el scanner
parser = Parser('./archivos/entrada5.txt')

# app = interfaz.Interfaz(Parser)
# app.mainloop()