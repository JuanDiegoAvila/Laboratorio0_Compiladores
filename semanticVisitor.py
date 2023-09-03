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

        visited = []
        if ctx.expr():
            visited = self.visit(ctx.expr())

            if isinstance(visited, list):
                for v in visited:
                    if isinstance(v, CommonToken):
                        token_type = self.lexer.symbolicNames[v.type]


        if ctx.ASSIGN():
            original_type = ctx.TYPE().getText()
            assign = self.visit(ctx.expr())[0]

            if isinstance(assign, CommonToken):
                assign = self.lexer.symbolicNames[assign.type]

                if assign == "BOOLEAN":
                    assign = "Boolean"
                elif assign == "INT" or assign == "DIGIT":
                    assign = "Int"
                elif assign == "STRING":
                    assign = "String"
                elif assign == "ID":
                    assign = self.tablaSimbolos.get_scope_simbolo(assign.text)
                    assign = assign.tipo_token
                
            
            if assign != original_type:
                linea = ctx.start.line
                columna = ctx.start.column
                message = f"Error semántico: Se está asignando un tipo {assign} a una variable de tipo {original_type} en la posición {linea}:{columna}"
                if message not in self.errors:
                    self.errors.append(message)
        
        for formal_ctx in ctx.formal():
            self.visit(formal_ctx)
            
        if token_type == "FUNCTION":
            
            self.tablaSimbolos.get_exitScope()

        return feature_name

    def visitExpr(self, ctx: yalpParser.ExprContext):
        
        if ctx.IF():
            
            def getHerencia(type_symbol, herencia = []):
                if type_symbol=="Boolean": type_symbol="Bool"
                type_symbol_if = self.tablaSimbolos.get_scope_simbolo(type_symbol)
                scope_tipo = type_symbol_if.scope
                scope_tipo = scope_tipo.get_symbol_scope(type_symbol_if)
                hereda = scope_tipo[1]
                if hereda:
                    herencia.append(hereda)
                    return getHerencia(hereda, herencia)
                else:
                    if 'Object' not in herencia:
                        herencia.append('Object')
                    return herencia
            
            def checkHerencia(if_expr, else_expr):
                menor = min(if_expr, else_expr, key=len)
                if menor==if_expr:
                    mayor = else_expr
                else:
                    mayor = if_expr
                
                for i in menor:
                    if i in mayor:
                        return i
                return None
            self.tablaSimbolos.get_enterScope()

            visited = self.handle_context(ctx)
            visited_if = visited[1][0]
            if_expr = visited[3][0]
            else_expr = visited[5][0]
            

            

            
            if if_expr!=else_expr:
                herencia_if = getHerencia(if_expr, [if_expr])
                herencia_else = getHerencia(else_expr, [else_expr])
                mcst = checkHerencia(herencia_if, herencia_else) #Minimum common supertype                
            else:
                mcst = if_expr
                    
            # if ctx.ELSE():
            #     self.tablaSimbolos.get_enterScope()
            #     self.tablaSimbolos.get_exitScope()
        

            if isinstance(visited_if, CommonToken):
                token_type = self.lexer.symbolicNames[visited_if.type]

                if token_type == "ID":
                    visited_if = self.tablaSimbolos.get_scope_simbolo(visited_if.text)

                    if not visited_if:
                        linea = visited_if.line
                        columna = visited_if.column
                        message = f"Error semántico: La variable '{visited_if.tipo_token}' en la posición '{linea}':'{columna}' no ha sido declarada."
                        if message not in self.errors:
                            self.errors.append(message)

                        self.tablaSimbolos.get_exitScope()
                        return None

                    else:
                        token_type = visited_if.tipo_token

                if token_type == "Boolean" or token_type == "TRUE" or token_type == "FALSE" or token_type == "Int" or token_type == "DIGIT":
                    argumento = ["Boolean"]
                    herencia_if = []
                    herencia_else = []
                    # self.tablaSimbolos.get_exitScope()
                    # return argumento
                
                else:
                    if isinstance(visited_if, Simbolo):
                        linea = visited_if.linea
                        columna = visited_if.columna
                    else:
                        linea = visited_if.line
                        columna = visited_if.column

                    message = f"Error semántico: La variable de tipo '{token_type}' en la posición '{linea}':'{columna}' debe ser de tipo boolean."
                    if message not in self.errors:
                        self.errors.append(message)

                    # self.tablaSimbolos.get_exitScope()
                    # return None
            
            else:
                if visited_if == "Boolean" or visited_if == "TRUE" or visited_if == "FALSE" or visited_if == "Int" or visited_if == "DIGIT":
                    argumento = ["Boolean"]
                    self.tablaSimbolos.get_exitScope()
                    if if_expr !=else_expr:
                        herencia_if = []
                        herencia_else = []
                    
                    return [mcst]
                
                if visited_if == None:
                    self.tablaSimbolos.get_exitScope()
                    return None
                
                else:
                    linea = ctx.start.line
                    columna = ctx.start.column
                    error = f'Error semántico: La variable de tipo {visited_if} no puede ser argumento del if {linea}:{columna}'
                    if error not in self.errors:
                        self.errors.append(error)

                    self.tablaSimbolos.get_exitScope()
                    return None

            
            
            self.tablaSimbolos.get_exitScope()
            return mcst

        elif ctx.ELSE():
            self.tablaSimbolos.get_enterScope()

            visited = self.handle_context(ctx)

            self.tablaSimbolos.get_exitScope()

        elif ctx.WHILE():
            self.tablaSimbolos.get_enterScope()
            

            visited_while = self.handle_context(ctx)
            visited_while = visited_while[1][0]

            if isinstance(visited_while, CommonToken):
                token_type = self.lexer.symbolicNames[visited_while.type]

                if token_type == "ID":
                    visited_while = self.tablaSimbolos.get_scope_simbolo(visited_while.text)

                    if not visited_while:
                        linea = ctx.start.line
                        columna = ctx.start.column
                        message = f"Error semántico: La variable '{visited_while.tipo_token}' en la posición '{linea}':'{columna}' no ha sido declarada."
                        if message not in self.errors:
                            self.errors.append(message)
                        
                        self.tablaSimbolos.get_exitScope()
                        return None

                    else:
                        token_type = visited_while.tipo_token

                if token_type == "Boolean" or token_type == "TRUE" or token_type == "FALSE" or token_type == "Int" or token_type == "DIGIT":
                    self.tablaSimbolos.get_exitScope()
                    return ["Object"]
                
                else:

                    if isinstance(visited_while, Simbolo):
                        linea = visited_while.linea
                        columna = visited_while.columna
                    else:
                        linea = ctx.start.line
                        columna = ctx.start.column

                    message = f"Error semántico: La variable de tipo '{token_type}' en la posición '{linea}':'{columna}' debe ser de tipo boolean."
                    if message not in self.errors:
                        self.errors.append(message)
                    self.tablaSimbolos.get_exitScope()
                    return None
            
            else:
                if visited_while == "Boolean" or visited_while == "TRUE" or visited_while == "FALSE" or visited_while == "Int" or visited_while == "DIGIT":
                    self.tablaSimbolos.get_exitScope()
                    return ["Object"]
                
                else:
                    linea = ctx.start.line
                    columna = ctx.start.column
                    message = f"Error semántico: La variable de tipo '{visited_while}' en la posición '{linea}':'{columna}' debe ser de tipo boolean."
                    if message not in self.errors:
                        self.errors.append(message)
                    self.tablaSimbolos.get_exitScope()
                    return None

        elif ctx.LET():
            
            self.tablaSimbolos.get_enterScope()
            
            visited_let = self.handle_context(ctx)
            tipo = visited_let[-1][0]
            
            if isinstance(tipo, CommonToken):
                token_type = self.lexer.symbolicNames[tipo.type]
                if token_type == "ID":
                    simbolo = self.tablaSimbolos.get_scope_simbolo(tipo.text)
                    
                    if simbolo:
                        token_type = simbolo.tipo_token
                        return [token_type]
                    else:
                        linea = tipo.line
                        columna = tipo.column
                        message = f"Error semántico: La variable '{tipo.text}' en la posición '{linea}':'{columna}' no ha sido declarada."

                        if message not in self.errors:
                            self.errors.append(message)
                        return [None]
                else:
                    if token_type == "DIGIT" or token_type == "Int":
                        return ['Int']
                    elif token_type == "STRING" or token_type == "String":
                        return ['String']
                    elif token_type == "TRUE" or token_type == "FALSE" or token_type == "Boolean" or token_type == 'Bool':
                        return ['Boolean']
                    else:
                        return [None]
            else:
                return [tipo]

            type_variable = self.tablaSimbolos.get_scope_simbolo(variable.text)
            
            self.tablaSimbolos.get_exitScope()

        elif ctx.DOT():

            visited_dot = self.handle_context(ctx)
            inherit_visited = []
            
            def getInputTypes(args):
                arg_types = []
                for arg in args:
                    if isinstance(arg, list):#Es un argumento y no una comma
                        argumento = arg[0]
                        token_type = self.lexer.symbolicNames[argumento.type]
                        if token_type=="ID":
                            simbolo = self.tablaSimbolos.get_scope_simbolo(argumento.text)
                            if not simbolo:
                                linea = ctx.start.line
                                columna = ctx.start.column
                                message = f"Error semantico: La variable '{argumento.text}' en la posicion '{linea}':'{columna}' no ha sido declarada."
                                if message not in self.errors:
                                    self.errors.append(message)
                                return None
                            else:
                                token_type = simbolo.tipo_token
                                arg_types.append(token_type)
                        else:
                            if token_type=="TRUE" or token_type=="FALSE" or token_type =="Boolean":
                                arg_types.append("Boolean")
                            elif token_type=="DIGIT" or token_type=="Int":
                                arg_types.append("Int")
                            elif token_type=="String" or token_type =="STRING":
                                arg_types.append("String")
                            elif token_type=="ERROR":
                                arg_types.append("Indefinido")
                            else:
                                arg_types.append(None)
                return arg_types
            
            def GetFunc(scope, func, inherits):
                
                
                if func in scope.symbols:
                    tipo_func = scope.symbols[func].tipo_token
                    scope_func = scope.get_symbol_scope(scope.symbols[func])
                    simbolos = scope_func[0].symbols
                    symbol_types = [i.tipo_token for i in simbolos.values()]
                    return (True, tipo_func, symbol_types)
                elif inherits:
                    if inherits not in inherit_visited:
                        inherit_visited.append(inherits)
                        type_symbol = self.tablaSimbolos.get_scope_simbolo(inherits)
                        scope_tipo = type_symbol.scope
                        scope_tipo = scope_tipo.get_symbol_scope(type_symbol)
                        return GetFunc(scope_tipo[0], func, scope_tipo[1])
                    else:
                        type_symbol = self.tablaSimbolos.get_scope_simbolo(inherits)
                        message = f'Semantic Error semántico: Hay una herencia recursiva en la clase {inherits}, {type_symbol.line}:{type_symbol.column}'
                        self.errors.append(message)
                        return(False, None, None)
                else:
                    return (False, None, None)    
                                
            variable = visited_dot[0][0]
            function = visited_dot[2]
            #Si variable es un ID
            if isinstance(variable, CommonToken):
                token_type = self.lexer.symbolicNames[variable.type]
                if token_type=='ID':
                    simbolo = self.tablaSimbolos.get_scope_simbolo(variable.text)
                    
                    #Verificamos si existe una variable con ese nombre en el scope
                    if not simbolo:
                        linea = ctx.start.line
                        columna = ctx.start.column
                        message = f"Error semántico: La variable '{variable.text}' en la posición '{linea}':'{columna}' no ha sido declarada."
                        if message not in self.errors:
                            self.errors.append(message)
                        return None
                    else:
                        tipo = simbolo.tipo_token #Me da el tipo del token
                        type_symbol = self.tablaSimbolos.get_scope_simbolo(tipo)
                        inherit_visited.append(type_symbol.lexema)
                        scope_tipo = type_symbol.scope
                        scope_tipo = scope_tipo.get_symbol_scope(type_symbol)
                        found, tipo_func, arg_tipos = GetFunc(scope_tipo[0], function.text, scope_tipo[1])
                        if not found:
                            linea = ctx.start.line
                            columna = ctx.start.column
                            message = f'Error semántico: Método {function.text} no se encontró para la clase {type_symbol.lexema}, {linea}:{columna}'
                            self.errors.append(message)
                            return [None]
                        else:
                            input_args = visited_dot[4:-1]
                            input_types = getInputTypes(input_args)
                            if not input_types:
                                return [None]
                            
                            
                            if len(input_types) != len(arg_tipos):
                                linea = ctx.start.line
                                columna = ctx.start.column
                                message = f"Error semantico: La función '{function.text}'  esperaba {len(arg_tipos)} argumentos, {len(input_types)} fueron pasados. {linea}:{columna}"
                                if message not in self.errors:
                                    self.errors.append(message)
                                return [None]
                            else:
                                for i in range(len(arg_tipos)):
                                    if arg_tipos[i]!=input_types[i]:
                                        linea = ctx.start.line
                                        columna = ctx.start.column
                                        message = f"Error semantico: La función '{function.text}'  esperaba un argumento de tipo '{arg_tipos[i]}', uno de tipo '{input_types[i]}' fue pasado. {linea}:{columna}"
                                        if message not in self.errors:
                                            self.errors.append(message)
                                        return [None]
                            return [tipo_func]
                
                else:
                    return [None]            
                #else:
                #    token_type = self.lexer.symbolicNames[variable.type]
                #    if token_type == "Boolean" or token_type == "TRUE" or token_type == "FALSE":
                #        tipo = "Boolean"
                #        type_symbol = self.tablaSimbolos.get_scope_simbolo(tipo)
                #        scope_tipo = type_symbol.scope
        
        elif ctx.ID() and ctx.LPAR():
            visited_func = self.handle_context(ctx)
            
            
            func_name = visited_func[0]
            
            def getInputTypes(args):
                arg_types = []
                for arg in args:
                    if isinstance(arg, list):#Es un argumento y no una comma
                        argumento = arg[0]
                        token_type = self.lexer.symbolicNames[argumento.type]
                        if token_type=="ID":
                            simbolo = self.tablaSimbolos.get_scope_simbolo(argumento.text)
                            if not simbolo:
                                linea = ctx.start.line
                                columna = ctx.start.column
                                message = f"Error semantico: La variable '{argumento.text}' en la posicion '{linea}':'{columna}' no ha sido declarada."
                                if message not in self.errors:
                                    self.errors.append(message)
                                return None
                            else:
                                token_type = simbolo.tipo_token
                                arg_types.append(token_type)
                        else:
                            if token_type=="TRUE" or token_type=="FALSE" or token_type =="Boolean":
                                arg_types.append("Boolean")
                            elif token_type=="DIGIT" or token_type=="Int":
                                arg_types.append("Int")
                            elif token_type=="String":
                                arg_types.append("String")
                            elif token_type=="ERROR":
                                arg_types.append("Indefinido")
                            else:
                                arg_types.append(None)
                return arg_types

            def getArgTypes(scope):
                items = scope[0].symbols.values()
                
                types = [value.tipo_token for value in items]
                return types          
                        
            
            token_type = self.lexer.symbolicNames[func_name.type]
            if token_type=='ID':
                simbolo = self.tablaSimbolos.get_scope_simbolo(func_name.text)
                
                #Verificamos si existe una funcion con ese nombre en el scope
                if not simbolo:
                    linea = ctx.start.line
                    columna = ctx.start.column
                    message = f"Error semantico: La función '{func_name.text}' en la posicion '{linea}':'{columna}' no ha sido declarada."
                    if message not in self.errors:
                        self.errors.append(message)
                    return None
                else:
                    scope_tipo = simbolo.scope
                    scope_tipo = scope_tipo.get_symbol_scope(simbolo)
                    func_args = visited_func[2:-1]
                    input_types = getInputTypes(func_args)
                    argTypes = getArgTypes(scope_tipo)
                    
                    if not input_types:
                        return [None]
                    
                    if len(argTypes)!=len(input_types):
                        linea = ctx.start.line
                        columna = ctx.start.column
                        message = f"Error semantico: La función '{func_name.text}'  esperaba {len(argTypes)} argumentos, {len(input_types)} fueron pasados. {linea}:{columna}"
                        if message not in self.errors:
                            self.errors.append(message)
                        return [None]
                    else:
                        for i in range(len(argTypes)):
                            if argTypes[i]!=input_types[i]:
                                linea = ctx.start.line
                                columna = ctx.start.column
                                message = f"Error semantico: La función '{func_name.text}'  esperaba un argumento de tipo '{argTypes[i]}', uno de tipo '{input_types[i]}' fue pasado. {linea}:{columna}"
                                if message not in self.errors:
                                    self.errors.append(message)
                                return [None]
                    return [simbolo.tipo_token]
            else:
                return [None]
                    
                    #De primero revisar si los argumentos metidos en la llamada hacen match de tipo y de cantidad a los de la función

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
                        message = f"Error semántico: La variable '{compared.tipo_token}' en la posición '{linea}':'{columna}' no ha sido declarada."
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
                    error = f'Error semántico: ~ no se puede operar con {visited[1]} en la posición {linea}:{columna}'
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
                        error = f'Error semántico: ~ no se puede operar con {temp} en la posición {linea}:{columna}'
                        
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
                        error = f'Error semántico: ~ no se puede operar con {token_type} en la posición {linea}:{columna}'
                        
                        if error not in self.errors:
                            self.errors.append(error)

        elif ctx.ID() and ctx.ASSIGN() and not ctx.LET():
            visited = self.handle_context(ctx)
            
            id1 = visited[0]
            type1 = self.tablaSimbolos.get_scope_simbolo(id1.text)

            # if isinstance(id1, CommonToken) and id1.type == yalpLexer.LET:
            #     id1 = visited[1]
            #     print(visited)

            if not type1:
                linea = id1.line
                columna = id1.column
                message = f"Error semántico: La variable '{id1.text}' en la posición '{linea}':'{columna}' no ha sido declarada."
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
                        message = f"Error semántico: La variable '{type2.text}' en la posición '{linea}':'{columna}' no ha sido declarada."
                        if message not in self.errors:
                            self.errors.append(message)
                        type2 = "None"
                        
                elif token_type == "DIGIT" or token_type == "Int":
                    type2 = "Int"
                elif token_type=="TRUE" or token_type=="FALSE":
                    type2 = 'Boolean'
                elif token_type == "STRING" or token_type == "String":
                    type2 = "String"
                elif token_type == "ERROR":
                    type2 = "Indefinido"

            if type1!=type2:
                linea = id1.line
                columna = id1.column

                message = f"Error semántico: Se está asignando un tipo {type2} a una variable de tipo {type1} en la posición {linea}:{columna}"
                if message not in self.errors:
                    self.errors.append(message)
                return None
            else:
                return [type2]
        
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
                                message = f"Error semántico: La variable '{op.text}' en la posición '{linea}':'{columna}' no ha sido declarada."

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
                                message = f"Error semántico: La variable '{op.text}' en la posición '{linea}':'{columna}' no ha sido declarada."

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
        
        elif ctx.LBRACE() and ctx.RBRACE():
            visited = self.handle_context(ctx)
            expressions = [i for i in visited if isinstance(i, list)]
            
            return_expr = expressions[-1][0]
            
            if isinstance(return_expr, CommonToken):
                token_type = self.lexer.symbolicNames[return_expr.type]
                if token_type == "ID":
                    simbolo = self.tablaSimbolos.get_scope_simbolo(return_expr.text)
                    
                    if simbolo:
                        token_type = simbolo.tipo_token
                        return [token_type]
                    else:
                        linea = return_expr.line
                        columna = return_expr.column
                        message = f"Error semántico: La variable '{return_expr.text}' en la posición '{linea}':'{columna}' no ha sido declarada."

                        if message not in self.errors:
                            self.errors.append(message)
                        return [None]
                else:
                    if token_type == "DIGIT" or token_type == "Int":
                        return ['Int']
                    elif token_type == "STRING" or token_type == "String":
                        return ['String']
                    elif token_type == "TRUE" or token_type == "FALSE" or token_type == "Boolean" or token_type == 'Bool':
                        return ['Boolean']
                    else:
                        return [None]

            else:
                return [return_expr]

            
        elif ctx.ISVOID():
            
            visited = self.handle_context(ctx)
            expresion = visited[1][0]

            if isinstance(expresion, CommonToken):
                token_type = self.lexer.symbolicNames[expresion.type]

                if token_type == "ID":
                    simbolo = self.tablaSimbolos.get_scope_simbolo(expresion.text)
                    
                    if simbolo:
                        tipo = simbolo.tipo_token
                    else:
                        linea = expresion.line
                        columna = expresion.column
                        message = f"Error semántico: La variable '{expresion.text}' en la posición '{linea}':'{columna}' no ha sido declarada."

                        if message not in self.errors:
                            self.errors.append(message)
                        tipo = None

                else:
                    tipo = token_type
            else:
                tipo = expresion

            if tipo in ["DIGIT", "Int", "String", "STRING"]:

                return ["Boolean"]
            else:
                linea = ctx.start.line
                columna = ctx.start.column
                error = f'Error semántico: isvoid no se puede operar con {tipo} en la posición {linea}:{columna}'
                if error not in self.errors:
                    self.errors.append(error)

                return [None]
            # expr_type = self.tablaSimbolos.get_scope_simbolo(expresion.text)
            
        elif ctx.NEW():
            
            visited = self.handle_context(ctx)
            type = visited[1].text
            type_symbol = self.tablaSimbolos.get_scope_simbolo(type)

            if not type_symbol:
                linea = ctx.start.line
                columna = ctx.start.column
                message = f"Error semántico: La clase '{type}' en la posición '{linea}':'{columna}' no ha sido declarada."
                if message not in self.errors:
                    self.errors.append(message)
                return [None]
            
            return [type]
       
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
            error = f'Error semántico: Operación invalida entre {types[0]} y {types[1]} en la posición {linea}:{columna}'
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

            elif v == "ERROR":
                types.append("Indefinido")

            if v == None:
                return None
        
        #Solo ocurre si hay 2 tipos distintos en la lista
        if len (types) != 1:
            linea = ctx.start.line
            columna = ctx.start.column
            error = f'Error semántico: Operación invalida entre {types[0]} y {types[1]} en la posición {linea}:{columna}'
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
