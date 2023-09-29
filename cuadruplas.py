
class Cuadrupla(object):
    def __init__(self, op, arg1, arg2, res):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.res = res


    def __str__(self):
        return f"({self.op}, {self.arg1}, {self.arg2}, {self.res})"

    def __repr__(self):
        return str(self)
    
def asignacion(arg1, res):
    return Cuadrupla("=", arg1, None, res)

def operacion(op, arg1, arg2, res):
    if op== '=':
        op = '=='
    return Cuadrupla(op, arg1, arg2, res)

def Not(arg1, res):
    return Cuadrupla("!", arg1, None, res)

def create_class_label(name):
    return Cuadrupla("class", name, None, None)

def create_if(if_expr, then_expr, else_expr, CI):
    label1 = f'L{CI.upLabel()}'
    
    Cuadruplas = []

    # print(if_expr, type(if_expr))

    if isinstance(if_expr, Cuadrupla):
        Cuadruplas.append(if_expr)
        if_expr = if_expr.res
    
    inicio = Cuadrupla("ifFalse", if_expr, None, label1)
    Cuadruplas.append(inicio)
    
    for i in then_expr:
        Cuadruplas.append(i)

    temp = []
    label1 = Cuadrupla("label", None, None, label1)
    temp.append(label1)

    for i in else_expr:
        temp.append(i)

    label2 = f'L{CI.upLabel()}'

    goto = Cuadrupla("goto", None, None, label2)
    Cuadruplas.append(goto)

    Cuadruplas.extend(temp)

    label2 = Cuadrupla("label", None, None, label2)
    Cuadruplas.append(label2)

    return Cuadruplas


def create_function_call(variable, name, params):
    # asignar primero los parametros

    Cuadruplas = []
    parametros = 0
    for i in params:
        parametros += 1
        temp = Cuadrupla("param", i, None, None)
        Cuadruplas.append(temp)

    # ULTIMA POSICION PARA EL VALOR DE RETORNO
    temp = Cuadrupla("call", name, parametros, variable)
    Cuadruplas.append(temp)

    return Cuadruplas

def create_function(name, params, expr):
    Cuadruplas = []

    inicio = Cuadrupla("func", name, None, None)
    Cuadruplas.append(inicio)

    if params != []:
        for i in params:
            temp = Cuadrupla("param_decl", i[0], i[1], None)
            Cuadruplas.append(temp)

    for i in expr:
        Cuadruplas.append(i)
        
    return Cuadruplas

def create_while(while_expr, loop_expr, CI): 
    # print('WHILE')
    
    label1 = f'L{CI.upLabel()}'
    
    Cuadruplas = []

    label_1 = Cuadrupla("label", None, None, label1)
    Cuadruplas.append(label_1)

    if isinstance(while_expr, Cuadrupla):
        Cuadruplas.append(while_expr)
        while_expr = while_expr.res

   

    temp = []
    for i in loop_expr:
        temp.append(i)

    goto = Cuadrupla("goto", None, None, label1)
    temp.append(goto)

    
    label2 = f'L{CI.upLabel()}'
    inicio = Cuadrupla("ifFalse", while_expr, None, label2)
    Cuadruplas.append(inicio)

    Cuadruplas.extend(temp)

    label2 = Cuadrupla("label", None, None, label2)
    Cuadruplas.append(label2)

    return Cuadruplas

def create_isVoid(variable, res):
    return Cuadrupla("isVoid", variable, None, res)

from prettytable import PrettyTable

def escribir_cuadruplas(cuadruplas):
    labels = ["Indice", "Operador", "Operando 1", "Operando 2", "Resultado"]
    x = PrettyTable()
    x.field_names = labels
    for i, cuadrupla in enumerate(cuadruplas):
        if isinstance(cuadrupla, Cuadrupla):
            x.add_row([i, cuadrupla.op, cuadrupla.arg1, cuadrupla.arg2, cuadrupla.res])
        else:
            print(cuadrupla)
    return x
    