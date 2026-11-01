
/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000021cc <read_slice_acc8>:
    21cc:	adrp	x3, 1f000 <__FRAME_END__+0x19dcc>
    21d0:	ldr	x3, [x3, #4040]
    21d4:	sub	sp, sp, #0xa0
    21d8:	movi	v0.4s, #0x0
    21dc:	mov	x2, sp
    21e0:	stp	x29, x30, [sp, #144]
    21e4:	add	x29, sp, #0x90
    21e8:	ldr	x4, [x3]
    21ec:	str	x4, [sp, #136]
    21f0:	mov	x4, #0x0                   	// #0
    21f4:	stp	q0, q0, [x2]
    21f8:	stp	q0, q0, [x2, #32]
    21fc:	stp	q0, q0, [x2, #64]
    2200:	stp	q0, q0, [x2, #96]
    2204:	cbz	x1, 22f4 <read_slice_acc8+0x128>
    2208:	movi	v0.4s, #0x0
    220c:	sub	x1, x1, #0x1
    2210:	add	x2, x0, #0x80
    2214:	lsr	x1, x1, #4
    2218:	add	x1, x2, x1, lsl #7
    221c:	mov	v2.16b, v0.16b
    2220:	mov	v3.16b, v0.16b
    2224:	mov	v4.16b, v0.16b
    2228:	mov	v5.16b, v0.16b
    222c:	mov	v6.16b, v0.16b
    2230:	mov	v7.16b, v0.16b
    2234:	mov	v1.16b, v0.16b
    2238:	nop
    223c:	nop
    2240:	ldp	q19, q18, [x0]
    2244:	ldp	q17, q16, [x0, #32]
    2248:	add	v1.2d, v1.2d, v19.2d
    224c:	add	v7.2d, v7.2d, v18.2d
    2250:	ldp	q19, q18, [x0, #64]
    2254:	add	v6.2d, v6.2d, v17.2d
    2258:	add	v5.2d, v5.2d, v16.2d
    225c:	ldp	q17, q16, [x0, #96]
    2260:	add	x0, x0, #0x80
    2264:	add	v4.2d, v4.2d, v19.2d
    2268:	add	v3.2d, v3.2d, v18.2d
    226c:	add	v2.2d, v2.2d, v17.2d
    2270:	add	v0.2d, v0.2d, v16.2d
    2274:	cmp	x0, x1
    2278:	b.ne	2240 <read_slice_acc8+0x74>  // b.any
    227c:	stp	q5, q4, [sp, #48]
    2280:	mov	v4.16b, v5.16b
    2284:	str	q0, [sp, #112]
    2288:	mov	v0.16b, v7.16b
    228c:	stp	q3, q2, [sp, #80]
    2290:	mov	v2.16b, v6.16b
    2294:	stp	q7, q6, [sp, #16]
    2298:	ldp	q3, q5, [sp, #64]
    229c:	add	v0.2d, v0.2d, v2.2d
    22a0:	ldr	q2, [sp, #96]
    22a4:	adrp	x0, 1f000 <__FRAME_END__+0x19dcc>
    22a8:	ldr	x0, [x0, #4040]
    22ac:	add	v3.2d, v3.2d, v4.2d
    22b0:	ldr	q4, [sp, #112]
    22b4:	add	v2.2d, v2.2d, v5.2d
    22b8:	ldr	x2, [sp, #136]
    22bc:	ldr	x1, [x0]
    22c0:	subs	x2, x2, x1
    22c4:	mov	x1, #0x0                   	// #0
    22c8:	add	v0.2d, v0.2d, v3.2d
    22cc:	add	v1.2d, v1.2d, v4.2d
    22d0:	add	v0.2d, v0.2d, v2.2d
    22d4:	add	v0.2d, v0.2d, v1.2d
    22d8:	mov	d1, v0.d[1]
    22dc:	add	d0, d1, d0
    22e0:	fmov	x0, d0
    22e4:	b.ne	2304 <read_slice_acc8+0x138>  // b.any
    22e8:	ldp	x29, x30, [sp, #144]
    22ec:	add	sp, sp, #0xa0
    22f0:	ret
    22f4:	ldp	q0, q2, [sp, #16]
    22f8:	movi	v1.4s, #0x0
    22fc:	ldr	q4, [sp, #48]
    2300:	b	2298 <read_slice_acc8+0xcc>
    2304:	bl	10e0 <__stack_chk_fail@plt>

Disassembly of section .fini:
