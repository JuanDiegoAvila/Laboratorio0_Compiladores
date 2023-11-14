.data
Otra_vtable:
	.word otra
Main_vtable:
	.word main


.text
.globl main
main:
	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, str_address

	jal main_Main

	li $v0, 10
	syscall


main_Main:
	addiu $sp, $sp, -8
	li $t0, 1
	sw $t0, 0($sp)
	li $t0, 2
	sw $t0, 4($sp)
	jal otra_Otra

	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, x_address



otra_Otra:
	lw $a0, 0($sp)
	lw $a1, 4($sp)
	li $a0, 3 
	jr $ra

