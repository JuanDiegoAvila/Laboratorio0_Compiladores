class MIPS(object):
    def __init__(self, cuadruplas):
        self.cuadruplas = cuadruplas
        
        self.in_main = False
        self.in_class_main = False
        self.texto = self.traducirTAC()
        self.escribiCodigo()
        self.queue = []


    def traducirTAC(self):
        texto = ""
        temporal = ""
        for cuadrupla in self.cuadruplas:

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

 
        elif operador == "func":
            nombre = arg1

            # if nombre == "main":
            #     texto += ".text\n"
            #     texto += ".globl main\n"
            
            # else:
            #     texto += "\n\n"

            texto += nombre + ":\n"

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

        elif operador == "call":
            texto += "\tjal " + arg1 + "\n\n"

        elif operador == "exit":
            texto += "\tli $v0, 10\n"
            texto += "\tsyscall\n\n"


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

                
        