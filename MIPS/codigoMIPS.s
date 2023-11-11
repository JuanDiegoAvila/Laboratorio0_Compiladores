.text
.globl main
main:
	jal main_Main

	li $v0, 10
	syscall


main_Main:
	li $a2, 1 
	li $a3, 0 
	sub $t0, $a2, $a3
	slti $t1, $t0, 0
	seq $t0, $t0, 0
	or $t0, $t0, $t1

	move $a0, $t0
	li $v0, 1
	syscall

	jr $ra

	li $a0, 3 
	j L1


L2:
	li $a0, 1 


L1:
	jr $ra

