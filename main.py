from antlr4 import *
from dist.yalpLexer import yalpLexer
from dist.yalpParser import yalpParser
from dist.yalpListener import yalpListener
from dist.yalpVisitor import yalpVisitor

TAMAÑO_MAXIMO_STRING = 100

class CustomLexerErrorListener(DiagnosticErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print(f"Error léxico en la posición {line}:{column} token {msg[-3:]} no reconocido.")

class CustomParserErrorListener(DiagnosticErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        expected_tokens = e.getExpectedTokens().toString(recognizer.literalNames, recognizer.symbolicNames)
        offending_token = offendingSymbol.text if offendingSymbol is not None else "no reconocido"
        print(f"Error sintáctico en {line}:{column}, token '{offending_token}' no reconocido. Se esperaba uno de los siguientes tokens: {expected_tokens}.")

class Scanner (object):
    def __init__(self, input_file):
        with open(input_file, 'r') as file:
            self.input_text = file.read()
        
        self.input_stream = InputStream(self.input_text)
        self.lexer = yalpLexer(self.input_stream)
        
        self.lexer.removeErrorListeners()
        self.lexer.addErrorListener(CustomLexerErrorListener())

        self.stream = CommonTokenStream(self.lexer)
        self.stream.fill()

class Parser (object):
    def __init__(self):
        self.scanner = Scanner("error.txt")
        self.parseTokens()

    def parseTokens(self):
        stream = self.scanner.stream
        token_stream = stream

        parser = yalpParser(token_stream)

        parser.removeErrorListeners()
        parser.addErrorListener(CustomParserErrorListener())

        tree = parser.program()
        tree_string = tree.toStringTree(recog=parser)
        print(tree_string)

# Llamar a la función para el scanner
parser = Parser()
