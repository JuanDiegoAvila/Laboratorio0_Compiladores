.text
.globl main
main:
	jal main_Main        # Llama a la subrutina main_Main

	li $v0, 1           # Prepara la syscall para imprimir un entero
	syscall             # Imprime el valor retornado por main_Main en $a0
	
	li $v0, 10          # Prepara la syscall para terminar el programa
	syscall             # Termina el programa

main_Main:
	li $t0, 1           # Establece $t0 a 1
	beqz $t0, L2        # Si $t0 es cero (lo cual nunca es cierto), salta a L2

	li $a0, 2           # Establece el valor a devolver a 2
	j L1                # Salta a la etiqueta L1 para retornar

L2:
	li $a0, 1           # Esto nunca se ejecutará, pero si lo hiciera, establecería el valor a devolver a 1

L1:
	jr $ra              # Devuelve control al llamador (main)