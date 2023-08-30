from antlr4.tree.Tree import TerminalNodeImpl, TerminalNode
from antlr4.Token import CommonToken
from dist.yalpParser import yalpParser
from dist.yalpLexer import yalpLexer
from tablaSimbolos import *
from treeVisitor import TreeVisitor
from dist.yalpVisitor import yalpVisitor


class SemanticVisitor(yalpVisitor):
    
    def __init__(self, lexer, tablaSimbolos):
        super().__init__()
        self.lexer = lexer
        self.tablaSimbolos = tablaSimbolos
        self.scope_counter = 0
        self.errors = []

    def visit(self, ctx):
        return super().visit(ctx)

    def visitProgram(self, ctx: yalpParser.ProgramContext):
        self.scope_counter = 0
        for class_ctx in ctx.class_():
            self.visit(class_ctx)
    
    def visitClass(self, ctx: yalpParser.ClassContext):
        class_name = ctx.TYPE()[0].getText()

        self.tablaSimbolos.get_enterScope()
        hay_main = False

        for feature_ctx in ctx.feature():
            feature = self.visit(feature_ctx)

            # verificar si hay un metodo main en la clase Main
            if class_name == "Main" and feature == "main":
                hay_main = True

                # verificar que el metodo main no tenga parametros
                if feature_ctx.formal():
                    self.errors.append(f"No debe haber parametros en el metodo main")

        if not hay_main and "Main" == class_name:
            self.errors.append(f"No se encontro el metodo main dentro de la clase Main")

        self.tablaSimbolos.get_exitScope()

        return class_name

    def visitFeature(self, ctx: yalpParser.FeatureContext):
        token_type = "FUNCTION" if ctx.LPAR() else "ATTRIBUTE"

        feature_name = ctx.ID().getText()

        if token_type == "FUNCTION":
            self.tablaSimbolos.get_enterScope()
            
        if ctx.expr():
            self.visit(ctx.expr())
        
        for formal_ctx in ctx.formal():
            self.visit(formal_ctx)
            
        if token_type == "FUNCTION":
            self.tablaSimbolos.get_exitScope()

        return feature_name

    def visitExpr(self, ctx: yalpParser.ExprContext):
        
        if ctx.DOT():
            visited_dot = self.handle_context(ctx)
            for i in visited_dot:
                print(i)
                
            variable = visited_dot[0][0]
            function = visited_dot[2]
            
            #Si variable es un ID
            if isinstance(variable, CommonToken):
                token_type = self.lexer.symbolicNames[variable.type]
                print(token_type)
                if token_type=='ID':
                    simbolo = self.tablaSimbolos.get_scope_simbolo(variable.text)
                    #Verificamos si existe una variable con ese nombre en el scope
                    if not simbolo:
                        print(self.tablaSimbolos.current_scope.name)
                        linea = ctx.start.line
                        columna = ctx.start.column
                        message = f"Error semantico: La variable '{variable.text}' en la posicion '{linea}':'{columna}' no ha sido declarada."
                        if message not in self.errors:
                            self.errors.append(message)
                        return None
                    pass
                else:
                    pass
                    #Si no es de type token entonces buscamos en las clases nativas
                    #
            print("aaaa\n")

        if ctx.LET():
            self.tablaSimbolos.get_enterScope()
            
            visited_let = self.handle_context(ctx)

            self.tablaSimbolos.get_exitScope()

        elif ctx.IF():
            self.tablaSimbolos.get_enterScope()
            
            visited = self.handle_context(ctx)
            
            # if isinstance(visited[1], list):
            visited_if = visited[1][0]
            # else:
            #     visited_if = visited[1]

            if isinstance(visited_if, CommonToken):
                token_type = self.lexer.symbolicNames[visited_if.type]

                if token_type == "ID":
                    visited_if = self.tablaSimbolos.get_scope_simbolo(visited_if.text)

                    if not visited_if:
                        linea = visited_if.line
                        columna = visited_if.column
                        message = f"Error semantico: La variable '{visited_if.tipo_token}' en la posicion '{linea}':'{columna}' no ha sido declarada."
                        if message not in self.errors:
                            self.errors.append(message)
                        return None

                    else:
                        token_type = visited_if.tipo_token

                if token_type == "Boolean" or token_type == "TRUE" or token_type == "FALSE" or token_type == "Int" or token_type == "DIGIT":
                    argumento = ["Boolean"]
                
                else:

                    if isinstance(visited_if, Simbolo):
                        linea = visited_if.linea
                        columna = visited_if.columna
                    else:
                        linea = visited_if.line
                        columna = visited_if.column

                    message = f"Error semantico: La variable de tipo '{token_type}' en la posicion '{linea}':'{columna}' debe ser de tipo boolean."
                    if message not in self.errors:
                        self.errors.append(message)
                    return None
            
            else:
                if visited_if == "Boolean" or visited_if == "TRUE" or visited_if == "FALSE" or visited_if == "Int" or visited_if == "DIGIT":
                    argumento = ["Boolean"]
                    return argumento
                if visited_if == None:
                    return None
                
                else:
                    linea = ctx.start.line
                    columna = ctx.start.column
                    error = f'Error semantico: La variable de tipo {visited_if} no puede ser argumento del if {linea}:{columna}'
                    if error not in self.errors:
                        self.errors.append(error)
                    return None

            if ctx.ELSE():
                self.tablaSimbolos.get_enterScope()


                self.tablaSimbolos.get_exitScope()

            else:
                visited = self.handle_context(ctx)
            
            self.tablaSimbolos.get_exitScope()

        elif ctx.WHILE():
            scope_while = self.tablaSimbolos.get_exitScope()
            
            visited_while = self.handle_context(ctx)
            visited_while = visited_while[1][0]

            if isinstance(visited_while, CommonToken):
                token_type = self.lexer.symbolicNames[visited_while.type]

                if token_type == "ID":
                    visited_while = self.tablaSimbolos.get_scope_simbolo(visited_while.text)

                    if not visited_while:
                        linea = visited_while.line
                        columna = visited_while.column
                        message = f"Error semantico: La variable '{visited_while.tipo_token}' en la posicion '{linea}':'{columna}' no ha sido declarada."
                        if message not in self.errors:
                            self.errors.append(message)
                        return None

                    else:
                        token_type = visited_while.tipo_token

                if token_type == "Boolean" or token_type == "TRUE" or token_type == "FALSE" or token_type == "Int" or token_type == "DIGIT":
                    return ["Boolean"]
                
                else:

                    if isinstance(visited_while, Simbolo):
                        linea = visited_while.linea
                        columna = visited_while.columna
                    else:
                        linea = visited_while.line
                        columna = visited_while.column

                    message = f"Error semantico: La variable de tipo '{token_type}' en la posicion '{linea}':'{columna}' debe ser de tipo boolean."
                    if message not in self.errors:
                        self.errors.append(message)
                    return None
            
            else:
                if visited_while == "Boolean" or visited_while == "TRUE" or visited_while == "FALSE" or visited_while == "Int" or visited_while == "DIGIT":
                    return ["Boolean"]
                
                else:
                    linea = visited_while.line
                    columna = visited_while.column
                    message = f"Error semantico: La variable de tipo '{visited_while}' en la posicion '{linea}':'{columna}' debe ser de tipo boolean."
                    if message not in self.errors:
                        self.errors.append(message)
                    return None

        elif ctx.LOOP():
            visited = self.handle_context(ctx)

            print('loop', visited)

            
            self.tablaSimbolos.get_exitScope()
        
        elif ctx.LPAR() and not ctx.ID():
            
            visited = self.handle_context(ctx)
            compared = visited[1][0]

            if isinstance(compared, CommonToken):
                token_type = self.lexer.symbolicNames[compared.type]
                
                if token_type == "ID":
                    compared = self.tablaSimbolos.get_scope_simbolo(compared.text)

                    if not compared:
                        linea = compared.line
                        columna = compared.column
                        message = f"Error semantico: La variable '{compared.tipo_token}' en la posicion '{linea}':'{columna}' no ha sido declarada."
                        if message not in self.errors:
                            self.errors.append(message)
                        return None

                    else:
                        token_type = compared.tipo_token


                
                if token_type == "Boolean" or token_type == "TRUE" or token_type == "FALSE":
                    return ["Boolean"]
                
                elif token_type == "Int" or token_type == "DIGIT":
                    return ["Int"]
                
                elif token_type == "String" or token_type == "STRING":
                    return ["String"]
            
                else:
                    return [token_type]
            
            else:
                if isinstance(compared, list):
                    return compared
                
                return [compared]
            
        elif ctx.DIAC():

            visited = self.handle_context(ctx)
                    
            if isinstance(visited[1], str):
                if visited[1] == "Int" or visited[1] == "Boolean":
                    return ["Int"]
                else:
                    linea = ctx.start.line
                    columna = ctx.start.column
                    error = f'Error semantico: ~ no se puede operar con {visited[1]} en la posicion {linea}:{columna}'
                    if error not in self.errors:
                        self.errors.append(error)
                
            else:
                if isinstance(visited[1][0], str):
                    temp = visited[1][0]

                    if temp == "Int" or temp == "Boolean":
                        return ["Int"]
                    
                    else: 
                        
                        linea = ctx.start.line
                        columna = ctx.start.column
                        error = f'Error semantico: ~ no se puede operar con {temp} en la posicion {linea}:{columna}'
                        
                        if error not in self.errors:
                            self.errors.append(error)
                else:
                    
                    temp = visited[1][0].type
                    token_type = self.lexer.symbolicNames[temp]
                    
                    if token_type == "Int" or token_type == "DIGIT" or token_type == "Boolean" or token_type == "TRUE" or token_type == "FALSE":
                        return ["Int"]
                    
                    else:
                        linea = ctx.start.line
                        columna = ctx.start.column
                        error = f'Error semantico: ~ no se puede operar con {token_type} en la posicion {linea}:{columna}'
                        
                        if error not in self.errors:
                            self.errors.append(error)

        elif ctx.ID() and ctx.ASSIGN():
            visited = self.handle_context(ctx)
            id1 = visited[0]
            type1 = self.tablaSimbolos.get_scope_simbolo(id1.text)
            # print(self.tablaSimbolos.index_scopes)

            if not type1:
                linea = id1.line
                columna = id1.column
                message = f"Error semantico: La variable '{id1.text}' en la posicion '{linea}':'{columna}' no ha sido declarada."
                if message not in self.errors:
                    self.errors.append(message)
                return None
            else:
                type1 = type1.tipo_token

            type2 =  visited[2][0]
            
            if isinstance(type2, CommonToken):
                token_type = self.lexer.symbolicNames[type2.type]
                
                
                if token_type=="ID":
                    simbolo = self.tablaSimbolos.get_scope_simbolo(type2.text)
                    if simbolo:
                        type2 = simbolo.tipo_token
                    else:
                        linea = type2.line
                        columna = type2.column
                        message = f"Error semantico: La variable '{type2.text}' en la posicion '{linea}':'{columna}' no ha sido declarada."
                        if message not in self.errors:
                            self.errors.append(message)
                        type2 = "None"
                        
                elif token_type == "DIGIT" or token_type == "Int":
                    type2 = "Int"
                elif token_type=="TRUE" or token_type=="FALSE":
                    type2 = 'Boolean'
                elif token_type == "STRING" or token_type == "String":
                    type2 = "String"

            if type1!=type2:
                linea = id1.line
                columna = id1.column

                message = f"Error: Se está asignando un tipo {type2} a una variable de tipo {type1} en la posición {linea}:{columna}"
                if message not in self.errors:
                    self.errors.append(message)
                return None
            else:
                return type2
        
        elif ctx.LT() or ctx.RT() or ctx.LE() or ctx.RE() or ctx.EQUALS():
    
            visited_op = self.handle_context(ctx)
            operadores = []
            operandos = []
            
            for visit in visited_op:
                if isinstance(visit, list):
                    op = visit[0]

                    if isinstance(op, CommonToken):
                        token_type = self.lexer.symbolicNames[op.type]

                        if token_type == "ID":
                            simbolo = self.tablaSimbolos.get_scope_simbolo(op.text)
                            
                            if simbolo:
                                operandos.append(simbolo.tipo_token)
                            else:
                                linea = op.line
                                columna = op.column
                                message = f"Error semantico: La variable '{op.text}' en la posicion '{linea}':'{columna}' no ha sido declarada."

                                if message not in self.errors:
                                    self.errors.append(message)
                        
                        else:
                            operandos.append(token_type)
                    else:
                        operandos.append(op)

                else:
                    if isinstance(visit, str):
                        operadores.append(visit)
                    else:
                        token_type = self.lexer.symbolicNames[visit.type]
                        operadores.append(token_type)

            if len(operandos) < 2:
                return [None]

            tipo = self.checkCompare(ctx, operandos)
            return [tipo]

        elif ctx.PLUS() or ctx.TIMES() or ctx.MINUS() or ctx.DIVIDE():    

            visited_op = self.handle_context(ctx)
            operadores = []
            operandos = []
            
            for visit in visited_op:
                if isinstance(visit, list):
                    op = visit[0]

                    if isinstance(op, CommonToken):
                        token_type = self.lexer.symbolicNames[op.type]

                        if token_type == "ID":
                            simbolo = self.tablaSimbolos.get_scope_simbolo(op.text)
                            
                            if simbolo:
                                operandos.append(simbolo.tipo_token)
                            else:
                                linea = op.line
                                columna = op.column
                                message = f"Error semantico: La variable '{op.text}' en la posicion '{linea}':'{columna}' no ha sido declarada."

                                if message not in self.errors:
                                    self.errors.append(message)
                        
                        else:
                            operandos.append(token_type)
                    else:
                        operandos.append(op)

                else:
                    if isinstance(visit, str):
                        operadores.append(visit)
                    else:
                        token_type = self.lexer.symbolicNames[visit.type]
                        operadores.append(token_type)

            if len(operandos) < 2:
                return [None]
            

            tipo = self.checkValues(ctx, operandos)
            return [tipo]
        
        else:
            v = self.handle_context(ctx) 
            return v

    def checkCompare(self, ctx: yalpParser.ExprContext, visited:list):
        types = []

        for v in visited:
            if v == "DIGIT" or v == "Int":
                types.append("Int")
            elif v == "STRING" or v == "String":
                types.append("String")
            elif v == "TRUE" or v == "FALSE" or v == "Boolean":
                types.append("Boolean")
            else:
                types.append(v)
            if v == None:
                return None
        
        compare = ''
        se_puede = False
        bool = False
        for type in types:
            if compare == '':
                compare = type

            else:
                if type == compare:
                    se_puede = True
                if (type == "Int" and compare == "Boolean") or (type == "Boolean" and compare == "Int"):
                    se_puede = True
                    bool = True
        
        if se_puede:
            return "Boolean" 
        
        else:
            linea = ctx.start.line
            columna = ctx.start.column
            error = f'Error semantico: Operacion invalida entre {types[0]} y {types[1]} en la posicion {linea}:{columna}'
            if error not in self.errors:
                self.errors.append(error)

            return None

    def checkValues(self, ctx: yalpParser.ExprContext, visited:list):
        types = []
        for v in visited:
            if v == "DIGIT" or v == "Int":
                if "Int" not in types:
                    if "Boolean" in types:
                        types[0]="Int"
                    else:
                        types.append("Int")
            elif v == "STRING" or v == "String":
                if "String" not in types:
                    types.append("String")
            
            elif v == "TRUE" or v == "FALSE" or v == "Boolean":
                if "Boolean" not in types and "Int" not in types:
                    types.append("Boolean")

            if v == None:
                return None\
        
        #Solo ocurre si hay 2 tipos distintos en la lista
        if len (types) != 1:
            linea = ctx.start.line
            columna = ctx.start.column
            error = f'Error semantico: Operacion invalida entre {types[0]} y {types[1]} en la posicion {linea}:{columna}'
            if error not in self.errors:
                self.errors.append(error)

            return None
        return ''.join(types)        
    
    def handle_context(self, ctx, formal=False):
        visited = []
        for child_ctx in ctx.getChildren():
            if isinstance(child_ctx, TerminalNode):
                token = self.visitTerminal(child_ctx, formal)
                visited.append(token)
            
            else:
                v = self.visit(child_ctx)

                if v is not None:
                    visited.append(v)
                             
        return visited
        
    def visitTerminal(self, node: TerminalNode, formal=False):
        token = node.getSymbol()
        
        return token
