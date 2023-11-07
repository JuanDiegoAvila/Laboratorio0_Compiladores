
def traducirCodigo(cuadruplas):
    texto = ""
    clase_actual = ""

    for cuadrupla in cuadruplas:
        if isinstance(cuadrupla, list):
            cuadrupla = cuadrupla[0]

        operador = cuadrupla.op
        argumento1 = cuadrupla.arg1
        argumento2 = cuadrupla.arg2
        respuesta = cuadrupla.res

        if operador == "class" and argumento1 == "Main":
            clase_actual = argumento1
            texto += f"\n{argumento1}:\n"

        if operador in ["+", "-", "*", "/", "==", "<", ">", "<=", ">=", "and", "or", "~"]:
            texto += f"\t {respuesta} = {argumento1} {operador} {argumento2}\n"

        elif operador == "func":
            # if clase_actual == "Main" and argumento1 == "main":
            #     texto += f"\t call {argumento1}\n"

            texto += f"\n{argumento1}:\n"

        elif operador == "call":
            texto += f"\t call {argumento1}\n"

        elif operador == "param_decl":
            texto += f"\t param {argumento1} : {argumento2}\n"

        elif operador == "exit":
            texto += f"\t exit program\n"

        elif operador in ["heap_assign", "stack_assign"]:
            texto += f"\t {operador} {respuesta} = {argumento1}\n"
        
        elif operador == "=":
            texto += f"\t {respuesta} = {argumento1}\n"

        elif operador == "goto":
            texto += f"\t goto {respuesta}\n"

        elif operador == "label":
            texto += f"\n\t label {respuesta}: \n"

        elif operador in ["return_func", "return_let"]:
            texto += f"\t return {respuesta}\n"

        elif operador in ["stack_register_init", "stack_pop"]:
            texto += f"\t {operador}\n"

        elif operador == "current_heap_instance":
            texto += f"\t {operador} = {respuesta}\n"

        elif operador == "ifFalse":
            texto += f"\t ifFalse {argumento1}, {respuesta}\n"

        elif operador in ["heap_declaration", "stack_declaration"]:
            texto += f"\t {operador} {argumento1} : {argumento2}\n"

    return(texto)


             
            

        