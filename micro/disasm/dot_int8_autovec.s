# ===== dot_autovec: hot loop = the 7 instructions of the innermost conditional backward branch holding the expected instruction (none (recorded)) =====
#   ld1b {z2.b}, p0/z, [x2, x0]
#   ld1b {z0.b}, p0/z, [x1, x0]
#   add x0, x0, x3
#   sel z0.b, p0, z0.b, z3.b
#   whilelo p0.b, x0, x4
#   sdot z1.s, z2.b, z0.b
#   b.ne 76c0 <dot_autovec+0x40>
# ===== whole function =====

/home/adnancheema917/edge-llm-on-arm/work/bin/dot_int8:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000007680 <dot_autovec>:
    7680:	cmp	x3, #0x0
    7684:	b.le	76f0 <dot_autovec+0x70>
    7688:	mov	x5, x2
    768c:	mov	x2, x0
    7690:	whilelo	p2.b, xzr, x4
    7694:	mov	z3.b, #0
    7698:	ptrue	p1.b
    769c:	add	x6, x5, x3, lsl #2
    76a0:	cntb	x3
    76a4:	cmp	x4, #0x0
    76a8:	b.le	76f4 <dot_autovec+0x74>
    76ac:	mov	x0, #0x0                   	// #0
    76b0:	mov	p0.b, p2.b
    76b4:	mov	z1.b, #0
    76b8:	nop
    76bc:	nop
    76c0:	ld1b	{z2.b}, p0/z, [x2, x0]
    76c4:	ld1b	{z0.b}, p0/z, [x1, x0]
    76c8:	add	x0, x0, x3
    76cc:	sel	z0.b, p0, z0.b, z3.b
    76d0:	whilelo	p0.b, x0, x4
    76d4:	sdot	z1.s, z2.b, z0.b
    76d8:	b.ne	76c0 <dot_autovec+0x40>  // b.any
    76dc:	uaddv	d1, p1, z1.s
    76e0:	add	x2, x2, x4
    76e4:	str	s1, [x5], #4
    76e8:	cmp	x6, x5
    76ec:	b.ne	76a4 <dot_autovec+0x24>  // b.any
    76f0:	ret
    76f4:	fmov	s1, wzr
    76f8:	b	76e0 <dot_autovec+0x60>

Disassembly of section .fini:
