
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
    
    def copy(self):
        return Cuadrupla(self.op, self.arg1, self.arg2, self.res)
    
    
    
def asignacion(arg1, res, size):
    return Cuadrupla("=", arg1, size, res)

def valueAssign(assign):
    return Cuadrupla("value_assign", None, None, assign)




def operacion(op, arg1, arg2, res, in_main):
    # if in_main:
    #     return [Cuadrupla(op, arg1[0], arg2[0], res)]

    # else:
    if op == "=":
        op = "=="
        
    Cuadruplas = []
    
    if not arg1[2] or not arg2[2]:
        current_instance = Cuadrupla("current_heap_instance", None, None, "t1")
        Cuadruplas.append(current_instance)

    if not arg1[1]:
        if not arg1[2]:
            temp = Cuadrupla("heap_assign", f'heap[t1 + offset{arg1[0]}]', None, "t2")
            primero = temp
        else:
            temp = Cuadrupla("stack_assign", f'stack[offset{arg1[0]}]', None, "t2")
            primero = temp
    else:
        primero = Cuadrupla("=", arg1[0], arg1[3], "t2")
    
    if not arg2[1]:
        if not arg2[2]:
            temp = Cuadrupla("heap_assign", f'heap[t1 + offset{arg2[0]}]', None, "t3")
            segundo = temp
        else:
            temp = Cuadrupla("stack_assign", f'stack[offset{arg2[0]}]', None, "t3")
            segundo = temp
    else:
        segundo = Cuadrupla("=", arg2[0], arg2[3], "t3")

    temp = Cuadrupla(op, "t2", "t3", "t4")


        # if not arg2[1]:
        #     update_instance = Cuadrupla("update_instance", "t1", f"offest{arg2[0]}", "current_instance")
        #     return [current_instance, primero, segundo, temp, update_instance]
        
        # elif not arg1[1] and arg2[1]:
        #     update_instance = Cuadrupla("update_instance", "t1", f"offest{arg1[0]}", "current_instance")
        #     return [current_instance, primero, segundo, temp, update_instance]
    Cuadruplas.extend([primero, segundo, temp])

    return Cuadruplas

        
def stack_variable(arg1, tipo, size):
    return Cuadrupla("stack_declaration", arg1, tipo, size)


def Not(arg1, res):
    return Cuadrupla("!", arg1, None, res)

def create_class_label(name):
    return Cuadrupla("class", name, None, None)

# def create_if(if_expr, then_expr, else_expr, CI):
#     label1 = f'L{CI.upLabel()}'
    
#     Cuadruplas = []

#     # print(if_expr, type(if_expr))

#     if isinstance(if_expr, Cuadrupla):
#         Cuadruplas.append(if_expr)
#         if_expr = if_expr.res
    
#     inicio = Cuadrupla("ifFalse", if_expr, None, label1)
#     Cuadruplas.append(inicio)
    
#     for i in then_expr:
#         Cuadruplas.append(i)

#     temp = []
#     label1 = Cuadrupla("label", None, None, label1)
#     temp.append(label1)

#     for i in else_expr:
#         temp.append(i)

#     label2 = f'L{CI.upLabel()}'

#     goto = Cuadrupla("goto", None, None, label2)
#     Cuadruplas.append(goto)

#     Cuadruplas.extend(temp)

#     label2 = Cuadrupla("label", None, None, label2)
#     Cuadruplas.append(label2)

#     return Cuadruplas

def create_if(if_expr, then_expr, else_expr, CI):
    # Genera etiquetas únicas
    label_then_end = f'L{CI.upLabel()}'
    label_else_start = f'L{CI.upLabel()}'
    
    Cuadruplas = []

    # Si if_expr es una Cuadrupla, la agregamos y usamos su resultado
    if isinstance(if_expr, Cuadrupla):
        Cuadruplas.append(if_expr)
        if_expr = if_expr.res

    if isinstance(if_expr, list):
        Cuadruplas.extend(if_expr)
        if_expr = if_expr[-1].res if isinstance(if_expr[-1], Cuadrupla) else if_expr[-1]
    
    
    # Agrega la cuádrupla inicial para saltar al bloque else si la condición es falsa
    Cuadruplas.append(Cuadrupla("ifFalse", if_expr, None, label_else_start))
    
    # Agrega cuádruplas para el bloque then
    Cuadruplas.extend(then_expr)
    
    # Agrega un salto incondicional al final del bloque if-else
    Cuadruplas.append(Cuadrupla("goto", None, None, label_then_end))

    # Agrega la etiqueta del inicio del bloque else
    Cuadruplas.append(Cuadrupla("label", None, None, label_else_start))

    # Agrega cuádruplas para el bloque else
    Cuadruplas.extend(else_expr)

    # Agrega la etiqueta del final del bloque if-else
    Cuadruplas.append(Cuadrupla("label", None, None, label_then_end))

    return Cuadruplas



def create_function_call(clase, variable, name, params, cuadruplas=None):
    # asignar primero los parametros
    Cuadruplas = []
    parametros = 0
    sizes = []
    size_reserve = 0
    if cuadruplas:
        for i in range(len(cuadruplas)):
            if cuadruplas[i].arg1 == name+"_"+clase:
                for j in range(len(params)):
                    sizes.append((cuadruplas[i+j+1].arg2, cuadruplas[i+j+1].res))
                    size_reserve+=cuadruplas[i+j+1].arg2
                break
            
    Cuadruplas.append(Cuadrupla('reserve_space', size_reserve, None, None))
    for i in range(len(params)):
        if cuadruplas:
            size, offset = sizes[i]
        else:
            size, offset = None, None
        parametros += 1
        temp = Cuadrupla("param", params[i], size, offset)
        Cuadruplas.append(temp)

    temp = Cuadrupla("call", name+"_"+clase, parametros, variable)
    Cuadruplas.append(temp)

    return Cuadruplas


