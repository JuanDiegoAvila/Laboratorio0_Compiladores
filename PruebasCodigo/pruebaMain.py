from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from dist.yalpLexer import yalpLexer
from dist.yalpParser import yalpParser
from dist.yalpListener import yalpListener
from dist.yalpVisitor import yalpVisitor
import pydot
from graphviz import Digraph, Graph
import os
from tree import *
from tablaSimbolos import *

TAMAÑO_MAXIMO_STRING = 100

ERRORS = False

class CustomLexer(yalpLexer):
    def __init__(self, input):
        super().__init__(input)
        self.errors = False
        self.tablaSimbolos = TablaSimbolos()

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

        tipo = yalpLexer.symbolicNames[token.type]
        self.tablaSimbolos.add_simbolo(token.text, token.line, token.column, tipo)
        
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

        print(self.scanner.lexer.tablaSimbolos.print_tabla())

    def Tree(self):
        os.system('antlr4-parse ./gramatica/yalp.g4 program -gui ./entrada.txt')
    
    def parseTokens(self):
        stream = self.scanner.stream
        token_stream = stream

        parser = yalpParser(token_stream)

        parser.removeErrorListeners()

        errorListener = CustomParserErrorListener()
        parser.addErrorListener(errorListener)
        

        tree = parser.program()
        
        tree_string = tree.toStringTree(recog=parser)
        #print(tree_string)
        #print(stringTreeToList(tree_string))
        #arbol = self.createTree2(tree_string)
#
        #arbol = self.createTree(tree_string)
        #arbol.Traverse2()
        
        
        #Por si no funciona el arbol: 
        if self.scanner.lexer.errors == False and errorListener.errors == False:
            self.Tree()
        
    def createTree2(self, tree_string):
        if not isinstance(tree_string, list):
            tree_string = stringTreeToList(tree_string)
            
        name_rules = [ "program", "class", "feature", "formal", "expr" ]
        root = None
        par_stack = []
        
        while tree_string:
            lookat = tree_string.pop(0)
            if lookat == '(':
                if tree_string[0] in name_rules:
                    #De primero, meter tree_string a la lista
                    #Si si existe algo en la root 
                    if tree_string[0]=='program':
                        root = Node(name=tree_string[0])
                        tree_string.pop(0)
                        continue
                    else:
                        par_stack.append(lookat)
                        child = tree_string.pop(0)
                        new_string = lookat+child+tree_string
                        root.addChild(self.createTree2(tree_string))
                else:
                    par_stack.append(lookat)
            

    
        
    def createTree(self, tree_string):
        if not isinstance(tree_string, list):
            tree_string = stringTreeToList(tree_string)
        
        par_stack = [tree_string.pop(0)]
        root = Node(tree_string.pop(0))
        name_rules = [ "program", "class", "feature", "formal", "expr" ]
        
        continue_flag = True

        #Revisar donde se cierran los parentesis
        while par_stack:
            
            for i in range(len(tree_string)):
                #Si el parentesis esta asociado con un rule_name
                if tree_string[i]=='(' and tree_string[i+1] in name_rules:
                    if continue_flag:
                        temp_pstack = []
                        index = 0
                        for j in range(len(tree_string[i:])):
                            if tree_string[j]=='(':
                                temp_pstack.append(tree_string[j])
                            elif tree_string[j]==')':
                                temp_pstack.pop()
                            if len(temp_pstack)==0:
                                index = j
                                break
                            
                        root.addChild(Node(tree_string[i]))
                        root.addChild(self.createTree(tree_string[i:index+1]))
                        par_stack.append(tree_string[i])
                        continue_flag = False
                        
                elif tree_string[i]==')':

                    par_stack.pop()
                    if len(par_stack)==0:
                        continue_flag=True
                        break
                    else:
                        if continue_flag==False or tree_string[i-1]=='(':
                            root.addChild(Node(tree_string[i]))
                            if '}' in tree_string[i:] and '{' in tree_string[:i] and root.name!='program':
                                root.addChild(Node('}'))
                                

                else:
                    if continue_flag:
                        if tree_string[i]=='(':
                            root.addChild(Node(tree_string[i]))
                            par_stack.append(tree_string[i])
                        else:
                            root.addChild(Node(tree_string[i]))
            
        return root

            
            
                
                

# Llamar a la función para el scanner
parser = Parser()
