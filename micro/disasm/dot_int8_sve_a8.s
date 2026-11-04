# ===== dot_sve_a8: hot loop = the 29 instructions of the innermost conditional backward branch holding the expected instruction (sdot z-form) =====
#   ld1b {z18.b}, p0/z, [x2]
#   ld1b {z17.b}, p0/z, [x0]
#   sdot z0.s, z17.b, z18.b
#   ld1b {z16.b}, p0/z, [x0, #1, mul vl]
#   add x3, x3, x5
#   ld1b {z18.b}, p0/z, [x2, #1, mul vl]
#   sdot z7.s, z16.b, z18.b
#   ld1b {z17.b}, p0/z, [x0, #2, mul vl]
#   ld1b {z16.b}, p0/z, [x0, #3, mul vl]
#   ld1b {z18.b}, p0/z, [x2, #2, mul vl]
#   sdot z6.s, z17.b, z18.b
#   ld1b {z17.b}, p0/z, [x0, #4, mul vl]
#   ld1b {z18.b}, p0/z, [x2, #3, mul vl]
#   sdot z5.s, z16.b, z18.b
#   ld1b {z16.b}, p0/z, [x0, #5, mul vl]
#   ld1b {z18.b}, p0/z, [x2, #4, mul vl]
#   sdot z4.s, z17.b, z18.b
#   ld1b {z17.b}, p0/z, [x0, #6, mul vl]
#   ld1b {z18.b}, p0/z, [x2, #5, mul vl]
#   sdot z3.s, z16.b, z18.b
#   ld1b {z16.b}, p0/z, [x0, #7, mul vl]
#   add x0, x0, x5
#   ld1b {z18.b}, p0/z, [x2, #6, mul vl]
#   sdot z2.s, z17.b, z18.b
#   ld1b {z17.b}, p0/z, [x2, #7, mul vl]
#   add x2, x2, x5
#   sdot z1.s, z16.b, z17.b
#   cmp x4, x3
#   b.gt 55c0 <dot_sve_a8+0x58>
# ===== whole function =====

/home/adnancheema917/edge-llm-on-arm/work/bin/dot_int8:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000005568 <dot_sve_a8>:
    5568:	cmp	x3, #0x0
    556c:	b.le	5664 <dot_sve_a8+0xfc>
    5570:	add	x8, x2, x3, lsl #2
    5574:	mov	x6, x2
    5578:	mov	x7, x0
    557c:	ptrue	p0.b
    5580:	cntb	x5, all, mul #8
    5584:	cmp	x4, #0x0
    5588:	b.le	5668 <dot_sve_a8+0x100>
    558c:	mov	x2, x1
    5590:	mov	x0, x7
    5594:	mov	z1.b, #0
    5598:	mov	z2.d, z1.d
    559c:	mov	z3.d, z1.d
    55a0:	mov	x3, #0x0                   	// #0
    55a4:	mov	z4.d, z1.d
    55a8:	mov	z5.d, z1.d
    55ac:	mov	z6.d, z1.d
    55b0:	mov	z7.d, z1.d
    55b4:	mov	z0.d, z1.d
    55b8:	nop
    55bc:	nop
    55c0:	ld1b	{z18.b}, p0/z, [x2]
    55c4:	ld1b	{z17.b}, p0/z, [x0]
    55c8:	sdot	z0.s, z17.b, z18.b
    55cc:	ld1b	{z16.b}, p0/z, [x0, #1, mul vl]
    55d0:	add	x3, x3, x5
    55d4:	ld1b	{z18.b}, p0/z, [x2, #1, mul vl]
    55d8:	sdot	z7.s, z16.b, z18.b
    55dc:	ld1b	{z17.b}, p0/z, [x0, #2, mul vl]
    55e0:	ld1b	{z16.b}, p0/z, [x0, #3, mul vl]
    55e4:	ld1b	{z18.b}, p0/z, [x2, #2, mul vl]
    55e8:	sdot	z6.s, z17.b, z18.b
    55ec:	ld1b	{z17.b}, p0/z, [x0, #4, mul vl]
    55f0:	ld1b	{z18.b}, p0/z, [x2, #3, mul vl]
    55f4:	sdot	z5.s, z16.b, z18.b
    55f8:	ld1b	{z16.b}, p0/z, [x0, #5, mul vl]
    55fc:	ld1b	{z18.b}, p0/z, [x2, #4, mul vl]
    5600:	sdot	z4.s, z17.b, z18.b
    5604:	ld1b	{z17.b}, p0/z, [x0, #6, mul vl]
    5608:	ld1b	{z18.b}, p0/z, [x2, #5, mul vl]
    560c:	sdot	z3.s, z16.b, z18.b
    5610:	ld1b	{z16.b}, p0/z, [x0, #7, mul vl]
    5614:	add	x0, x0, x5
    5618:	ld1b	{z18.b}, p0/z, [x2, #6, mul vl]
    561c:	sdot	z2.s, z17.b, z18.b
    5620:	ld1b	{z17.b}, p0/z, [x2, #7, mul vl]
    5624:	add	x2, x2, x5
    5628:	sdot	z1.s, z16.b, z17.b
    562c:	cmp	x4, x3
    5630:	b.gt	55c0 <dot_sve_a8+0x58>
    5634:	add	z0.s, z0.s, z7.s
    5638:	add	x7, x7, x4
    563c:	add	z0.s, z0.s, z6.s
    5640:	add	z0.s, z0.s, z5.s
    5644:	add	z0.s, z0.s, z4.s
    5648:	add	z0.s, z0.s, z3.s
    564c:	add	z0.s, z0.s, z2.s
    5650:	add	z0.s, z0.s, z1.s
    5654:	saddv	d0, p0, z0.s
    5658:	str	s0, [x6], #4
    565c:	cmp	x8, x6
    5660:	b.ne	5584 <dot_sve_a8+0x1c>  // b.any
    5664:	ret
    5668:	mov	z1.b, #0
    566c:	mov	z2.d, z1.d
    5670:	mov	z3.d, z1.d
    5674:	mov	z4.d, z1.d
    5678:	mov	z5.d, z1.d
    567c:	mov	z6.d, z1.d
    5680:	mov	z7.d, z1.d
    5684:	mov	z0.d, z1.d
    5688:	b	5634 <dot_sve_a8+0xcc>

Disassembly of section .fini:
