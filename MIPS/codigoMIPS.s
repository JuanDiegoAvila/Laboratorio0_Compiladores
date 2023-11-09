.text
.globl main
main:
	jal main_Main

	li $v0, 10
	syscall


main_Main:
	li $a2, 1 
	li $a3, 0 
	slt $a4, $a2, $a3
	xori $a4, $a4, 0x1
	beqz $t0, L2

	li $a0, 3 
	j L1


L2:
	li $a0, 1 


L1:
	jr $ra

