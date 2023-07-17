from antlr4 import *
from dist.yalpLexer import yalpLexer
from dist.yalpParser import yalpParser
from dist.yalpListener import yalpListener
from dist.yalpVisitor import yalpVisitor

TAMAÑO_MAXIMO_STRING = 100

def scanner(input_file):
    # Leer el archivo de entrada
    with open(input_file, 'r') as file:
        input_text = file.read()

    input_stream = InputStream(input_text)
    lexer = yalpLexer(input_stream)

    stream = CommonTokenStream(lexer)
    stream.fill()

    # Obtener los tokens
    token = lexer.nextToken()
    reconocidos = []

    # Imprimir los tokens
    while token.type != Token.EOF:
        if token.type == lexer.ERROR:
            reconocidos.append(('ERROR', [f"Error léxico en la línea {token.line}:{token.column} - {token.text}", token.text]))
        elif token.type == lexer.STRING:
            text = token.text[1:-1]
            # si el tamaño del string es mayor que el establecido reportar como error
            if len(token.text) > TAMAÑO_MAXIMO_STRING:
                reconocidos.append(('ERROR', [f"El string: [ {token.text} ] supera el tamaño máximo de {TAMAÑO_MAXIMO_STRING}", token.text]))
            # PENDIENTE
            if '\n' in text and not text.endswith('\\n'):
                reconocidos.append(('ERROR', [f"El string: [ {token.text} ] contiene un carácter de nueva línea no escapado.", token.text]))
            else:
                reconocidos.append((lexer.symbolicNames[token.type], token.text))
        else:
            reconocidos.append((lexer.symbolicNames[token.type], token.text)) 

        token = lexer.nextToken()

    return reconocidos, stream


def parse(tokens_reconocidos, stream):

    token_stream = stream

    error = False

    for token in tokens_reconocidos:
        if token[0] == 'ERROR':
            print(token[1][0])
            error = True

    if error:
        print("Se encontraron errores léxicos, no se procederá con el análisis sintáctico.")
        return
    
    # token_stream = CommonTokenStream(yalpLexer(None))
    # token_stream.tokens = tokens_reconocidos
    # token_stream = token_stream.fill()

    # a partir de los tokens recibidos en el lexer, crear lista common_tokens para asignar el token stream
    parser = yalpParser(token_stream)
    
    tree = parser.program()

    print(tree.toStringTree(recog=parser))

    

    # 
    # token_stream.tokens = common_tokens

    


# Archivo de entrada a analizar
archivo_entrada = "entrada.txt"

# Llamar a la función para el scanner
tokens_reconocidos, stream = scanner(archivo_entrada)

# Llamar a la función para el parser
parse(tokens_reconocidos, stream)
