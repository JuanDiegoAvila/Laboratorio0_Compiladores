.data
num1: .word 40  # Primer numero
num2: .word 10  # Segundo numero

.text
.globl main
main:
    # Se cargan los valores en registros
    la $a0, num1 # Se carga la direccion de memoria de num1 en $a0
    lw $a0, 0($a0) # Se carga el valor de num1 en $a0
    
    la $a1, num2 # Se carga la direccion de memoria de num2 en $a1
    lw $a1, 0($a1) # Se carga el valor de num2 en $a1

    # Se llama a la funcion recursiva de gcd
    jal gcd

    # Funcion de salida
    move $a0, $v0 # Se mueve el valor de retorno de gcd a $a0
    li $v0, 1 # Se carga el codigo de salida para imprimir un valor entero
    syscall # Se llama a la funcion de salida

    li $v0, 10 # Se carga el codigo de salida para terminar el programa
    syscall # Se llama a la funcion de salida

gcd:
    # Comprobar caso base (a1 == 0)
    beq $a1, $zero, done # Si a1 == 0, se retorna el valor de a0

    # Guardar los registros en la pila
    subu $sp, $sp, 12 # Se reserva espacio en la pila
    sw $ra, 8($sp)  # Se guarda el valor de $ra en la pila
    sw $a0, 4($sp)  # Se guarda el valor de $a0 en la pila
    sw $a1, 0($sp)  # Se guarda el valor de $a1 en la pila

    # Calcular el residuo
    divu $a0, $a1  # Se divide $a0 entre $a1
    mfhi $t0 # Se guarda el residuo en $t0

    # Preparar argumentos para la próxima recursión
    move $a0, $a1 # Se mueve el divisor a $a0
    move $a1, $t0 # Se mueve el residuo a $a1

    # Llamada recursiva
    jal gcd 

    # Restaurar los registros de la pila
    lw $a1, 0($sp) # Se carga el valor de $a1 desde la pila
    lw $a0, 4($sp) # Se carga el valor de $a0 desde la pila
    lw $ra, 8($sp) # Se carga el valor de $ra desde la pila
    addu $sp, $sp, 12 # Se libera el espacio de la pila

    # Retorno
    jr $ra # Se retorna al main

done:
    # En este punto, a0 contiene el MCD
    move $v0, $a0 # Se mueve el MCD a $v0
    jr $ra # Se retorna al main
