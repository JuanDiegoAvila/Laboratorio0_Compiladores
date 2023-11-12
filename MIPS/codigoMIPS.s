.data
x_address: .word 0


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
	jal otra_Otra

	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, x_address



otra_Otra:
	li $a0, 3 
	jr $ra

