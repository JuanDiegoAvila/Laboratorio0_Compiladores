.data
x_Util_address: .word 3
str_Main_address: .word 0
y_Main_address: .word 0
Util_vtable:
	.word test_Util
Main_vtable:
	.word main_Main


.text
.globl main
main:
	li $a0, 14
	li $v0, 9
	syscall
	sw $v0, str_Main_address

	la $t0, Util_vtable
	sw $t0, 0($v0)

	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, y_Main_address

	jal main_Main

	li $v0, 10
	syscall


main_Main:
	jal in_int

	lw $t0, y_Main_address
	sw $v0, 0($t0)
	move $a0, $v0
	jal out_int

	li $a0, 1 


test_Util:
	li $a0, 2 
	jr $ra



in_int:
	li $v0, 5
	syscall
	jr $ra



out_int:
	li $v0, 1
	syscall
	jr $ra

