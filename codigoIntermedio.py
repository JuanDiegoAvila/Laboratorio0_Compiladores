from antlr4.tree.Tree import TerminalNode
from graphviz import Digraph
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
        self.stack = Stack()

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

            elif token.isnumeric() or token.isalpha():  # Operand
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
        self.scope_counter = 0
        for class_ctx in ctx.class_():
            self.visit(class_ctx)

    def visitClass(self, ctx: yalpParser.ClassContext):
        class_name = ctx.TYPE()[0].getText()
            
        self.cuadruplas.append(create_class_label(class_name))

        for feature_ctx in ctx.feature():
            self.visit(feature_ctx)
        
        self.tablaSimbolos.exitScope()

    def visitFeature(self, ctx: yalpParser.FeatureContext):
        token_type = "FUNCTION" if ctx.LPAR() else "ATTRIBUTE"
        feature_name = ctx.ID().getText()
        feature_type = ctx.TYPE().getText() if ctx.TYPE() else None
        if feature_type == "SELF_TYPE":
            feature_type = self.actual_class

        if token_type == "FUNCTION":
            visited = self.handle_context(ctx)
            print(visited)
           #for i in self.tablaSimbolos.current_scope.parent.children:
            #    print(i.name)
            pass

        #     #self.tablaSimbolos.get_enterScope()
        
        visited = []
        if ctx.expr():
            visited = self.visit(ctx.expr())
        
        if ctx.ASSIGN() and ctx.expr():
            original_type = ctx.TYPE().getText() if ctx.TYPE() else None
            assign = self.visit(ctx.expr())[0]
        
        params = []
        for formal_ctx in ctx.formal():
            parametros = self.visit(formal_ctx)
            params.append(parametros)
            
        if token_type == "FUNCTION":
            # self.tablaSimbolos.get_exitScope()
            self.cuadruplas.extend(create_function(feature_name, params, visited))

        return feature_name
    
    def upLabel(self):
        self.labels += 1
        return self.labels
    
    
             
    def visitExpr(self, ctx: yalpParser.ExprContext):
        
        if ctx.IF():
            
            
            # #self.tablaSimbolos.get_enterScope()

            visited = self.handle_context(ctx)
            print('if', visited)
            

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


            cuadruplas = create_if(if_expr[0], then_expr, else_expr, self)
            # self.cuadruplas.extend(cuadruplas)
            return cuadruplas


            return cuadruplas

            #self.tablaSimbolos.get_exitScope()      


        elif ctx.WHILE():
            #self.tablaSimbolos.get_enterScope()
            

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

            cuadruplas = create_while(while_expr[0], loop_expr, self)
            # self.cuadruplas.extend(cuadruplas)

            return cuadruplas

            # return cuadruplas
            #self.tablaSimbolos.get_exitScope()

            # return visited_while

        elif ctx.LET():
            
            #self.tablaSimbolos.get_enterScope()
            
            visited_let = self.handle_context(ctx)
            tipo = visited_let[-1][0]
            
            
            #self.tablaSimbolos.get_exitScope()

            return visited_let

        elif ctx.DOT():
            visited_dot = self.handle_context(ctx)
            inherit_visited = []


            if ctx.AT():

                variable = visited_dot[0][0]
                clase = visited_dot[2]
                funcion = visited_dot[4]



            variable = visited_dot[0]
            function = visited_dot[2]
            parametros = []
            
            if len(visited_dot) > 3:
                # Apartir de la posicion 3 en adelante son los parametros
                parametros = visited_dot[3:]

            cuadruplas = create_function_call(variable, function, parametros)
            return cuadruplas

        elif ctx.ISVOID():
            visited = self.handle_context(ctx)
            temp = 't1'
            cuadrupla = create_isVoid(visited[1], temp)
            return cuadrupla

        elif ctx.ID() and ctx.LPAR():
            visited_func = self.handle_context(ctx)
            
            func_name = visited_func[0]

            return visited_func
            
           
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

            
        elif ctx.DIAC():

            visited = self.handle_context(ctx)


            return visited
             

        elif ctx.ID() and ctx.ASSIGN() and not ctx.LET():
            visited = self.handle_context(ctx)

            cuadrupla = asignacion(visited[2], visited[0])

            return cuadrupla
            
        
        elif ctx.LT() or ctx.RT() or ctx.LE() or ctx.RE() or ctx.EQUALS() or ctx.PLUS() or ctx.TIMES() or ctx.MINUS() or ctx.DIVIDE():
    
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

                    while token.res == f't{temp_counter}':
                        temp_counter += 1

                elif token.isnumeric() or token.isalpha():
                    stack.append(token)

                else:
                    arg2 = stack.pop()
                    arg1 = stack.pop()
                    temp = f't{temp_counter}'
                    temp_counter += 1
                    
                    cuadruplas.append(operacion(token, arg1, arg2, temp))
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
            type = visited[1].text

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

                if token not in ['{', '}', '(', ')', ';', ','] and not formal:
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
    