def heap_variable(arg1, class_name, espacio):
    # guardar_espacio = Cuadrupla("maloc", arg1, , None)
    declaracion = Cuadrupla("heap_declaration", arg1, class_name, espacio)
    return [ declaracion]

# def create_heap_function(name, params, expr):
#     Cuadruplas = []
#     temps = 0

#     inicio = Cuadrupla("func", name, None, None)
#     Cuadruplas.append(inicio)

#     parametros = []
#     if params != []:
#         for i in params:
#             temp = Cuadrupla("param_decl", i[0], i[1], None)
#             parametros += [i[0]]
#             Cuadruplas.append(temp)

#     t1 = Cuadrupla("current_heap_instance", None, None, "t1")
#     Cuadruplas.append(t1)
#     temps += 1

#     print(parametros)
#     for i in expr:
#         print('op', i.op)
#         print('arg1', i.arg1)
#         print('arg2', i.arg2)
#         print('res', i.res)


#         if i.arg1 not in parametros:
#             if i.arg1 != None:
#                 temps += 1
#                 temp = Cuadrupla("heap_assign", f'heap[t1 + offset{i.arg1}]', None, f't{temps}')
#                 Cuadruplas.append(temp)
#                 i.arg1 = f't{temps}'

#         if i.arg2 not in parametros:
#             if i.arg2 != None:
#                 arg2_check = True
#                 temps += 1
#                 temp = Cuadrupla("heap_assign", f'heap[t1 + offset{i.arg2}]', None, f't{temps}')
#                 Cuadruplas.append(temp)
#                 i.arg2 = f't{temps}'


#         Cuadruplas.append(i)

#     print(Cuadruplas)

        
#     return Cuadruplas

def heap_assign(arg1, res):
    return Cuadrupla("heap_assign", arg1, None, res)

def create_function(name, params, expr, clase, sizes):
    Cuadruplas = []

    # if clase == "Main" and name == "main":
    #     llamada = Cuadrupla("call", "Main_main", 0, None)
    #     # salir = Cuadrupla("exit", None, None, None)

    #     Cuadruplas.append(llamada)
        # Cuadruplas.append(salir)

    inicio = Cuadrupla("func", name+"_"+clase, None, None)
    Cuadruplas.append(inicio)

    if params != []:
        offset = 0
        for i in range(len(params)):
            temp = Cuadrupla("param_decl", params[i][0], sizes[i], offset)
            offset = sizes[i]
            Cuadruplas.append(temp)

    for i in expr:
        if isinstance(i, Cuadrupla):
            Cuadruplas.append(i)
        else:
            Cuadruplas.append(Cuadrupla(None, i, None, i))
        
    return Cuadruplas



# def create_while(while_expr, loop_expr, CI): 
#     # print('WHILE')
    
#     label1 = f'L{CI.upLabel()}'
    
#     Cuadruplas = []

#     label_1 = Cuadrupla("label", None, None, label1)
#     Cuadruplas.append(label_1)

#     if not isinstance(while_expr, list):
#         while_expr = [while_expr]

#     for i in while_expr:
#         if isinstance(i, Cuadrupla):
#             Cuadruplas.append(i)
#             # while_expr = while_expr.res

#     while_expr = while_expr[-1]
#     if isinstance(while_expr, Cuadrupla):
#         while_expr = while_expr.res

   

#     temp = []
#     for i in loop_expr:
#         temp.append(i)

#     goto = Cuadrupla("goto", None, None, label1)
#     temp.append(goto)

    
#     label2 = f'L{CI.upLabel()}'
#     inicio = Cuadrupla("ifFalse", while_expr, None, label2)
#     Cuadruplas.append(inicio)

#     Cuadruplas.extend(temp)

#     label2 = Cuadrupla("label", None, None, label2)
#     Cuadruplas.append(label2)

#     return Cuadruplas
def create_while(while_expr, loop_expr, CI):
    # Create the label for the start of the loop
    label_start = f'L{CI.upLabel()}'
    label_end = f'L{CI.upLabel()}'
    Cuadruplas = []

    call_label1 = Cuadrupla("goto", None, None, label_start)
    Cuadruplas.append(call_label1)
    
    # Label at the beginning of the loop
    label_start_cuad = Cuadrupla("label", None, None, label_start)
    Cuadruplas.append(label_start_cuad)
    
    # Process the condition, the result of the last evaluation in while_expr should be the condition result
    if not isinstance(while_expr, list):
        while_expr = [while_expr]
    Cuadruplas.extend(while_expr)
    
    # This assumes that the last quadruple of while_expr evaluates the condition
    condition_result = while_expr[-1].res if isinstance(while_expr[-1], Cuadrupla) else while_expr[-1]
    
    # Check if the result is false, if so jump to the end (exit the loop)
    exit_loop_cuad = Cuadrupla("ifFalse", condition_result, None, label_end)
    Cuadruplas.append(exit_loop_cuad)
    
    # Body of the loop
    for expr in loop_expr:
        Cuadruplas.extend(expr if isinstance(expr, list) else [expr])
    
    # Jump back to the start of the loop
    goto_start_cuad = Cuadrupla("goto", None, None, label_start)
    Cuadruplas.append(goto_start_cuad)
    
    # Label for the end of the loop
    label_end_cuad = Cuadrupla("label", None, None, label_end)
    Cuadruplas.append(label_end_cuad)
    
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
        
    return x
    