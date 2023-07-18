from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from dist.yalpLexer import yalpLexer
from dist.yalpParser import yalpParser
from dist.yalpListener import yalpListener
from dist.yalpVisitor import yalpVisitor

TAMAÑO_MAXIMO_STRING = 100

class CustomLexer(yalpLexer):
    def __init__(self, input):
        super().__init__(input)

    def nextToken(self):

        token = super().nextToken()
        if token.type == yalpLexer.STRING:
            # verificar le tamaño del string
            if len(token.text) > TAMAÑO_MAXIMO_STRING:
                # EMULAR error sintactico para que no se detenga el programa
                token.type = yalpLexer.ERROR
                print(f"Error léxico en la posición {token.line}:{token.column} string {token.text} de tamaño mayor al permitido ({TAMAÑO_MAXIMO_STRING}).")

            # verificar si tiene un salto de linea escapado
            if token.text.count("\n") > 0:
                token.type = yalpLexer.ERROR
                print(f"Error léxico en la posición {token.line}:{token.column} string {token.text} con salto de linea no permitido.")
        
        elif token.type == yalpLexer.ERROR:
                print(f"Error léxico en la posición {token.line}:{token.column} token {token.text} no reconocido.")
    
        return token
        

class CustomParserErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        expected_tokens = recognizer.getExpectedTokens().toString(recognizer.literalNames, recognizer.symbolicNames)
        offending_token = offendingSymbol.text if offendingSymbol is not None else "no reconocido"
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
