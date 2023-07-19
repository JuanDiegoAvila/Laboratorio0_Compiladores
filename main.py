from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from dist.yalpLexer import yalpLexer
from dist.yalpParser import yalpParser
from dist.yalpListener import yalpListener
from dist.yalpVisitor import yalpVisitor
import pydot
from graphviz import Digraph, Graph
import os

TAMAÑO_MAXIMO_STRING = 100

def stringTreeToList(tree_string):
    new_word = ''
    words = []
    string_flag = False

    for i in tree_string:
        if string_flag==False:
            if i =='(':
                words.append(i)
                new_word = ''
            elif i == ' ':
                if new_word != '' and new_word!=' ':
                    words.append(new_word)
                new_word=''
            elif i == ')':
                if new_word != '' and new_word!=' ':
                    words.append(new_word)
                new_word=''
                words.append(i)
            elif i == '"':
                string_flag=True
                new_word=i
            else:
                new_word+=i
        else:
            if i == '"':
                string_flag=False
                new_word+=i
                words.append(new_word)
                new_word=''
            else: 
                new_word+=i
    return words


class Node:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []
        self.number = 0
    
    def addChild(self, child_node):
        self.children.append(child_node)
        
    def Traverse(self):
        stack = [self]
        while stack:
            lookat = stack.pop()
            print(lookat.name)
            if lookat.children:
                for i in lookat.children:
                    stack.append(i)
                    
    def Traverse2(self):
        print(" ")
        stack = [self]
        while stack:
            lookat = stack.pop()

            if lookat.children:
                names = [i.name for i in lookat.children]
                print(lookat.name, names)

                for i in lookat.children:
                    if i.children:
                        
                        stack.append(i)
    
    def showGraph(self):
        stack = [self]
        count = 0
        dot = Graph()
        
        dot.node(name=str(self.number)+' '+self.name, label=self.name)
        while stack:
            lookat = stack.pop()
            if lookat.children:
                for i in lookat.children:
                    count+=1
                    i.number = count
                    nombre_i = str(i.number)+' '+i.name
                    dot.node(name=nombre_i, label=i.name)
                    dot.edge((str(lookat.number)+' '+lookat.name), nombre_i)
                    stack.append(i)
        dot.render('tree', format='png')

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
        
        print(token_stream)

        tree = parser.program()
        tree_string = tree.toStringTree(recog=parser)
        print(tree_string)
        print(stringTreeToList(tree_string))
        arbol = self.createTree(tree_string)
        arbol.Traverse2()
        
        #Por si no funciona el arbol: os.system('antlr4-parse ./gramatica/yalp.g4 program -gui ./entrada.txt')
        
    def createTree2(self, tree_string):
        if not isinstance(tree_string, list):
            tree_string = stringTreeToList(tree_string)

        
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
                        root.addChild(Node(tree_string[i]))
                        root.addChild(self.createTree(tree_string[i:]))
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
