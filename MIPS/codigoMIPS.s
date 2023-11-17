.data
x_Util_address: .word 3
str_Main_address: .word 0
hola_Main_address: .word 0
x_Main_address: .word 0
y_Main_address: .word 0
string_1: .asciiz "Ingrese un numero: "
string_2: .asciiz "El valor de x es: "
string_3: .asciiz "El valor ingresado es: "
Util_vtable:
	.word test_Util
Main_vtable:
	.word main_Main
newline: .asciiz "\n"


.text
.globl main
main:
	li $a0, 14
	li $v0, 9
	syscall
	sw $v0, str_Main_address

	la $t0, Util_vtable
	sw $t0, 0($v0)

	li $a0, 14
	li $v0, 9
	syscall
	sw $v0, hola_Main_address

	la $t0, Util_vtable
	sw $t0, 0($v0)

	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, x_Main_address

	li $a0, 4
	li $v0, 9
	syscall
	sw $v0, y_Main_address

	jal main_Main

	li $v0, 10
	syscall


main_Main:
	lw $t0, Util_vtable
	move $t1, $t0
	jal $t1

	lw $t0, x_Main_address
	move $t1, $v0
	sw $t1, 0($t0)

	la $a0, string_1
	jal out_string

	jal in_int

	lw $t0, y_Main_address
	move $t1, $v0
	sw $t1, 0($t0)

	la $a0, string_2
	jal out_string

	lw $t0, x_Main_address
	lw $a0, 0($t0)

	jal out_int

	la $a0, string_3
	jal out_string

	lw $t0, y_Main_address
	lw $a0, 0($t0)

	jal out_int

	li $v0, 1 

	jr $ra


test_Util:
	li $v0, 2 
	jr $ra



out_string:
	li $v0, 4
	syscall
	jr $ra



in_int:
	li $v0, 5
	syscall
	jr $ra



out_int:
	li $v0, 1
	syscall

	la $a0, newline
	li $v0, 4
	syscall
	jr $ra

