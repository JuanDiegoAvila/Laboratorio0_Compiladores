.text
.globl main
main:
	li $a2, 1 
	lw $a2, 0($a2)

	li $a3, 2 
	lw $a3, 0($a3)

	add $a0, $a2, $a3


division:
	li $a2, 5 
	lw $a2, 0($a2)

	li $a3, 5 
	lw $a3, 0($a3)

	div $a2, $a3
	mfhi $t0
