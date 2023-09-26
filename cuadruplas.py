
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
    return Cuadrupla(op, arg1, arg2, res)

def Not(arg1, res):
    return Cuadrupla("!", arg1, None, res)

def create_class_label(name):
    return Cuadrupla(name, None, None, None)

def create_if(if_expr, then_expr, else_expr, label):
    label1 = f'L{label}'
    
    label = label + 1
    label2 = f'L{label}'

    Cuadruplas = []

    print(if_expr, type(if_expr))

    if isinstance(if_expr, Cuadrupla):
        Cuadruplas.append(if_expr)
        if_expr = if_expr.res
    
    inicio = Cuadrupla("ifFalse", if_expr, None, label1)
    Cuadruplas.append(inicio)
    
    for i in then_expr:
        Cuadruplas.append(i)

    goto = Cuadrupla("goto", None, None, label2)
    Cuadruplas.append(goto)

    label1 = Cuadrupla("label", None, None, label1)
    Cuadruplas.append(label1)

    for i in else_expr:
        Cuadruplas.append(i)
    
    label2 = Cuadrupla("label", None, None, label2)
    Cuadruplas.append(label2)

    return Cuadruplas, label

def create_while(while_expr, loop_expr, label): 
    print('WHILE')
    
    label1 = f'L{label}'
    
    label = label + 1
    label2 = f'L{label}'

    Cuadruplas = []

    label_1 = Cuadrupla("label", None, None, label1)
    Cuadruplas.append(label_1)

    if isinstance(while_expr, Cuadrupla):
        Cuadruplas.append(while_expr)
        while_expr = while_expr.res

    inicio = Cuadrupla("ifFalse", while_expr, None, label2)
    Cuadruplas.append(inicio)

    for i in loop_expr:
        Cuadruplas.append(i)

    goto = Cuadrupla("goto", None, None, label1)
    Cuadruplas.append(goto)

    label2 = Cuadrupla("label", None, None, label2)
    Cuadruplas.append(label2)

    return Cuadruplas, label



