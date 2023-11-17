class Clase:
    def __init__(self, nombre, metodos, clase_base=None):
        self.nombre = nombre
        self.metodos = metodos  
        self.clase_base = clase_base

    def __repr__(self):
        return f"Clase: {self.nombre}\n\tMetodos: {self.metodos}\n\tClase base: {self.clase_base}\n"

class Metodo:
    def __init__(self, nombre, direccion):
        self.nombre = nombre
        self.direccion = direccion

    def __repr__(self):
        return f"Metodo: {self.nombre}\n\tDireccion: {self.direccion}"

class MIPS(object):
    def __init__(self, cuadruplas):
        self.cuadruplas = cuadruplas
        
        self.in_main = False
        self.in_class_main = False
        self.llamada_main = True
        self.data = {}
        self.nativas = [
            "abort_Object",
            "type_name",
            "copy_Object",
            "length_String",
            "concat_String",
            "substr_String",
            "out_string_IO",
            "in_string_IO",
            "out_int_IO",
            "in_int_IO",
        ]
        self.nativas_original = {
            "abort_Object": "abort",
            "type_name": "type_name",
            "copy_Object": "copy",
            "length_String": "length",
            "concat_String": "concat",
            "substr_String": "substr",
            "out_string_IO": "out_string",
            "in_string_IO": "in_string",
            "out_int_IO": "out_int",
            "in_int_IO": "in_int",
        }
        self.clases_nativas = ["Int", "Boolean", "String", "IO"]
        self.cargar_nativas = []
        self.value_assign = None
        self.current_class = None

        self.contador_direcciones = 0
        self.recolectarInformacionClases()
        self.generarVTables()
        self.t_register = 0
        self.a_register = 0
        self.register_used = 'a'

        self.atributos_clase = {}
        self.funcion_main = False
        self.strings = 0
        
        
        self.texto = self.traducirTAC()
        self.escribiCodigo()
        self.queue = []
        self.parameters = 0



    def traducirTAC(self):
        texto = ""
        temporal = ""
        for cuadrupla in self.cuadruplas:
            if isinstance(cuadrupla, list):
                cuadrupla = cuadrupla[0]

            if cuadrupla.op == "class":
                self.current_class = cuadrupla.arg1

            if cuadrupla.op == "class" and cuadrupla.arg1 == "Main":
                self.in_main = True

            texto_temp = ""
            # if cuadrupla.op in ["heap_declaration"] and self.in_main:
            #     clase = cuadrupla.arg2
            #     variable = cuadrupla.arg1

            #     print(clase, 'clase')
            #     print(variable, 'variable')

            #     queue_temp = self.recorrerCuadruplasCondicion(self.cuadruplas, clase, variable)

            #     print(queue_temp)
            #     if queue_temp != []:
            #         for cuadr in queue_temp:
            #             texto_temp += self.traducirCuadupla(cuadr)

            traducido = self.traducirCuadupla(cuadrupla)
            
            if self.in_class_main:
                texto += traducido
                texto += texto_temp if texto_temp != "" else ""


            else:
                temporal += traducido
                temporal += texto_temp if texto_temp != "" else ""

        texto += "\n\tjr $ra\n"
        texto += temporal

        if self.data != {}:
            texto = self.traducirData() + texto

        if self.cargar_nativas != []:
            texto = texto + self.crearNativas()

        return texto
    
    def generarVTables(self):
        self.VTables = {}
        for clase in self.lista_de_clases:
            vtable = {}
            for metodo in clase.metodos:
                vtable[metodo.nombre] = metodo.nombre
            self.VTables[clase.nombre] = vtable

    def recolectarInformacionClases(self):
        self.lista_de_clases = []
        for cuadrupla in self.cuadruplas:
            if isinstance(cuadrupla, list):
                cuadrupla = cuadrupla[0]
            if cuadrupla.op == "class":
                nombre_clase = cuadrupla.arg1
                metodos = self.obtenerMetodos(nombre_clase)
                clase_base = self.obtenerClaseBase(nombre_clase)
                self.lista_de_clases.append(Clase(nombre_clase, metodos, clase_base))

    def obtenerMetodos(self, nombre_clase):
        metodos = []
        for cuadrupla in self.cuadruplas:
            if isinstance(cuadrupla, list):
                cuadrupla = cuadrupla[0]

            if cuadrupla.op == "func" and cuadrupla.arg1.split('_')[1] == nombre_clase:
                nombre_metodo = cuadrupla.arg1.split('_')[0]
                
                metodos.append(self.asignarDireccionAMetodo(nombre_metodo))
        return metodos
    
    def asignarDireccionAMetodo(self, nombre_metodo):
        direccion = self.contador_direcciones
        self.contador_direcciones += 1
        return Metodo(nombre_metodo, direccion)

    def obtenerClaseBase(self, nombre_clase):
        for cuadrupla in self.cuadruplas:
            if isinstance(cuadrupla, list):
                cuadrupla = cuadrupla[0]
            if cuadrupla.arg2 != None and cuadrupla.arg1 == nombre_clase:
                return cuadrupla.arg2  # Suponiendo que 'arg2' contiene el nombre de la clase base
        return None  # Si no hay herencia

    def crearNativas(self):
        cargadas = []
        texto = ""
        for nativa in self.cargar_nativas:
            if nativa not in cargadas:
                cargadas.append(nativa)

                if nativa == "abort_Object":
                    pass
                elif nativa == "type_name":
                    pass
                elif nativa == "copy_Object":
                    pass
                elif nativa == "length_String" or nativa == "length_String_IO":
                    texto += self.stringLength()
                elif nativa == "concat_String" or nativa == "concat_String_IO":
                    texto += self.concat()
                elif nativa == "substr_String" or nativa == "substr_String_IO":
                    texto += self.substr()
                elif nativa == "out_string" or nativa == "out_string_IO":
                    texto += self.outString()
                elif nativa == "in_string_IO" or nativa == "in_string":
                    texto += self.inString()
                elif nativa == "out_int_IO" or nativa == "out_int":
                    texto += self.outInt()
                elif nativa == "in_int_IO" or nativa == "in_int":
                    texto += self.inInt()
        return texto
                
    def traducirData(self):
        texto = ".data\n"
        for key in self.data:
            tipo = self.data[key]["type"]
            valor = self.data[key]["value"]
            texto += f"{key}: {tipo} {valor}\n"

        for clase in self.lista_de_clases:
            texto += f"{clase.nombre}_vtable:\n"
            for metodo in clase.metodos:
                texto += f"\t.word {metodo.nombre}_{clase.nombre}\n"  # Suponiendo que el nombre del método es también la etiqueta de su código MIPS
        

        texto += "newline: .asciiz \"\\n\"\n"
        texto += "\n\n"
        return texto

    # def recorrerCuadruplasCondicion(self, cuadruplas, clase, variable):
    #     encontro_clase = False
    #     queue_temp = []
    #     for cuadrupla in cuadruplas:
            
    #         if isinstance(cuadrupla, list):
    #             cuadrupla = cuadrupla[0]

    #         temp = cuadrupla.copy()

    #         if encontro_clase and cuadrupla.op in ["class", "func"]:
    #             break

    #         if cuadrupla.arg1 == clase and cuadrupla.op == "class":
    #             encontro_clase = True

    #         if encontro_clase and cuadrupla.op in ["heap_declaration"]:
    #             temp.arg1 = temp.arg1 + "_" + variable

    #             queue_temp.append(temp)
        
    #     return queue_temp

    # El string debe estar en $a0
    def stringLength(self):
        texto = ""
        # Funcion length
        texto += "\n\n length:\n"
        texto += "\tli $v0, 0\n"
        texto += "\tli $t0, 0\n"


        texto += "\n\n\tloopLength:\n"
        texto += "\t\tlb $t1, 0($a0)\n"
        texto += "\t\tbeqz $t1, endLength\n"
        texto += "\t\taddi $v0, $v0, 1\n"
        texto += "\t\taddi $a0, $a0, 1\n"
        texto += "\t\tj loopLength\n"

        texto += "\n\n\tendLength:\n"
        texto += "\t\tjr $ra\n\n"

        return texto

    def concat(self):
        self.data["buffer"] = {"type": ".space", "value": "100"}
        texto = ""

        texto += "\n\nconcat:\n"
        texto += "\tla $t0, buffer\n"

        texto += "\n\n\tloopConcat:\n"
        texto += "\t\tlb $t1, 0($a0)\n"
        texto += "\t\tbeqz $t1, nextConcat\n"
        texto += "\t\tsb $t1, 0($t0)\n"
        texto += "\t\taddi $a0, $a0, 1\n"
        texto += "\t\taddi $t0, $t0, 1\n"
        texto += "\t\tj loopConcat\n"

        texto += "\n\n\tnextConcat:\n"
        texto += "\t\tlb $t1, 0($a1)\n"
        texto += "\t\tbeqz $t1, endConcat\n"
        texto += "\t\tsb $t1, 0($t0)\n"
        texto += "\t\taddi $a1, $a1, 1\n"
        texto += "\t\taddi $t0, $t0, 1\n"
        texto += "\t\tj nextConcat\n"

        texto += "\n\n\tendConcat:\n"
        texto += "\t\tsb $zero, 0($t0)\n"
        texto += "\t\tla $v0, buffer\n"
        texto += "\t\tjr $ra\n\n"

        return texto
    
    def substr(self):
        if "buffer" not in self.data.keys():
            self.data["buffer"] = {"type": ".space", "value": "100"}
        
        texto = ""

        texto += "\n\nsubstr:\n"
        texto += "\tla $t0, buffer\n"
        texto += "\tadd $t1, $zero, $a1"

        texto += "\n\n\tloopSubstr:\n"
        texto += "\t\tbge $t1, $a2, endSubstr\n"
        texto += "\t\tadd $t2, $a0, $t1\n"
        texto += "\t\tlb $t3, 0($t2)\n"
        texto += "\t\tbeqz $t3, endSubstr\n"
        texto += "\t\tsb $t3, 0($t0)\n"
        texto += "\t\taddi $t0, $t0, 1\n"
        texto += "\t\taddi $t1, $t1, 1\n"
        texto += "\t\tj loopSubstr\n"


        texto += "\n\n\tendSubstr:\n"
        texto += "\t\tsb $zero, 0($t0)\n"
        texto += "\t\tla $v0, buffer\n"
        texto += "\t\tjr $ra\n\n"

        return texto

    def outString(self):
        texto = ""
        
        texto += "\n\nout_string:\n"
        texto += "\tli $v0, 4\n"
        texto += "\tsyscall\n"
        texto += "\tjr $ra\n\n"

        return texto
    
    def outInt(self):
        texto = ""

        texto += "\n\nout_int:\n"
        texto += "\tli $v0, 1\n"
        texto += "\tsyscall\n"

        texto += "\n\tla $a0, newline\n"
        texto += "\tli $v0, 4\n"
        texto += "\tsyscall\n"

        texto += "\tjr $ra\n\n"


        return texto
    
    def inInt(self):
        texto = ""

        texto += "\n\nin_int:\n"
        texto += "\tli $v0, 5\n"
        texto += "\tsyscall\n"
        texto += "\tjr $ra\n\n"

        return texto
    
    def inString(self):
        if "buffer" not in self.data.keys():
            self.data["buffer"] = {"type": ".space", "value": "100"}
        
        texto = ""

        texto += "\n\nin_string:\n"
        texto += "\tla $a0, buffer\n"
        texto += "\tli $a1, 100\n"
        texto += "\tli $v0, 8\n"
        texto += "\tsyscall\n"
        texto += "\tjr $ra\n\n"

        return texto
    
    def calcularOffsetMetodo(self, nombre_clase, nombre_metodo):
        offset = 0
        tamaño_palabra = 4  # Tamaño de una palabra en MIPS (32 bits = 4 bytes)

        # Encuentra la clase correspondiente
        clase = next((clase for clase in self.lista_de_clases if clase.nombre == nombre_clase), None)
        if clase is None:
            return None  # Clase no encontrada

        # Calcula el offset buscando la posición del método en la lista de métodos
        for metodo in clase.metodos:
            if metodo.nombre == nombre_metodo:
                return offset
            offset += tamaño_palabra
    
        return None  # Método no encontrado en la clase

    def traducirCuadupla(self, cuadrupla):
        texto = ""
        operador = cuadrupla.op
        arg1 = cuadrupla.arg1
        arg2 = cuadrupla.arg2
        res = cuadrupla.res
        

        if arg1 == "false":
            arg1 = 0
        elif arg1 == "true":
            arg1 = 1

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

            texto += "\n\n"+nombre + ":\n"

        elif operador == "=" and arg1 != None:
            # Si es un numero usar li, sino usar la
            try:
                int(arg1)
                texto += f"\tli ${res}, {arg1} \n\n"
            except:
                if arg1 == "true":
                    texto += f"\tli ${res}, 1 \n\n"

                elif arg1 == "false":
                    texto += f"\tli ${res}, 0 \n\n"
                # Si tiene el formato "{texto}" entonces es un string
                
                elif arg1[0] == "\"" and arg1[-1] == "\"":
                    pass

                else:
                    # # if arg1==res:
                    # #     texto+=f"\tlw $t0, {arg1}_{self.current_class}_address\n"
                    # #     texto+=f"\tsw $v0, 0($t0)\n\n"
                    texto+=f"\tlw $t0, {arg1}_{self.current_class}_address\n"
                    texto+=f"\tmove $t1, $v0\n"
                    texto+=f"\tsw $t1, 0($t0)\n\n"
                    
                    # if arg1!=res:    
                    #     texto += f"\tla ${res}, {arg1} \n"
                        
                    #     # cargar el valor en la direccion de memoria con lw
                    #     texto += f"\tlw ${res}, 0(${res})\n\n"


        elif operador == "+":

            texto += "\tadd $a0, $" + str(arg1) + ", $" + str(arg2) + "\n\n"

        elif operador == "/":

            texto += "\tdiv $" + str(arg1) + ", $" + str(arg2) + "\n\n"
            texto += "\tmfhi $t0\n\n"
        
        elif operador == "*":
            texto += "\tmult $" + str(arg1) + ", $" + str(arg2) + "\n\n"
            texto += "\tmflo $t0\n\n"

       
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
            palabras = arg1.split("_")
            if len(palabras) > 2:
                objeto = palabras[-1]

                palabas_metodo = palabras[:-1]
                metodo = "_".join(palabas_metodo)
            else:
                objeto = arg1.split('_')[1]
                metodo = arg1.split('_')[0]

            if arg1 in self.nativas:
                self.register_used = 'a'
                nombre = self.nativas_original[arg1]
                texto += "\tjal " + nombre + "\n\n"
                self.cargar_nativas.append(arg1)


            else:
                #print(cuadrupla)
                offset = self.calcularOffsetMetodo(objeto, metodo)
                if offset is not None:
                    self.register_used = 'a'
                    texto += f"\tlw $t0, {objeto}_vtable\n"
                    texto += f"\tmove $t1, $t0\n"

                    if offset > 0:
                        texto += f"\tlw $t2, {offset}($t1)\n"
                        texto += "\tjal $t2\n\n"
                    else:
                        texto += "\tjal $t1\n\n"

                else:
                    # Si no se encontró el método en la clase, buscar en la clase base
                    clase = next((clase for clase in self.lista_de_clases if clase.nombre == objeto), None)
                    if clase is None:
                        pass

                    clase_base = clase.clase_base
                    
                    if clase_base in self.clases_nativas:
                        self.register_used = 'a'
                        texto += "\tjal " + metodo + "\n\n"
                        self.cargar_nativas.append(metodo)
                        
                    else:
                        offset = self.calcularOffsetMetodo(clase_base, metodo)
                        if offset is not None:
                            self.register_used = 'a'
                            texto += f"\tlw $t0, {objeto}_vtable\n"
                            texto += f"\tmove $t1, $t0\n"

                            if offset > 0:
                                texto += f"\tlw $t2, {offset}($t1)\n"
                                texto += "\tjal $t2\n\n"
                            else:
                                texto += "\tjal $t1\n\n"

                        else:
                            pass
                    

                
        elif operador == "reserve_space":
            if self.register_used=='t':
                texto += f"\taddiu $sp, $sp, -{arg1}\n\n"
        
        elif operador == "param":
            if self.register_used == 't':
                texto += f"\tli $t0, {arg1}_{self.current_class}_address\n"
                texto += f"\tsw $t0, {res}($sp)\n"
            elif self.register_used == 'a':
                try:
                    int(arg1)
                    texto += f"\tli ${self.register_used}{self.a_register}, {arg1}\n"
                except:

                    # si es un string cargar la direccion de memoria y crear un espacio
                    if arg1[0] == "\"" and arg1[-1] == "\"":
                        self.strings += 1
                        nombre = f"string_{self.strings}"
                        texto += f"\tla $a0, {nombre}\n"
                        self.data[nombre] = {"type": ".asciiz", "value": arg1}

                    else:
                        if f"{arg1}_{self.current_class}_address" in self.data.keys() and self.data[f"{arg1}_{self.current_class}_address"]["type"] == ".asciiz":
                            texto += f"\tla ${self.register_used}{self.a_register}, {arg1}_{self.current_class}_address\n"
                        
                        else:
                            texto += f"\tlw $t0, {arg1}_{self.current_class}_address\n"	
                            texto += f"\tlw ${self.register_used}{self.a_register}, 0($t0)\n\n"


        # elif operador == "param":
        #     self.parameters += 1
        elif operador == "param_decl":
            if self.register_used == 'a' and self.a_register== 4:
                self.register_used = 't'
                self.a_register = 0
                self.t_register = 0
                
            if self.register_used == 't':
                texto += f"\tlw ${self.register_used}{self.t_register}, {res}($sp)\n"
                self.t_register += 1

            
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
                texto += f"\tli $v0, {arg1} \n"
            except:

                # si es un string cargar la direccion de memoria y crear un espacio
                if arg1[0] == "\"" and arg1[-1] == "\"":
                    self.strings += 1
                    nombre = f"string_{self.strings}"
                    texto += f"\tla $a0, {nombre}\n"
                    self.data[nombre] = {"type": ".asciiz", "value": arg1}
                
                else:
                    texto += f"\tla $a0, {arg1}_{self.current_class}_address \n"
                    
                    # cargar el valor en la direccion de memoria con lw
                    texto += f"\tlw $a0, 0($a0)\n\n"
        
        elif operador == "ifFalse":

            try:
                int(arg1)
                texto += f"\tli $t0, {arg1} \n"
            
            except:
                texto += f"\tla $t0, {arg1}_{self.current_class}_address \n"
                
                # cargar el valor en la direccion de memoria con lw
                texto += f"\tlw $t0, 0($t0)\n\n"

            
            texto += f"\tbeqz $t0, {res}\n\n"

        elif operador == "value_assign":
            self.value_assign = res
            
        # elif operador == "heap_declaration":
        #     espacio = res
        #     nombre = arg1 

        #     texto += "\tli $a0, " + str(espacio) + "\n"
        #     texto += "\tli $v0, 9\n"
        #     texto += "\tsyscall\n"
        #     texto += "\tla $t0, " + nombre + "_address\n"
        #     texto += "\tsw $v0, 0($t0)\n\n"

        #     # Asignando el valor
        #     texto += f"\tli $t1, {self.value_assign}\n\n"
        #     texto += f"\tsw $t1, 0($v0)\n\n"
        #     self.value_assign = None

        #     return texto

        # elif operador == "heap_declaration" and not self.in_main:
        #     espacio = res
        #     nombre = arg1 
        #     tipo = arg2
        #     print(cuadrupla)
        #     temporal = self.traducirCuadupla(cuadrupla)

        #     print(temporal)

        #     self.atributos_clase[self.current_class] = []

        elif operador == "heap_declaration":
            espacio = res
            nombre = arg1 
            tipo = arg2

            temporal = ""

            if not self.in_class_main:
                temporal += "\tli $a0, " + str(espacio) + "\n"
                temporal += "\tli $v0, 9\n"
                temporal += "\tsyscall\n"
                temporal += f"\tsw $v0, {nombre}_{self.current_class}_address\n\n"

                # Cargar la direccion de la VTable
                if tipo not in ["Int", "Bool", "String", "IO"]:
                    temporal += f"\tla $t0, {tipo}_vtable\n"
                    temporal += f"\tsw $t0, 0($v0)\n\n"

                self.atributos_clase[self.current_class] = nombre

            else:

                texto += "\tli $a0, " + str(espacio) + "\n"
                texto += "\tli $v0, 9\n"
                texto += "\tsyscall\n"
                texto += f"\tsw $v0, {nombre}_{self.current_class}_address\n\n"

                # Cargar la direccion de la VTable
                if tipo not in ["Int", "Bool", "String", "IO"]:
                    texto += f"\tla $t0, {tipo}_vtable\n"
                    texto += f"\tsw $t0, 0($v0)\n\n"

                if self.current_class in self.atributos_clase.keys():
                    texto += self.atributos_clase[self.current_class]
            
            # texto += temporal

            #  # Asignando el valor
            # texto += f"\tli $t1, {self.value_assign}\n\n"
            # texto += f"\tsw $t1, 0($v0)\n\n"
            # self.value_assign = None
            if self.value_assign is not None:

                try:
                    int(self.value_assign)
                    texto += f"\tli $t1, {self.value_assign}\n\n"
                    texto += f"\tsw $t1, 0($v0)\n\n"
                    self.data[nombre +"_"+self.current_class+"_address"] = {"type": ".word", "value": self.value_assign}
                except:
                # si es un string cargar la direccion de memoria y crear un espacio
                    if self.value_assign[0] == "\"" and self.value_assign[-1] == "\"":
                        self.data[nombre +"_"+self.current_class+"_address"] = {"type": ".asciiz", "value": self.value_assign}
            else:
                self.data[nombre +"_"+self.current_class+"_address"] = {"type": ".word", "value": "0"}
        

        elif operador == "stack_declaration":
            espacio = res
            nombre = arg1 

            texto += "\taddi $sp, $sp, -" + str(espacio) + "\n"
            texto += f"\tli $t0, {self.value_assign}\n\n"
            texto += f"\tsw $t0, 0($sp)\n\n"

            self.value_assign = None
            return texto



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

                
        