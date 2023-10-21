.data
num1: .word 40
num2: .word 10

.text
.globl main
main:
    la $a0, num1
    lw $a0, 0($a0)

    la $a1, num2
    lw $a1, 0($a1)

    jal sum

    move $a0, $v0
    li $v0, 1
    syscall

    li $v0, 10
    syscall


sum:
    # subu $sp, $sp, 12
    # sw $ra, 8($sp)
    # sw $a0, 4($sp)
    # sw $a1, 0($sp)

    add $v0, $a0, $a1

    # move $v0, $s0

    # lw $ra, 8($sp)
    # lw $a0, 4($sp)
    # lw $a1, 0($sp)
    # addu $sp, $sp, 12
    
    jr $ra


