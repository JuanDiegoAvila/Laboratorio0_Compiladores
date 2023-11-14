from antlr4.tree.Tree import TerminalNode
from graphviz import Digraph
from antlr4.Token import CommonToken
from dist.yalpParser import yalpParser
from dist.yalpLexer import yalpLexer
from dist.yalpVisitor import yalpVisitor
from tablaSimbolos import *
from cuadruplas import *
from StackMemory import Stack

class codigoVisitor(yalpVisitor):
    def __init__(self, lexer):
        super().__init__()
        self.lexer = lexer
        self.tablaSimbolos = lexer.tablaSimbolos
        self.graph = Digraph()
        self.id = 0
        self.scope_counter = 0
        self.errors = []
        self.nativas = False
        self.cuadruplas = []
        self.labels = 0
        self.stack = False
        self.heap = False
        self.in_main = False
        self.actual_class = None
        self.stack_created = False

    def getLabel(self):
        self.labels += 1
        return self.labels

    def visit(self, ctx):
        return super().visit(ctx)
    
    def toPostfix(self, expression):
        precedence = {
            '~': 1,
            '*': 2,
            '/': 3,
            '+': 4,
            '-': 5,
            '<': 6,
            '<=': 7,
            '>': 8,
            '>=': 9,
            '=': 10
        }
        
        # Helper function to split the expression into tokens
        def tokenize(expr):
            tokens = []
            i = 0
            while i < len(expr):
                if expr[i] in ['<', '>', '='] and i + 1 < len(expr) and expr[i+1] == '=':
                    tokens.append(expr[i:i+2])
                    i += 2
                else:
                    tokens.append(expr[i])
                    i += 1
            return tokens
        
        # Convert expression into list of tokens
        tokens = tokenize(expression)

        # Initialize an empty stack and an empty output list
        stack = []
        output = []

        for token in tokens:
            if isinstance(token, Cuadrupla):
                output.append(token)

            elif token.isnumeric() or token.isalpha() or token=='""':  # Operand
                output.append(token)

            elif token in precedence:  # Operator
                while stack and stack[-1] in precedence and precedence[token] >= precedence[stack[-1]]:
                    output.append(stack.pop())
                stack.append(token)

            elif token == '(':  # Left parenthesis
                stack.append(token)
            elif token == ')':  # Right parenthesis
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()

        # Pop any remaining operators from the stack
        while stack:
            output.append(stack.pop())

        return output

    def visitProgram(self, ctx: yalpParser.ProgramContext):
        self.tablaSimbolos.current_scope = self.tablaSimbolos.current_scope.exit()
        self.tablaSimbolos.index_scopes = 0
        
        self.scope_counter = 0
        for class_ctx in ctx.class_():
            self.visit(class_ctx)

    def visitClass(self, ctx: yalpParser.ClassContext):
        self.heap = True
        
        def getSymbolClass(func_symbol):
            class_scope = func_symbol.scope
            global_scope = class_scope.parent
            index = global_scope.children.index(class_scope)
            classes = list(global_scope.symbols.keys())
            class_name = classes[index]
            return class_name
            

        class_name = ctx.TYPE()[0].getText()
        self.actual_class = class_name

        if class_name == "Main":
            self.in_main = True

        hereda = self.tablaSimbolos.get_simbolo(class_name).hereda
        self.tablaSimbolos.get_enterScope()
            
        self.cuadruplas.append(create_class_label(class_name, hereda))

        
        for feature_ctx in ctx.feature():
            # print(feature_ctx.getText())
            v = self.visit(feature_ctx)
            func_symbol = self.tablaSimbolos.get_simbolo(v)
            
            if func_symbol.funcion==False:
                if getSymbolClass(func_symbol) == class_name:
                    self.cuadruplas.extend(heap_variable(func_symbol.lexema, func_symbol.tipo_token, func_symbol.size))
                # elif class_name=="Main":
                #     self.cuadruplas.append(heap_variable(func_symbol.lexema, class_name))
            
        

        if class_name == "Main":
            self.in_main = False

        self.tablaSimbolos.get_exitScope()
        
    def visitFeature(self, ctx: yalpParser.FeatureContext):
        
        token_type = "FUNCTION" if ctx.LPAR() else "ATTRIBUTE"
        feature_name = ctx.ID().getText()
        feature_type = ctx.TYPE().getText() if ctx.TYPE() else None
        if feature_type == "SELF_TYPE":
            feature_type = self.actual_class

        if token_type == "FUNCTION":
            self.tablaSimbolos.get_enterScope()

            # visited = self.handle_context(ctx)
           
        visited = []
        if ctx.expr():
            visited = self.visit(ctx.expr())
        
        
        if ctx.ASSIGN() and ctx.expr():
            original_type = ctx.TYPE().getText() if ctx.TYPE() else None
            assign = self.visit(ctx.expr())[0]
            self.cuadruplas.append(valueAssign(assign))
            #('STack...', None, None, valor)
        else:
            if token_type == "ATTRIBUTE":
                #print('tipo', feature_type)
                if feature_type == "Int":
                    self.cuadruplas.append(valueAssign(0))
                elif feature_type == "String":
                    self.cuadruplas.append(valueAssign('""'))
                elif feature_type == "Boolean":
                    self.cuadruplas.append(valueAssign(0)) # 0 = false, 1 = true
                else:
                    self.cuadruplas.append(valueAssign(None))
                    
        params = []
        sizes = []
        for formal_ctx in ctx.formal():
            parametros = self.visit(formal_ctx)
            params.append(parametros)
            
            sizes.append(self.tablaSimbolos.current_scope.symbols[parametros[0]].size)
            
        if token_type == "FUNCTION":
            self.tablaSimbolos.get_exitScope()

            clase = self.tablaSimbolos.get_simbolo(self.actual_class)

            # if self.in_main:
            self.cuadruplas.extend(create_function(feature_name, params, visited, clase.lexema, sizes))

            if self.stack_created: 
                retorno = False
                for i in self.cuadruplas:
                    if isinstance(i, list):
                        for j in i:
                            if j.op == 'return_let' or j.op == 'return_func':
                                retorno = True
                    else:
                        if i.op == 'return_let' or i.op == 'return_func':
                            retorno = True

                temp = Cuadrupla("stack_pop", None, None, None)
                self.cuadruplas.append(temp)

                if not retorno:
                    temp = Cuadrupla("return_func", None, None, self.cuadruplas[-1].res)
                    self.cuadruplas.append(temp)

                self.stack_created = False

            else:
                retorno = False
                for i in self.cuadruplas:
                    if isinstance(i, list):
                        for j in i:
                            if j.op == 'return_let' or j.op == 'return_func':
                                retorno = True
                    else:
                        if i.op == 'return_let' or i.op == 'return_func':
                            retorno = True

                if not retorno:
                    temp = Cuadrupla("return_func", None, None, self.cuadruplas[-1].res)
                    self.cuadruplas.append(temp)

            # else:
            #     self.cuadruplas.extend(create_heap_function(feature_name, params, visited))

        return feature_name
    
    def upLabel(self):
        self.labels += 1
        return self.labels
      
    def visitExpr(self, ctx: yalpParser.ExprContext):
        
        if ctx.IF():
            
            self.tablaSimbolos.get_enterScope()

            visited = self.handle_context(ctx)

            if_expr = []
            then_expr = []
            else_expr = []
            
            inIf = False
            inThen = False
            inElse = False
            
            for v in visited:
                if v == 'if':
                    inIf = True
                
                elif v == 'then':
                    inIf = False
                    inThen = True

                elif v == 'else':
                    inThen = False
                    inElse = True

                elif v == 'FI':
                    inElse = False
                
                else:
                    if inIf:
                        if_expr.append(v)

                    elif inThen:
                        then_expr.append(v)
                    
                    elif inElse:
                        else_expr.append(v)

            # label = self.getLabel()
            # label = f'Label{label}'

            cuadruplas = create_if(if_expr, then_expr, else_expr, self)
            # self.cuadruplas.extend(cuadruplas)
            self.tablaSimbolos.get_exitScope()      
            
            return cuadruplas

        elif ctx.ELSE():
            self.tablaSimbolos.get_enterScope()

            visited = self.handle_context(ctx)

            self.tablaSimbolos.get_exitScope()

        elif ctx.WHILE():
            self.tablaSimbolos.get_enterScope()
            

            visited_while = self.handle_context(ctx)

            # visited_while = visited_while[1][0]
            # temp = visited_while
            while_expr = []
            loop_expr = []

            inWhile = False
            inLoop = False

            for v in visited_while:
                if v == 'while':
                    inWhile = True
                
                elif v == 'loop':
                    inWhile = False
                    inLoop = True
                
                elif v == 'pool':
                    inLoop = False

                else:
                    if inWhile:
                        while_expr.append(v)

                    elif inLoop:
                        loop_expr.append(v)

            cuadruplas = create_while(while_expr, loop_expr, self)
            # self.cuadruplas.extend(cuadruplas)

            
            self.tablaSimbolos.get_exitScope()
            return cuadruplas

            # return cuadruplas

            # return visited_while

        elif ctx.LET():
            
            self.tablaSimbolos.get_enterScope()
            Cuadruplas = []
            
            visited_let = self.handle_context(ctx)
            # tipo = visited_let[-1][0]

            variables = []
            # # sin la primera posicion ni las ultimas dos
            # variables = visited_let[1:-2]
            in_ = False
            for i in visited_let:
                if i == "in":
                    in_ = True
                
                else:
                    if not in_ and i != "let":
                        variables.append(i)


            # if '<-' in variables:
            #     print(variables)
            
            # else:
            variables = ''.join(variables).split(',')
            
            definido = False

            for variable in variables:
                temp = variable.split(':')
                variable = temp[0]
                tipo = temp[1].split('<-')[0]
                valor = temp[1].split('<-')[1] if len(temp[1].split('<-')) > 1 else None

                token = self.tablaSimbolos.get_simbolo(variable)
                # print(token)
                # input()
                if token.in_function:

                    if not definido:
                        temp = Cuadrupla("stack_register_init", None, None, None)
                        Cuadruplas.append(temp)
                        definido = True
                        self.stack_created = True
                    Cuadruplas.append(valueAssign(valor))
                    #stack_assign_declare()
                    cuadrupla = stack_variable(token.lexema, token.tipo_token, token.size)
                    Cuadruplas.append(cuadrupla)

            in_ = False
            for i in visited_let:

                if i == "in":
                    in_ = True
                else:
                    if in_:
                        Cuadruplas.append(i)


            ya_retorno = False
            for i in Cuadruplas:
                if isinstance(i, Cuadrupla):
                    if "return_let" == i.op:
                        ya_retorno = True


            if not ya_retorno:
                retorno = None
                if Cuadruplas[-1].res == None:
                    retorno = Cuadruplas[-1].arg1

                else:
                    retorno = Cuadruplas[-1].res

                temp = Cuadrupla("return_let", None, None, retorno)
                Cuadruplas.append(temp)
            
            self.tablaSimbolos.get_exitScope()

            return Cuadruplas

        elif ctx.DOT():
            visited_dot = self.handle_context(ctx)
            inherit_visited = []
            #print(visited_dot)

            if ctx.AT():

                variable = visited_dot[0][0]
                clase = visited_dot[2]
                funcion = visited_dot[4]

                if len(visited_dot) > 5:
                    parametros = visited_dot[5:]

                else:
                    parametros = []

                cuadruplas = create_function_call(clase, variable, funcion, parametros)


                return cuadruplas


            variable = visited_dot[0]
            function = visited_dot[2]
            parametros = []
            # print(variable)
            type_variable = self.tablaSimbolos.get_simbolo(variable)

            if None == type_variable:
                # es nativo
                token = variable
            
            else:
                token = type_variable.tipo_token

            
            if len(visited_dot) > 3:
                # Apartir de la posicion 3 en adelante son los parametros
                parametros = visited_dot[3:]

            temp = []
            for parametro in parametros:
                if parametro != ",":
                    temp.append(parametro)
            #print(temp)

            parametros = temp

            cuadruplas = create_function_call(token, variable, function, parametros, self.cuadruplas)
            return cuadruplas

        elif ctx.ISVOID():
            visited = self.handle_context(ctx)
            temp = 't1'
            cuadrupla = create_isVoid(visited[1], temp)
            return cuadrupla

        elif ctx.ID() and ctx.LPAR():
            visited_func = self.handle_context(ctx)
            func_name = visited_func[0]
            parametros = []
            
            func_symbol = self.tablaSimbolos.get_simbolo(func_name)
            class_scope = func_symbol.scope
            global_scope = class_scope.parent
            index = global_scope.children.index(class_scope)
            classes = list(global_scope.symbols.keys())
            class_name = classes[index]

            if len(visited_func) > 2:
                parametros = visited_func[2:]
                
            cuadruplas = create_function_call(class_name, None, func_name, parametros, self.cuadruplas)
            self.cuadruplas.extend(cuadruplas)

            return cuadruplas
            
           
        elif ctx.LPAR() and not ctx.ID():

            visited = self.handle_context(ctx)
            compared = None

            # if isinstance(visited, list) and not isinstance(visited[1], Cuadrupla):
            #     compared = visited[1][0]
            
            # else:
            #     compared = visited[1]

            if not isinstance(visited[0], Cuadrupla):
                compared = visited[0]
            
            else:
                compared = visited[0]
            

            return visited

            
        # elif ctx.DIAC():

        #     visited = self.handle_context(ctx)
        #     print(visited)
        #     op = visited[0]
        #     operador = visited[1]

        #     # cuadrupla = operacion(op, operador, None, None, self.in_main)
        #     # return [cuadrupla]

        #     return visited
             

        elif ctx.ID() and ctx.ASSIGN() and not ctx.LET():
            visited = self.handle_context(ctx)
            cuadruplas = []

            variable = visited[0]
            asig = visited[2::]
            
            res = self.tablaSimbolos.get_simbolo(visited[0])
            print(asig)
            if isinstance(asig[0], Cuadrupla):
                cuadruplas.extend(asig)
                if(asig[-1].op == "call"):
                    asig[-1].res = variable

                cuadruplas.append(asignacion(asig[-1].res, variable, res.size))
                # cuadruplas.append(asignacion(visited[2].res, visited[0]))
            
            else:
                #print(res)

                cuadruplas.append(asignacion(visited[2], visited[0], res.size))
            # cuadrupla = asignacion(visited[2], visited[0])

            return cuadruplas
            
        
        elif ctx.LT() or ctx.RT() or ctx.LE() or ctx.RE() or ctx.EQUALS() or ctx.PLUS() or ctx.TIMES() or ctx.MINUS() or ctx.DIVIDE() or ctx.DIAC():
    
            visited_op = self.handle_context(ctx)

            # print(visited_op, 'visited op')
            temp_counter = 1
            operacion_postfix = self.toPostfix(visited_op)
            # print(operacion_postfix, 'operacion postfix')
            cuadruplas = []

            stack = []
            for token in operacion_postfix:
                if isinstance(token, Cuadrupla):
                    cuadruplas.append(token)
                    stack.append(token.res)

                    while token.res == f'a{temp_counter}':
                        temp_counter += 1

                elif token.isnumeric() or token.isalpha() or token=='""':
                    stack.append(token)

                else:
                   
                    arg2 = stack.pop()

                    if len(stack) == 0:
                        arg1 = None
                    else:
                        arg1 = stack.pop()

                    temp = f'a{temp_counter}'
                    temp_counter += 1

                    type_arg1 = self.tablaSimbolos.get_simbolo(arg1)
                    type_arg2 = self.tablaSimbolos.get_simbolo(arg2)

                    if type_arg1 is None:
                        type_arg1 = arg1
                        if isinstance(arg1, CommonToken):
                            primero = [arg1, False, type_arg1.in_function, type_arg1.size]
                        else:
                            primero = [arg1, True, False, None]

                    else:

                        primero = [arg1, type_arg1.parametro, type_arg1.in_function, type_arg1.size]

                    if type_arg2 is None:
                        type_arg2 = arg2
                        if isinstance(arg2, CommonToken):
                            segundo = [arg2, False, type_arg2.in_function, type_arg2.size]
                        else:
                            segundo = [arg2, True, False, None]

                    else:
                        segundo = [arg2, type_arg2.parametro, type_arg2.in_function, type_arg2.size]

                    # print(type_arg1.lexema, type_arg1.tipo_token, type_arg1.parametro)
                    # print(type_arg2.lexema, type_arg2.tipo_token, type_arg2.parametro)
                    # primero = [arg1, type_arg1.parametro]
                    # segundo = [arg2, type_arg2.parametro]
                    
                    cuadruplas.extend(operacion(token, primero, segundo, temp, self.in_main))
                    
                    stack.append(temp)
                
            

            return cuadruplas
            
        
        elif ctx.LBRACE() and ctx.RBRACE():
            visited = self.handle_context(ctx)
            expressions = [i for i in visited if isinstance(i, list)]
            return visited
         
        elif ctx.ISVOID():
            
            visited = self.handle_context(ctx)
            # expresion = visited[1][0]

            return visited
            
        elif ctx.NEW():
            
            visited = self.handle_context(ctx)
            return visited

        else:
            v = self.handle_context(ctx) 

            return v

    def visitFormal(self, ctx: yalpParser.FormalContext):
        
        if ctx.ID() is not None and ctx.TYPE() is not None:

            if isinstance(ctx.ID(), list) and isinstance(ctx.TYPE(), list):

                ids = ctx.ID()
                tipos = ctx.TYPE()

                parametros = []
                for id_node, tipo_node in zip(ids, tipos):

                    variable_name = id_node.getText()
                    variable_type = tipo_node.getText()

                    parametros.append([variable_name, variable_type])

                    # regresar el arreglo de tipos
                return parametros
                    
            else:

                variable_name = ctx.ID().getText()
                variable_type = ctx.TYPE().getText()

                return [variable_name, variable_type]
            
    def handle_context(self, ctx, formal=False):
        visited = []
        for child_ctx in ctx.getChildren():
            if isinstance(child_ctx, TerminalNode):
                token = self.visitTerminal(child_ctx, formal)

                if token not in ['{', '}', '(', ')', ';'] and not formal:
                    visited.append(token)
            
            else:
                v = self.visit(child_ctx)

                if v is not None and isinstance(v, list):
                    visited.extend(v)
                
                elif v is not None:
                    visited.append(v)
        return visited

    def visitTerminal(self, node: TerminalNode, formal=False):
        token = node.getSymbol()
        return token.text
    
