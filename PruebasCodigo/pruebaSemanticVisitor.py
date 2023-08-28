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

        scope = self.tablaSimbolos.get_enterScope()
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
            scope = self.tablaSimbolos.get_enterScope()
            
        if ctx.expr():
            self.visit(ctx.expr())
        
        for formal_ctx in ctx.formal():
            self.visit(formal_ctx)
            
        if token_type == "FUNCTION":
            self.tablaSimbolos.get_exitScope()

        return feature_name

    def visitExpr(self, ctx: yalpParser.ExprContext):

        if ctx.LET():
            scope_let = self.tablaSimbolos.get_exitScope()
            
            visited_let = self.handle_context(ctx)

            self.tablaSimbolos.get_exitScope()

        if ctx.IF():
            scope_if = self.tablaSimbolos.get_exitScope()

            visited_if = self.handle_context(ctx)

            self.tablaSimbolos.get_exitScope()

        if ctx.ELSE():
            scope_else = self.tablaSimbolos.get_exitScope()

            visited_else = self.handle_context(ctx)

            self.tablaSimbolos.get_exitScope()

        if ctx.WHILE():
            scope_while = self.tablaSimbolos.get_exitScope()

            visited_while = self.handle_context(ctx)

            self.tablaSimbolos.get_exitScope()

        # if ctx.MINUS() or ctx.PLUS() or ctx.TIMES() or ctx.DIVIDE() or ctx.LT() or ctx.RT() or ctx.LE() or ctx.RE():
        if ctx.PLUS() or ctx.TIMES() or ctx.MINUS() or ctx.DIVIDE() or ctx.LT() or ctx.RT() or ctx.LE() or ctx.RE():    

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
                                message = f"Error: La variable '{op.text}' en la posicion '{linea}':'{columna}' no ha sido declarada."

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

        
    def checkValues(self, ctx: yalpParser.ExprContext, visited:list):
        types = []
        
        for v in visited:
            print(v)

            if v == "DIGIT" or v == "Int":
                if "Int" not in types:
                    types.append("Int")
            elif v == "STRING" or v == "String":
                if "String" not in types:
                    types.append("String")
            elif v == "TRUE" or v == "FALSE" or v == "Boolean":
                if "Boolean" not in types:
                    types.append("Boolean")

            if v == None:
                return None
            
        if len (types) != 1:
            linea = ctx.start.line
            columna = ctx.start.column
            error = f'Type error: Operacion invalida entre {types[0]} y {types[1]} en la posicion {linea}:{columna}'
            if error not in self.errors:
                self.errors.append(error)

            return None

        return ''.join(types)
    
 #   def checkInt(self, ctx: yalpParser.ExprContext, opTypes:tuple):
        MUL = ctx.TIMES
        DIV = ctx.DIVIDE
        PLUS = ctx.PLUS
        MINUS = ctx.MINUS
        LT =  ctx.LT
        GT =  ctx.RT
        LE =  ctx.LE
        RE =  ctx.RE
        
        
        
        exp1 = opTypes[0] #Debido a que es checkInt se espera que este dato sea int
        exp2 = opTypes[1]
        
        if ctx.getToken(PLUS, 0):
            if exp2 == "string":
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation +: between Int and String'
                self.errors.append(err1)
                self.errors.append(err2)
            elif exp2 == 'Bool':
                #Todo: Expresar el casteo implicito de bool a int
                #False = 0
                #True  = 1
                pass
            #Si se está comparando con una tipo de alguna clase
            else:
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation +: between Int and {exp2}'
                self.errors.append(err1)
                self.errors.append(err2)
            
        elif ctx.getToken(MUL, 0) or ctx.getToken(DIV, 0) or ctx.getToken(MINUS, 0):
            if exp2 == "string":
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation {ctx.getText()}: between Int and String'
                self.errors.append(err1)
                self.errors.append(err2)
            elif exp2 == 'Bool':
                #Todo: Expresar el casteo implicito de bool a int
                #False = 0
                #True  = 1
                
                pass
            #Si se está comparando con una tipo de alguna clase
            else:
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation +: between Int and {exp2}'
                self.errors.append(err1)
                self.errors.append(err2)
        elif ctx.getToken(RE, 0) or ctx.getToken(LE, 0) or ctx.getToken(GT, 0) or ctx.getToken(LT, 0):
            if exp2 == "string":
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: `{ctx.getText()}` not valid: between Int and String'
                self.errors.append(err1)
                self.errors.append(err2)
            elif exp2 == 'Bool':
                #Todo: Expresar el casteo implicito de bool a int
                #False = 0
                #True  = 1
                #Ahora el tipo de expresión resultante será un booleano y no un entero. 
                pass
            #Si se está comparando con una tipo de alguna clase
            else:
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: {ctx.getText()} not valid: between Int and {exp2}'
                self.errors.append(err1)
                self.errors.append(err2)
                
