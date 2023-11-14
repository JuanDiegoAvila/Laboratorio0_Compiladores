.data
str_address: .word 0
Main_vtable:
	.word main_Main


.text
.globl main
main:
	li $a0, 0
	li $v0, 9
	syscall
	sw $v0, str_address

	jal main_Main

	li $v0, 10
	syscall


main_Main:
	# addiu $sp, $sp, -0
	# li $t0, 1
	# sw $t0, None($sp)
	# jal out_int

	# li $a0, 1 
	# jr $ra
	li $a0, 1        # Cargamos el argumento para out_int (1)
    jal out_int       # Llamamos a outInt
    li $v0, 1        # Preparamos el valor de retorno (1)
    jr $ra           # Retornamos



out_int:
	li $v0, 1
	syscall
	jr $ra

