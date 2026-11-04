# ===== dot_scalar: hot loop = the 6 instructions of the innermost conditional backward branch holding the expected instruction (no SIMD multiply) =====
#   ldrsb w5, [x6, x0]
#   ldrsb w3, [x1, x0]
#   add x0, x0, #0x1
#   madd w2, w5, w3, w2
#   cmp x4, x0
#   b.ne 7630 <dot_scalar+0x30>
# ===== whole function =====

/home/adnancheema917/edge-llm-on-arm/work/bin/dot_int8:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000007600 <dot_scalar>:
    7600:	cmp	x3, #0x0
    7604:	b.le	7658 <dot_scalar+0x58>
    7608:	add	x8, x2, x3, lsl #2
    760c:	mov	x7, x2
    7610:	mov	x6, x0
    7614:	nop
    7618:	nop
    761c:	nop
    7620:	cmp	x4, #0x0
    7624:	b.le	765c <dot_scalar+0x5c>
    7628:	mov	x0, #0x0                   	// #0
    762c:	mov	w2, #0x0                   	// #0
    7630:	ldrsb	w5, [x6, x0]
    7634:	ldrsb	w3, [x1, x0]
    7638:	add	x0, x0, #0x1
    763c:	madd	w2, w5, w3, w2
    7640:	cmp	x4, x0
    7644:	b.ne	7630 <dot_scalar+0x30>  // b.any
    7648:	add	x6, x6, x4
    764c:	str	w2, [x7], #4
    7650:	cmp	x8, x7
    7654:	b.ne	7620 <dot_scalar+0x20>  // b.any
    7658:	ret
    765c:	mov	w2, #0x0                   	// #0
    7660:	add	x6, x6, x4
    7664:	str	w2, [x7], #4
    7668:	cmp	x8, x7
    766c:	b.ne	7620 <dot_scalar+0x20>  // b.any
    7670:	b	7658 <dot_scalar+0x58>

Disassembly of section .fini:
