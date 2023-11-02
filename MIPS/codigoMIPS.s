.text
.globl main
main:
	li $a0, 8
	li $v0, 9
	syscall
	sw $v0, prueba_address

	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, y_prueba_address

	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, z_prueba_address

	li $a0, 8
	li $v0, 9
	syscall
	sw $v0, x_address

	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, y_x_address

	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, z_x_address

	jal Main_main

	li $v0, 10
	syscall

main_Main:
	jal hola_Prueba

otra_Main:
	li $a2, 5 
	li $a3, 5 
	add $a0, $a2, $a3

hola_Prueba:
	li $z, 6 
	li $y, 5 
	add $a0, $a2, $a3

	la $a2, a3 
	lw $a2, 0($a2)

	la $a3, a4 
	lw $a3, 0($a3)

otra_Prueba:
	li $a2, 5 
	li $a3, 5 
	add $a0, $a2, $a3