#    def checkString(self, ctx: yalpParser.ExprContext, opTypes:tuple):
        MUL = ctx.TIMES
        DIV = ctx.DIVIDE
        PLUS = ctx.PLUS
        MINUS = ctx.MINUS
        LT =  ctx.LT
        GT =  ctx.RT
        LE =  ctx.LE
        RE =  ctx.RE
        
        
        
        exp1 = opTypes[0] #Debido a que es checkString se espera que este dato sea String
        exp2 = opTypes[1]
        
        if ctx.getToken(PLUS, 0):
            if exp2 == "Int":
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation +: between String and Int'
                self.errors.append(err1)
                self.errors.append(err2)
            elif exp2 == 'Bool':
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation +: between String and Bool'
                self.errors.append(err1)
                self.errors.append(err2)
                
            #Si se está comparando con una tipo de alguna clase
            else:
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation +: between Int and {exp2}'
                self.errors.append(err1)
                self.errors.append(err2)
            
        elif ctx.getToken(MUL, 0) or ctx.getToken(DIV, 0) or ctx.getToken(MINUS, 0):
            if exp2 == "string":
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation {ctx.getText()}: between Int and String'
                self.errors.append(err1)
                self.errors.append(err2)
            elif exp2 == 'Bool':
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation +: between String and Bool'
                self.errors.append(err1)
                self.errors.append(err2)
                
            #Si se está comparando con una tipo de alguna clase
            else:
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation +: between Int and {exp2}'
                self.errors.append(err1)
                self.errors.append(err2)
        elif ctx.getToken(RE, 0) or ctx.getToken(LE, 0) or ctx.getToken(GT, 0) or ctx.getToken(LT, 0):
            if exp2 == "string":
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: `{ctx.getText()}` not valid: between Int and String'
                self.errors.append(err1)
                self.errors.append(err2)
            elif exp2 == 'Bool':
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation +: between String and Bool'
                self.errors.append(err1)
                self.errors.append(err2)
            #Si se está comparando con una tipo de alguna clase
            else:
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: {ctx.getText()} not valid: between Int and {exp2}'
                self.errors.append(err1)
                self.errors.append(err2)
                
#    def checkBool(self, ctx: yalpParser.ExprContext, opTypes:tuple):
        MUL = ctx.TIMES
        DIV = ctx.DIVIDE
        PLUS = ctx.PLUS
        MINUS = ctx.MINUS
        LT =  ctx.LT
        GT =  ctx.RT
        LE =  ctx.LE
        RE =  ctx.RE
        
        
        
        exp1 = opTypes[0] #Debido a que es checkBool se espera que este dato sea bool
        exp2 = opTypes[1]
        
        if ctx.getToken(ctx.PLUS, 0):
            if exp2 == "String":
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation +: between Int and String'
                self.errors.append(err1)
                self.errors.append(err2)
            elif exp2 == 'Int':
                #Todo: Expresar el casteo implicito de bool a int
                #False = 0
                #True  = 1
                pass
            #Si se está comparando con una tipo de alguna clase
            else:
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation +: between Int and {exp2}'
                self.errors.append(err1)
                self.errors.append(err2)
            
        elif ctx.getToken(MUL, 0) or ctx.getToken(DIV, 0) or ctx.getToken(MINUS, 0):
            if exp2 == "String":
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation {ctx.getText()}: between Int and String'
                self.errors.append(err1)
                self.errors.append(err2)
            elif exp2 == 'Int':
                #Todo: Expresar el casteo implicito de bool a int
                #False = 0
                #True  = 1
                
                pass
            #Si se está comparando con una tipo de alguna clase
            else:
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: Invalid operation +: between Int and {exp2}'
                self.errors.append(err1)
                self.errors.append(err2)
        elif ctx.getToken(RE, 0) or ctx.getToken(LE, 0) or ctx.getToken(GT, 0) or ctx.getToken(LT, 0):
            if exp2 == "String":
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: `{ctx.getText()}` not valid: between Int and String'
                self.errors.append(err1)
                self.errors.append(err2)
            elif exp2 == 'Int':
                #Todo: Expresar el casteo implicito de bool a int
                #False = 0
                #True  = 1
                #Ahora el tipo de expresión resultante será un booleano y no un entero. 
                pass
            #Si se está comparando con una tipo de alguna clase
            else:
                err1 = f'Semantic Error: on line {ctx.start.line}, column: {ctx.start.column}'
                err2 = f'Type error: {ctx.getText()} not valid: between Int and {exp2}'
                self.errors.append(err1)
                self.errors.append(err2)           
    
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
