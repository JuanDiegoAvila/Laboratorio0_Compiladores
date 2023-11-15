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
	li $a0, 5
	jal out_int

	li $a0, 1 
	jr $ra



out_int:
	li $v0, 1
	syscall
	jr $ra

