# ===== dot_sve_a4: hot loop = the 17 instructions of the innermost conditional backward branch holding the expected instruction (sdot z-form) =====
#   ld1b {z5.b}, p0/z, [x0]
#   ld1b {z6.b}, p0/z, [x2]
#   ld1b {z4.b}, p0/z, [x0, #1, mul vl]
#   sdot z0.s, z5.b, z6.b
#   add x3, x3, x5
#   ld1b {z6.b}, p0/z, [x2, #1, mul vl]
#   ld1b {z5.b}, p0/z, [x0, #2, mul vl]
#   sdot z3.s, z4.b, z6.b
#   ld1b {z4.b}, p0/z, [x0, #3, mul vl]
#   add x0, x0, x5
#   ld1b {z6.b}, p0/z, [x2, #2, mul vl]
#   sdot z2.s, z5.b, z6.b
#   ld1b {z5.b}, p0/z, [x2, #3, mul vl]
#   add x2, x2, x5
#   sdot z1.s, z4.b, z5.b
#   cmp x4, x3
#   b.gt 54cc <dot_sve_a4+0x40>
# ===== whole function =====

/home/adnancheema917/edge-llm-on-arm/work/bin/dot_int8:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

000000000000548c <dot_sve_a4>:
    548c:	cmp	x3, #0x0
    5490:	b.le	5530 <dot_sve_a4+0xa4>
    5494:	add	x8, x2, x3, lsl #2
    5498:	mov	x6, x2
    549c:	mov	x7, x0
    54a0:	ptrue	p0.b
    54a4:	cntb	x5, all, mul #4
    54a8:	cmp	x4, #0x0
    54ac:	b.le	5534 <dot_sve_a4+0xa8>
    54b0:	mov	x2, x1
    54b4:	mov	x0, x7
    54b8:	mov	z1.b, #0
    54bc:	mov	z2.d, z1.d
    54c0:	mov	z3.d, z1.d
    54c4:	mov	x3, #0x0                   	// #0
    54c8:	mov	z0.d, z1.d
    54cc:	ld1b	{z5.b}, p0/z, [x0]
    54d0:	ld1b	{z6.b}, p0/z, [x2]
    54d4:	ld1b	{z4.b}, p0/z, [x0, #1, mul vl]
    54d8:	sdot	z0.s, z5.b, z6.b
    54dc:	add	x3, x3, x5
    54e0:	ld1b	{z6.b}, p0/z, [x2, #1, mul vl]
    54e4:	ld1b	{z5.b}, p0/z, [x0, #2, mul vl]
    54e8:	sdot	z3.s, z4.b, z6.b
    54ec:	ld1b	{z4.b}, p0/z, [x0, #3, mul vl]
    54f0:	add	x0, x0, x5
    54f4:	ld1b	{z6.b}, p0/z, [x2, #2, mul vl]
    54f8:	sdot	z2.s, z5.b, z6.b
    54fc:	ld1b	{z5.b}, p0/z, [x2, #3, mul vl]
    5500:	add	x2, x2, x5
    5504:	sdot	z1.s, z4.b, z5.b
    5508:	cmp	x4, x3
    550c:	b.gt	54cc <dot_sve_a4+0x40>
    5510:	add	z0.s, z0.s, z3.s
    5514:	add	x7, x7, x4
    5518:	add	z0.s, z0.s, z2.s
    551c:	add	z0.s, z0.s, z1.s
    5520:	saddv	d0, p0, z0.s
    5524:	str	s0, [x6], #4
    5528:	cmp	x8, x6
    552c:	b.ne	54a8 <dot_sve_a4+0x1c>  // b.any
    5530:	ret
    5534:	mov	z1.b, #0
    5538:	add	x7, x7, x4
    553c:	mov	z2.d, z1.d
    5540:	mov	z3.d, z1.d
    5544:	mov	z0.d, z1.d
    5548:	add	z0.s, z0.s, z3.s
    554c:	add	z0.s, z0.s, z2.s
    5550:	add	z0.s, z0.s, z1.s
    5554:	saddv	d0, p0, z0.s
    5558:	str	s0, [x6], #4
    555c:	cmp	x8, x6
    5560:	b.ne	54a8 <dot_sve_a4+0x1c>  // b.any
    5564:	b	5530 <dot_sve_a4+0xa4>

Disassembly of section .fini:
