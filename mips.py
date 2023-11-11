class MIPS(object):
    def __init__(self, cuadruplas):
        self.cuadruplas = cuadruplas
        
        self.in_main = False
        self.in_class_main = False
        self.llamada_main = True
        self.texto = self.traducirTAC()
        self.escribiCodigo()
        self.queue = []


    def traducirTAC(self):
        texto = ""
        temporal = ""
        for cuadrupla in self.cuadruplas:
            if isinstance(cuadrupla, list):
                cuadrupla = cuadrupla[0]


            if cuadrupla.op == "class" and cuadrupla.arg1 == "Main":
                self.in_main = True

            texto_temp = ""
            if cuadrupla.op in ["heap_declaration"] and self.in_main:
                clase = cuadrupla.arg2
                variable = cuadrupla.arg1

                queue_temp = self.recorrerCuadruplasCondicion(self.cuadruplas, clase, variable)

                if queue_temp != []:
                    for cuadr in queue_temp:
                        texto_temp += self.traducirCuadupla(cuadr)

            traducido = self.traducirCuadupla(cuadrupla)
            
            if self.in_class_main:

                texto += traducido
                texto += texto_temp if texto_temp != "" else ""

            else:
                temporal += traducido
                temporal += texto_temp if texto_temp != "" else ""

        texto += temporal
        return texto

    def recorrerCuadruplasCondicion(self, cuadruplas, clase, variable):
        encontro_clase = False
        queue_temp = []
        for cuadrupla in cuadruplas:
            
            if isinstance(cuadrupla, list):
                cuadrupla = cuadrupla[0]

            temp = cuadrupla.copy()

            if encontro_clase and cuadrupla.op in ["class", "func"]:
                break

            if cuadrupla.arg1 == clase and cuadrupla.op == "class":
                encontro_clase = True

            if encontro_clase and cuadrupla.op in ["heap_declaration"]:
                temp.arg1 = temp.arg1 + "_" + variable

                queue_temp.append(temp)
        
        return queue_temp

    
    def traducirCuadupla(self, cuadrupla):
        texto = ""
        operador = cuadrupla.op
        arg1 = cuadrupla.arg1
        arg2 = cuadrupla.arg2
        res = cuadrupla.res



        if operador == "class" and self.in_class_main:
            self.in_class_main = False

        elif operador == "class" and arg1 == "Main":
            texto += ".text\n"
            texto += ".globl main\n"
            texto += "main:\n"
            self.in_class_main = True
        

        elif operador in ["func", "label"]:
            if operador == "func":
                nombre = arg1
            elif operador == "label":
                nombre = res

            if self.in_main and self.llamada_main:
                texto += "\tjal main_Main\n"
                texto += "\n\tli $v0, 10\n"
                texto += "\tsyscall\n"
                self.llamada_main = False

            # if nombre == "main":
            #     texto += ".text\n"
            #     texto += ".globl main\n"
            
            # else:
            #     texto += "\n\n"

            texto += "\n\n"+nombre + ":\n"

        elif operador == "=":
            # Si es un numero usar li, sino usar la
            try:
                int(arg1)
                texto += f"\tli ${res}, {arg1} \n"
            except:
                texto += f"\tla ${res}, {arg1} \n"
                
                # cargar el valor en la direccion de memoria con lw
                texto += f"\tlw ${res}, 0(${res})\n\n"


        elif operador == "+":

            texto += "\tadd $a0, $" + str(arg1) + ", $" + str(arg2) + "\n\n"

        elif operador == "/":

            texto += "\tdiv $" + str(arg1) + ", $" + str(arg2) + "\n\n"
            texto += "\tmfhi $t0\n\n"
        
        elif operador == "*":
            texto += "\tmult $" + str(arg1) + ", $" + str(arg2) + "\n\n"
            texto += "\tmflo $t0\n\n"

        elif operador == "heap_declaration" and self.in_class_main:
            espacio = res
            nombre = arg1 
            tipo = arg2

            texto += "\tli $a0, " + str(espacio) + "\n"
            texto += "\tli $v0, 9\n"
            texto += "\tsyscall\n"
            texto += "\tsw $v0, " + nombre + "_address\n\n"
        
        elif operador == ">":
            operador1 = arg1
            operador2 = arg2
            resultado = res

            # text= f"bgt $t0, $t1, true_label"
            texto += f"\tsgt ${resultado}, ${operador1}, ${operador2}\n"
        
        elif operador == "<":
            operador1 = arg1
            operador2 = arg2
            resultado = res

            # text= f"bgt $t0, $t1, true_label"
            texto += f"\tslt ${resultado}, ${operador1}, ${operador2}\n" # resultado = op1 < op2

        elif operador == ">=":
            operador1 = arg1
            operador2 = arg2
            resultado = res
            if resultado[-1]=='4':
                resultado = 't0'
            texto += f"\tsub ${resultado}, ${operador1}, ${operador2}\n" #resultado = op1 - op2
            texto += f"\tsgt $t1, ${resultado}, $zero\n" #resultado = resultado < 0 (significa que op1 si es menor a op2)
            texto += f"\tseq $t0, $t0, 0\n"
            texto += f"\tor $t0, $t0, t1\n"

        elif operador == "<=":
            operador1 = arg1
            operador2 = arg2
            resultado = res
            if resultado[-1]=='4':
                resultado = 't0'
            texto += f"\tsub ${resultado}, ${operador1}, ${operador2}\n" #resultado = op1 - op2
            texto += f"\slti $t1, ${resultado}, \n" #resultado = resultado < 0 (significa que op1 si es menor a op2)
            texto += f"\tseq $t0, $t0, 0\n"
            texto += f"\tor $t0, $t0, t1\n"
        
        elif operador == "==":
            operador1 = arg1
            operador2 = arg2
            resultado = res

            # text= f"bgt $t0, $t1, true_label"
            texto += f"\tseq ${resultado}, ${operador1}, ${operador2}\n"

        elif operador == "call":
            texto += "\tjal " + arg1 + "\n"
        
        elif operador == "goto":
            texto += "\tj " + res + "\n"

        elif operador == "exit":
            texto += "\tli $a0, 10\n"
            texto += "\tsyscall\n\n"

        elif operador == "return_func":
            texto += "\tjr $ra\n\n"

        elif operador == None:
            # carga el operando 1 en el registro res y regresa la direccion de memoria
            # texto += f"\tli $a0, {arg1}\n"
            try:
                int(arg1)
                texto += f"\tli $a0, {arg1} \n"
            except:
                texto += f"\tla $a0, {arg1} \n"
                
                # cargar el valor en la direccion de memoria con lw
                texto += f"\tlw $a0, 0($a0)\n\n"
        
        elif operador == "ifFalse":

            try:
                int(arg1)
                texto += f"\tli $t0, {arg1} \n"
            except:
                texto += f"\tla $t0, {arg1} \n"
                
                # cargar el valor en la direccion de memoria con lw
                texto += f"\tlw $t0, 0($t0)\n\n"

            
            texto += f"\tbeqz $t0, {res}\n\n"
            


        # texto += "operador: " + cuadrupla.op + "\n"
        # texto += "arg1: " + str(cuadrupla.arg1) + "\n" if cuadrupla.arg1 != None else "arg1: None\n"
        # texto += "arg2: " + str(cuadrupla.arg2) + "\n" if cuadrupla.arg2 != None else "arg2: None\n"
        # texto += "res: " + str(cuadrupla.res) + "\n" if cuadrupla.res != None else "res: None\n"
        # texto += "\n\n"
        

        return texto

    
    def escribiCodigo(self):
        path = "./MIPS/codigoMIPS.s"
        archivo = open(path, "w")
        archivo.write(self.texto)
        archivo.close()

                
        