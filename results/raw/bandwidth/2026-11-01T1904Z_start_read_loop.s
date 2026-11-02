
/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002a0c <read_slice_acc8_k1>:
    2a0c:	adrp	x3, 1f000 <__FRAME_END__+0x187e0>
    2a10:	ldr	x3, [x3, #4040]
    2a14:	sub	sp, sp, #0xa0
    2a18:	movi	v0.4s, #0x0
    2a1c:	mov	x2, sp
    2a20:	stp	x29, x30, [sp, #144]
    2a24:	add	x29, sp, #0x90
    2a28:	ldr	x4, [x3]
    2a2c:	str	x4, [sp, #136]
    2a30:	mov	x4, #0x0                   	// #0
    2a34:	stp	q0, q0, [x2]
    2a38:	stp	q0, q0, [x2, #32]
    2a3c:	stp	q0, q0, [x2, #64]
    2a40:	stp	q0, q0, [x2, #96]
    2a44:	cbz	x1, 2b34 <read_slice_acc8_k1+0x128>
    2a48:	movi	v0.4s, #0x0
    2a4c:	sub	x1, x1, #0x1
    2a50:	add	x2, x0, #0x80
    2a54:	lsr	x1, x1, #4
    2a58:	add	x1, x2, x1, lsl #7
    2a5c:	mov	v2.16b, v0.16b
    2a60:	mov	v3.16b, v0.16b
    2a64:	mov	v4.16b, v0.16b
    2a68:	mov	v5.16b, v0.16b
    2a6c:	mov	v6.16b, v0.16b
    2a70:	mov	v7.16b, v0.16b
    2a74:	mov	v1.16b, v0.16b
    2a78:	nop
    2a7c:	nop
    2a80:	ldp	q19, q18, [x0]
    2a84:	ldp	q17, q16, [x0, #32]
    2a88:	add	v1.2d, v1.2d, v19.2d
    2a8c:	add	v7.2d, v7.2d, v18.2d
    2a90:	ldp	q19, q18, [x0, #64]
    2a94:	add	v6.2d, v6.2d, v17.2d
    2a98:	add	v5.2d, v5.2d, v16.2d
    2a9c:	ldp	q17, q16, [x0, #96]
    2aa0:	add	x0, x0, #0x80
    2aa4:	add	v4.2d, v4.2d, v19.2d
    2aa8:	add	v3.2d, v3.2d, v18.2d
    2aac:	add	v2.2d, v2.2d, v17.2d
    2ab0:	add	v0.2d, v0.2d, v16.2d
    2ab4:	cmp	x0, x1
    2ab8:	b.ne	2a80 <read_slice_acc8_k1+0x74>  // b.any
    2abc:	stp	q5, q4, [sp, #48]
    2ac0:	mov	v4.16b, v5.16b
    2ac4:	str	q0, [sp, #112]
    2ac8:	mov	v0.16b, v7.16b
    2acc:	stp	q3, q2, [sp, #80]
    2ad0:	mov	v2.16b, v6.16b
    2ad4:	stp	q7, q6, [sp, #16]
    2ad8:	ldp	q3, q5, [sp, #64]
    2adc:	add	v0.2d, v0.2d, v2.2d
    2ae0:	ldr	q2, [sp, #96]
    2ae4:	adrp	x0, 1f000 <__FRAME_END__+0x187e0>
    2ae8:	ldr	x0, [x0, #4040]
    2aec:	add	v3.2d, v3.2d, v4.2d
    2af0:	ldr	q4, [sp, #112]
    2af4:	add	v2.2d, v2.2d, v5.2d
    2af8:	ldr	x2, [sp, #136]
    2afc:	ldr	x1, [x0]
    2b00:	subs	x2, x2, x1
    2b04:	mov	x1, #0x0                   	// #0
    2b08:	add	v0.2d, v0.2d, v3.2d
    2b0c:	add	v1.2d, v1.2d, v4.2d
    2b10:	add	v0.2d, v0.2d, v2.2d
    2b14:	add	v0.2d, v0.2d, v1.2d
    2b18:	mov	d1, v0.d[1]
    2b1c:	add	d0, d1, d0
    2b20:	fmov	x0, d0
    2b24:	b.ne	2b44 <read_slice_acc8_k1+0x138>  // b.any
    2b28:	ldp	x29, x30, [sp, #144]
    2b2c:	add	sp, sp, #0xa0
    2b30:	ret
    2b34:	ldp	q0, q2, [sp, #16]
    2b38:	movi	v1.4s, #0x0
    2b3c:	ldr	q4, [sp, #48]
    2b40:	b	2ad8 <read_slice_acc8_k1+0xcc>
    2b44:	bl	12e0 <__stack_chk_fail@plt>

Disassembly of section .fini:
