.global main
.type main, @function
.extern print_int
.section .text
main:
pushq %rbp
movq %rsp, %rbp
subq $128, %rsp
# FunctionDefinition(name='square', label=L1)
square:
# Call(fun=*, args=[x1, x1], dest=x2)
movq -16(%rbp), %rax
imulq -16(%rbp), %rax
movq %rax, -24(%rbp)
ret
# LoadIntConst(value=2, dest=x3)
movq $2, -32(%rbp)
# Copy(source=x3, dest=x4)
movq -32(%rbp), %rax
movq %rax, -40(%rbp)
# LoadIntConst(value=2, dest=x5)
movq $2, -48(%rbp)
# Call(fun=square, args=[x5], dest=x6)
movq -48(%rbp), %rdi
call square
movq %rax, -64(%rbp)
movq $0, %rax
movq %rbp, %rsp
popq %rbp
ret

