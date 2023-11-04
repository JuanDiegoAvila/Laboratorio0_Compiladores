.text
.globl main
main:
	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, x_address

	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, y_address

	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, z_address

	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, p_address

	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, a_address

	li $a0, 0
	li $v0, 9
	syscall
	sw $v0, print_address

hola_Main:
	jal Main_main

	li $v0, 10
	syscall

main_Main:
	jal copy_Int

	li $a2, 1 
	la $a3, false 
	lw $a3, 0($a3)

	mult $a2, $a3

	mflo $t0

	la $a2, a3 
	lw $a2, 0($a2)

	la $a3, a4 
	lw $a3, 0($a3)

	add $a0, $a2, $a3

	la $a2, a4 
	lw $a2, 0($a2)

	li $a3, 3 
	la $a2, a4 
	lw $a2, 0($a2)

	li $a3, 3 
	li $a2, 2 
	li $a3, 3 
	mult $a2, $a3

	mflo $t0

	la $a2, a3 
	lw $a2, 0($a2)

	la $a3, a4 
	lw $a3, 0($a3)

	add $a0, $a2, $a3

	la $a2, a4 
	lw $a2, 0($a2)

	li $a3, 4 
	la $a2, a4 
	lw $a2, 0($a2)

	li $a3, 4 
	la $x, y 
	lw $x, 0($x)

	li $a2, 5 
	li $a3, 0 
	jal out_string_IO

	la $x, y 
	lw $x, 0($x)

	li $x, 1 
	li $x, 2 
