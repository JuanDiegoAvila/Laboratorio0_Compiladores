.data
a_size: .word 4
b_size: .word 4
c_size: .word 4

.text
.globl main

main:
    # Asignar espacio en el heap para 'a'
    lw $a0, a_size
    li $v0, 9
    syscall
    move $t0, $v0  # Guardar la dirección de 'a' en $t0

    # Asignar espacio en el heap para 'b'
    lw $a0, b_size
    li $v0, 9
    syscall
    move $t1, $v0  # Guardar la dirección de 'b' en $t1

    # Asignar espacio en el heap para 'c'
    lw $a0, c_size
    li $v0, 9
    syscall
    move $t2, $v0  # Guardar la dirección de 'c' en $t2

    # Inicializar 'a' y 'b'
    li $t3, 5       # Supongamos que 'a' es 5
    sw $t3, 0($t0) # Almacenar 'a' en el heap

    li $t3, 10      # Supongamos que 'b' es 10
    sw $t3, 0($t1) # Almacenar 'b' en el heap

    # Cargar 'a' y 'b' desde el heap
    lw $t3, 0($t0) # Cargar 'a'
    lw $t4, 0($t1) # Cargar 'b'

    # Sumar 'a' y 'b'
    add $t5, $t3, $t4

    # Almacenar el resultado en 'c'
    sw $t5, 0($t2)

    # Aquí el resultado de 'a + b' está en 'c' y en $t5
