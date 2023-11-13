#####################################################################
# Cross References:
# v0: N,
# t0: Sum
#####################################################################
    .data
prompt: .asciiz "\n Please Input a value for N = "
result: .asciiz " The sum of the integers from 1 to N is "
bye: .asciiz "\n **** Adios Amigo - Have a good day ****"
        .globl main
        .text
main:
    addiu $sp, $sp, -8

    li $t0, 5
    sw $t0, 0($sp)
    li $t0, 6
    sw $t0, 4($sp)
    jal print_number
    addiu $sp, $sp, 8

print_number:
    lw $t0, 4($sp)
    lw $t1, 0($sp)

    move $a0, $t0

    li $v0, 1
    syscall

    move $a0, $t1

    li $v0, 1
    syscall

    li $v0, 10
    syscall