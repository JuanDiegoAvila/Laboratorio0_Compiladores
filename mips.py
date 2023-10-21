class MIPS(object):
    def __init__(self, cuadruplas):
        self.cuadruplas = cuadruplas
        self.texto = self.traducirTAC()
        self.escribiCodigo()

    def traducirTAC(self):
        texto = ""
        for cuadrupla in self.cuadruplas:
            operador = cuadrupla.op
            arg1 = cuadrupla.arg1
            arg2 = cuadrupla.arg2
            res = cuadrupla.res

            if operador == "func":
                nombre = arg1

                if nombre == "main":
                    texto += ".text\n"
                    texto += ".globl main\n"
                
                else:
                    texto += "\n\n"

                texto += nombre + ":\n"

            if operador == "=":

                
                # Si es un numero usar li, sino usar la
                try:
                    int(arg1)
                    texto += f"\tli ${res}, {arg1} \n"
                except:
                    texto += f"\tla ${res}, {arg1} \n"
                # if isinstance(arg1, int):
                #     texto += f"\tli ${res}, {arg1} \n"
                # else:
                #     texto += f"\tla ${res}, {arg1} \n"

                # cargar el valor en la direccion de memoria con lw
                texto += f"\tlw ${res}, 0(${res})\n\n"

            elif operador == "+":

                texto += "\tadd $a0, $" + str(arg1) + ", $" + str(arg2) + "\n"

            elif operador == "/":

                texto += "\tdiv $" + str(arg1) + ", $" + str(arg2) + "\n"
                texto += "\tmfhi $t0\n"


        return texto
    
    def escribiCodigo(self):
        path = "./MIPS/codigoMIPS.s"
        archivo = open(path, "w")
        archivo.write(self.texto)
        archivo.close()

                
        