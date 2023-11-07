.text
.globl main
main:
	jal main_Main

	li $v0, 10
	syscall


main_Main:
	li $a2, 1 
	li $a3, 7 
	add $a0, $a2, $a3

	jr $ra

