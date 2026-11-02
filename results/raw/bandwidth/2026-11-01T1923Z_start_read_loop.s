# ===== read_slice_acc16_k1 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000027a0 <read_slice_acc16_k1>:
    27a0:	adrp	x3, 1f000 <__FRAME_END__+0x18670>
    27a4:	ldr	x3, [x3, #4040]
    27a8:	sub	sp, sp, #0x120
    27ac:	movi	v0.4s, #0x0
    27b0:	mov	x2, sp
    27b4:	stp	x29, x30, [sp, #272]
    27b8:	add	x29, sp, #0x110
    27bc:	ldr	x4, [x3]
    27c0:	str	x4, [sp, #264]
    27c4:	mov	x4, #0x0                   	// #0
    27c8:	stp	q0, q0, [x2]
    27cc:	stp	q0, q0, [x2, #32]
    27d0:	stp	q0, q0, [x2, #64]
    27d4:	stp	q0, q0, [x2, #96]
    27d8:	stp	q0, q0, [x2, #128]
    27dc:	stp	q0, q0, [x2, #160]
    27e0:	stp	q0, q0, [x2, #192]
    27e4:	stp	q0, q0, [x2, #224]
    27e8:	cbz	x1, 2970 <read_slice_acc16_k1+0x1d0>
    27ec:	movi	v0.4s, #0x0
    27f0:	sub	x1, x1, #0x1
    27f4:	add	x2, x0, #0x100
    27f8:	lsr	x1, x1, #5
    27fc:	add	x1, x2, x1, lsl #8
    2800:	mov	v2.16b, v0.16b
    2804:	mov	v3.16b, v0.16b
    2808:	mov	v4.16b, v0.16b
    280c:	mov	v5.16b, v0.16b
    2810:	mov	v6.16b, v0.16b
    2814:	mov	v7.16b, v0.16b
    2818:	mov	v16.16b, v0.16b
    281c:	mov	v17.16b, v0.16b
    2820:	mov	v18.16b, v0.16b
    2824:	mov	v19.16b, v0.16b
    2828:	mov	v20.16b, v0.16b
    282c:	mov	v21.16b, v0.16b
    2830:	mov	v22.16b, v0.16b
    2834:	mov	v23.16b, v0.16b
    2838:	mov	v1.16b, v0.16b
    283c:	nop
    2840:	ldp	q27, q26, [x0]
    2844:	ldp	q25, q24, [x0, #32]
    2848:	add	v1.2d, v1.2d, v27.2d
    284c:	add	v23.2d, v23.2d, v26.2d
    2850:	ldp	q27, q26, [x0, #64]
    2854:	add	v22.2d, v22.2d, v25.2d
    2858:	add	v21.2d, v21.2d, v24.2d
    285c:	ldp	q25, q24, [x0, #96]
    2860:	add	v20.2d, v20.2d, v27.2d
    2864:	add	v19.2d, v19.2d, v26.2d
    2868:	ldp	q27, q26, [x0, #128]
    286c:	add	v18.2d, v18.2d, v25.2d
    2870:	add	v17.2d, v17.2d, v24.2d
    2874:	ldp	q25, q24, [x0, #160]
    2878:	add	v16.2d, v16.2d, v27.2d
    287c:	add	v7.2d, v7.2d, v26.2d
    2880:	ldp	q27, q26, [x0, #192]
    2884:	add	v6.2d, v6.2d, v25.2d
    2888:	add	v5.2d, v5.2d, v24.2d
    288c:	ldp	q25, q24, [x0, #224]
    2890:	add	x0, x0, #0x100
    2894:	add	v4.2d, v4.2d, v27.2d
    2898:	add	v3.2d, v3.2d, v26.2d
    289c:	add	v2.2d, v2.2d, v25.2d
    28a0:	add	v0.2d, v0.2d, v24.2d
    28a4:	cmp	x1, x0
    28a8:	b.ne	2840 <read_slice_acc16_k1+0xa0>  // b.any
    28ac:	stp	q7, q6, [sp, #144]
    28b0:	mov	v7.16b, v19.16b
    28b4:	mov	v6.16b, v17.16b
    28b8:	str	q0, [sp, #240]
    28bc:	mov	v0.16b, v23.16b
    28c0:	stp	q5, q4, [sp, #176]
    28c4:	mov	v4.16b, v21.16b
    28c8:	mov	v5.16b, v16.16b
    28cc:	stp	q3, q2, [sp, #208]
    28d0:	mov	v2.16b, v22.16b
    28d4:	mov	v3.16b, v20.16b
    28d8:	stp	q23, q22, [sp, #16]
    28dc:	stp	q21, q20, [sp, #48]
    28e0:	stp	q19, q18, [sp, #80]
    28e4:	stp	q17, q16, [sp, #112]
    28e8:	add	v0.2d, v0.2d, v2.2d
    28ec:	ldr	q2, [sp, #96]
    28f0:	add	v3.2d, v3.2d, v4.2d
    28f4:	ldp	q4, q16, [sp, #144]
    28f8:	add	v0.2d, v0.2d, v3.2d
    28fc:	ldr	q3, [sp, #192]
    2900:	add	v2.2d, v2.2d, v7.2d
    2904:	ldr	q7, [sp, #176]
    2908:	adrp	x0, 1f000 <__FRAME_END__+0x18670>
    290c:	ldr	x0, [x0, #4040]
    2910:	add	v2.2d, v2.2d, v6.2d
    2914:	add	v4.2d, v4.2d, v5.2d
    2918:	ldp	q6, q5, [sp, #208]
    291c:	add	v3.2d, v3.2d, v7.2d
    2920:	ldr	x2, [sp, #264]
    2924:	ldr	x1, [x0]
    2928:	subs	x2, x2, x1
    292c:	mov	x1, #0x0                   	// #0
    2930:	add	v0.2d, v0.2d, v2.2d
    2934:	ldr	q2, [sp, #240]
    2938:	add	v4.2d, v4.2d, v16.2d
    293c:	add	v0.2d, v0.2d, v4.2d
    2940:	add	v3.2d, v3.2d, v6.2d
    2944:	add	v2.2d, v2.2d, v5.2d
    2948:	add	v0.2d, v0.2d, v3.2d
    294c:	add	v1.2d, v2.2d, v1.2d
    2950:	add	v0.2d, v0.2d, v1.2d
    2954:	mov	d1, v0.d[1]
    2958:	add	d0, d1, d0
    295c:	fmov	x0, d0
    2960:	b.ne	2988 <read_slice_acc16_k1+0x1e8>  // b.any
    2964:	ldp	x29, x30, [sp, #272]
    2968:	add	sp, sp, #0x120
    296c:	ret
    2970:	ldp	q0, q2, [sp, #16]
    2974:	movi	v1.4s, #0x0
    2978:	ldp	q4, q3, [sp, #48]
    297c:	ldr	q7, [sp, #80]
    2980:	ldp	q6, q5, [sp, #112]
    2984:	b	28e8 <read_slice_acc16_k1+0x148>
    2988:	bl	12e0 <__stack_chk_fail@plt>

Disassembly of section .fini:

# ===== read_slice_acc16_k2 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

000000000000298c <read_slice_acc16_k2>:
    298c:	adrp	x3, 1f000 <__FRAME_END__+0x18670>
    2990:	ldr	x3, [x3, #4040]
    2994:	sub	sp, sp, #0x120
    2998:	movi	v0.4s, #0x0
    299c:	lsr	x1, x1, #1
    29a0:	mov	x2, sp
    29a4:	stp	x29, x30, [sp, #272]
    29a8:	add	x29, sp, #0x110
    29ac:	ldr	x4, [x3]
    29b0:	str	x4, [sp, #264]
    29b4:	mov	x4, #0x0                   	// #0
    29b8:	stp	q0, q0, [x2]
    29bc:	stp	q0, q0, [x2, #32]
    29c0:	stp	q0, q0, [x2, #64]
    29c4:	stp	q0, q0, [x2, #96]
    29c8:	stp	q0, q0, [x2, #128]
    29cc:	stp	q0, q0, [x2, #160]
    29d0:	stp	q0, q0, [x2, #192]
    29d4:	stp	q0, q0, [x2, #224]
    29d8:	cbz	x1, 2bd0 <read_slice_acc16_k2+0x244>
    29dc:	movi	v4.4s, #0x0
    29e0:	sub	x2, x1, #0x1
    29e4:	add	x3, x0, #0x100
    29e8:	add	x1, x0, x1, lsl #3
    29ec:	lsr	x2, x2, #5
    29f0:	add	x2, x3, x2, lsl #8
    29f4:	mov	v6.16b, v4.16b
    29f8:	mov	v7.16b, v4.16b
    29fc:	mov	v16.16b, v4.16b
    2a00:	mov	v17.16b, v4.16b
    2a04:	mov	v18.16b, v4.16b
    2a08:	mov	v19.16b, v4.16b
    2a0c:	mov	v20.16b, v4.16b
    2a10:	mov	v21.16b, v4.16b
    2a14:	mov	v22.16b, v4.16b
    2a18:	mov	v23.16b, v4.16b
    2a1c:	mov	v24.16b, v4.16b
    2a20:	mov	v25.16b, v4.16b
    2a24:	mov	v26.16b, v4.16b
    2a28:	mov	v27.16b, v4.16b
    2a2c:	mov	v5.16b, v4.16b
    2a30:	ldp	q0, q29, [x1]
    2a34:	ldp	q3, q2, [x0]
    2a38:	ldr	q28, [x1, #32]
    2a3c:	ldr	q1, [x0, #32]
    2a40:	add	v3.2d, v3.2d, v0.2d
    2a44:	add	v2.2d, v2.2d, v29.2d
    2a48:	add	v1.2d, v1.2d, v28.2d
    2a4c:	ldp	q29, q28, [x1, #48]
    2a50:	add	v5.2d, v5.2d, v3.2d
    2a54:	ldp	q0, q3, [x0, #48]
    2a58:	add	v27.2d, v27.2d, v2.2d
    2a5c:	add	v26.2d, v26.2d, v1.2d
    2a60:	ldp	q2, q1, [x0, #80]
    2a64:	add	v0.2d, v0.2d, v29.2d
    2a68:	add	v3.2d, v3.2d, v28.2d
    2a6c:	ldp	q29, q28, [x1, #80]
    2a70:	add	v25.2d, v25.2d, v0.2d
    2a74:	add	v24.2d, v24.2d, v3.2d
    2a78:	ldp	q0, q3, [x0, #112]
    2a7c:	add	v2.2d, v2.2d, v29.2d
    2a80:	add	v1.2d, v1.2d, v28.2d
    2a84:	ldp	q29, q28, [x1, #112]
    2a88:	add	v23.2d, v23.2d, v2.2d
    2a8c:	add	v22.2d, v22.2d, v1.2d
    2a90:	ldp	q2, q1, [x0, #144]
    2a94:	add	v0.2d, v0.2d, v29.2d
    2a98:	add	v3.2d, v3.2d, v28.2d
    2a9c:	ldp	q29, q28, [x1, #144]
    2aa0:	add	v21.2d, v21.2d, v0.2d
    2aa4:	add	v20.2d, v20.2d, v3.2d
    2aa8:	ldp	q0, q3, [x0, #176]
    2aac:	add	v2.2d, v2.2d, v29.2d
    2ab0:	add	v1.2d, v1.2d, v28.2d
    2ab4:	ldp	q29, q28, [x1, #176]
    2ab8:	add	v19.2d, v19.2d, v2.2d
    2abc:	add	v18.2d, v18.2d, v1.2d
    2ac0:	ldp	q2, q1, [x0, #208]
    2ac4:	add	x0, x0, #0x100
    2ac8:	add	v0.2d, v0.2d, v29.2d
    2acc:	add	v3.2d, v3.2d, v28.2d
    2ad0:	ldp	q29, q28, [x1, #208]
    2ad4:	add	x1, x1, #0x100
    2ad8:	add	v17.2d, v17.2d, v0.2d
    2adc:	ldur	q0, [x0, #-16]
    2ae0:	add	v16.2d, v16.2d, v3.2d
    2ae4:	ldur	q3, [x1, #-16]
    2ae8:	add	v2.2d, v2.2d, v29.2d
    2aec:	add	v1.2d, v1.2d, v28.2d
    2af0:	add	v0.2d, v0.2d, v3.2d
    2af4:	add	v7.2d, v7.2d, v2.2d
    2af8:	add	v6.2d, v6.2d, v1.2d
    2afc:	add	v4.2d, v4.2d, v0.2d
    2b00:	cmp	x0, x2
    2b04:	b.ne	2a30 <read_slice_acc16_k2+0xa4>  // b.any
    2b08:	mov	v0.16b, v27.16b
    2b0c:	mov	v1.16b, v26.16b
    2b10:	str	q4, [sp, #240]
    2b14:	mov	v3.16b, v25.16b
    2b18:	mov	v2.16b, v24.16b
    2b1c:	mov	v4.16b, v20.16b
    2b20:	stp	q17, q16, [sp, #176]
    2b24:	mov	v16.16b, v18.16b
    2b28:	stp	q7, q6, [sp, #208]
    2b2c:	mov	v7.16b, v23.16b
    2b30:	mov	v6.16b, v21.16b
    2b34:	stp	q27, q26, [sp, #16]
    2b38:	stp	q25, q24, [sp, #48]
    2b3c:	stp	q23, q22, [sp, #80]
    2b40:	stp	q21, q20, [sp, #112]
    2b44:	stp	q19, q18, [sp, #144]
    2b48:	add	v0.2d, v0.2d, v1.2d
    2b4c:	ldr	q1, [sp, #96]
    2b50:	add	v2.2d, v2.2d, v3.2d
    2b54:	ldr	q3, [sp, #144]
    2b58:	add	v0.2d, v0.2d, v2.2d
    2b5c:	ldr	q2, [sp, #192]
    2b60:	add	v1.2d, v1.2d, v7.2d
    2b64:	ldr	q7, [sp, #176]
    2b68:	add	v3.2d, v3.2d, v4.2d
    2b6c:	adrp	x0, 1f000 <__FRAME_END__+0x18670>
    2b70:	ldr	x0, [x0, #4040]
    2b74:	add	v1.2d, v1.2d, v6.2d
    2b78:	ldp	q6, q4, [sp, #208]
    2b7c:	add	v3.2d, v3.2d, v16.2d
    2b80:	add	v2.2d, v2.2d, v7.2d
    2b84:	ldr	x2, [sp, #264]
    2b88:	ldr	x1, [x0]
    2b8c:	subs	x2, x2, x1
    2b90:	mov	x1, #0x0                   	// #0
    2b94:	add	v0.2d, v0.2d, v1.2d
    2b98:	ldr	q1, [sp, #240]
    2b9c:	add	v0.2d, v0.2d, v3.2d
    2ba0:	add	v2.2d, v2.2d, v6.2d
    2ba4:	add	v1.2d, v1.2d, v4.2d
    2ba8:	add	v0.2d, v0.2d, v2.2d
    2bac:	add	v1.2d, v1.2d, v5.2d
    2bb0:	add	v0.2d, v0.2d, v1.2d
    2bb4:	mov	d1, v0.d[1]
    2bb8:	add	d0, d1, d0
    2bbc:	fmov	x0, d0
    2bc0:	b.ne	2bec <read_slice_acc16_k2+0x260>  // b.any
    2bc4:	ldp	x29, x30, [sp, #272]
    2bc8:	add	sp, sp, #0x120
    2bcc:	ret
    2bd0:	ldp	q0, q1, [sp, #16]
    2bd4:	movi	v5.4s, #0x0
    2bd8:	ldp	q3, q2, [sp, #48]
    2bdc:	ldr	q7, [sp, #80]
    2be0:	ldp	q6, q4, [sp, #112]
    2be4:	ldr	q16, [sp, #160]
    2be8:	b	2b48 <read_slice_acc16_k2+0x1bc>
    2bec:	bl	12e0 <__stack_chk_fail@plt>

Disassembly of section .fini:

# ===== read_slice_acc16_k4 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002bf0 <read_slice_acc16_k4>:
    2bf0:	adrp	x4, 1f000 <__FRAME_END__+0x18670>
    2bf4:	ldr	x4, [x4, #4040]
    2bf8:	sub	sp, sp, #0x120
    2bfc:	movi	v0.4s, #0x0
    2c00:	mov	x3, x0
    2c04:	mov	x2, sp
    2c08:	lsr	x5, x1, #2
    2c0c:	stp	x29, x30, [sp, #272]
    2c10:	add	x29, sp, #0x110
    2c14:	ldr	x0, [x4]
    2c18:	str	x0, [sp, #264]
    2c1c:	mov	x0, #0x0                   	// #0
    2c20:	stp	q0, q0, [x2]
    2c24:	stp	q0, q0, [x2, #32]
    2c28:	stp	q0, q0, [x2, #64]
    2c2c:	stp	q0, q0, [x2, #96]
    2c30:	stp	q0, q0, [x2, #128]
    2c34:	stp	q0, q0, [x2, #160]
    2c38:	stp	q0, q0, [x2, #192]
    2c3c:	stp	q0, q0, [x2, #224]
    2c40:	cbz	x5, 2dd4 <read_slice_acc16_k4+0x1e4>
    2c44:	movi	v0.4s, #0x0
    2c48:	lsl	x2, x5, #3
    2c4c:	mov	x4, #0x0                   	// #0
    2c50:	mov	v2.16b, v0.16b
    2c54:	mov	v3.16b, v0.16b
    2c58:	mov	v4.16b, v0.16b
    2c5c:	mov	v5.16b, v0.16b
    2c60:	mov	v6.16b, v0.16b
    2c64:	mov	v7.16b, v0.16b
    2c68:	mov	v16.16b, v0.16b
    2c6c:	mov	v17.16b, v0.16b
    2c70:	mov	v18.16b, v0.16b
    2c74:	mov	v19.16b, v0.16b
    2c78:	mov	v20.16b, v0.16b
    2c7c:	mov	v21.16b, v0.16b
    2c80:	mov	v22.16b, v0.16b
    2c84:	mov	v23.16b, v0.16b
    2c88:	mov	v1.16b, v0.16b
    2c8c:	mov	x0, x3
    2c90:	mov	w1, #0x4                   	// #4
    2c94:	ldp	q27, q26, [x0]
    2c98:	subs	w1, w1, #0x1
    2c9c:	ldp	q25, q24, [x0, #32]
    2ca0:	add	v1.2d, v1.2d, v27.2d
    2ca4:	add	v23.2d, v23.2d, v26.2d
    2ca8:	ldp	q27, q26, [x0, #64]
    2cac:	add	v22.2d, v22.2d, v25.2d
    2cb0:	add	v21.2d, v21.2d, v24.2d
    2cb4:	ldp	q25, q24, [x0, #96]
    2cb8:	add	v20.2d, v20.2d, v27.2d
    2cbc:	add	v19.2d, v19.2d, v26.2d
    2cc0:	ldp	q27, q26, [x0, #128]
    2cc4:	add	v18.2d, v18.2d, v25.2d
    2cc8:	add	v17.2d, v17.2d, v24.2d
    2ccc:	ldp	q25, q24, [x0, #160]
    2cd0:	add	v16.2d, v16.2d, v27.2d
    2cd4:	add	v7.2d, v7.2d, v26.2d
    2cd8:	ldp	q27, q26, [x0, #192]
    2cdc:	add	v6.2d, v6.2d, v25.2d
    2ce0:	add	v5.2d, v5.2d, v24.2d
    2ce4:	ldp	q25, q24, [x0, #224]
    2ce8:	add	x0, x0, x2
    2cec:	add	v4.2d, v4.2d, v27.2d
    2cf0:	add	v3.2d, v3.2d, v26.2d
    2cf4:	add	v2.2d, v2.2d, v25.2d
    2cf8:	add	v0.2d, v0.2d, v24.2d
    2cfc:	b.ne	2c94 <read_slice_acc16_k4+0xa4>  // b.any
    2d00:	add	x4, x4, #0x20
    2d04:	add	x3, x3, #0x100
    2d08:	cmp	x5, x4
    2d0c:	b.hi	2c8c <read_slice_acc16_k4+0x9c>  // b.pmore
    2d10:	stp	q7, q6, [sp, #144]
    2d14:	mov	v7.16b, v19.16b
    2d18:	mov	v6.16b, v17.16b
    2d1c:	str	q0, [sp, #240]
    2d20:	mov	v0.16b, v23.16b
    2d24:	stp	q5, q4, [sp, #176]
    2d28:	mov	v4.16b, v21.16b
    2d2c:	mov	v5.16b, v16.16b
    2d30:	stp	q3, q2, [sp, #208]
    2d34:	mov	v2.16b, v22.16b
    2d38:	mov	v3.16b, v20.16b
    2d3c:	stp	q23, q22, [sp, #16]
    2d40:	stp	q21, q20, [sp, #48]
    2d44:	stp	q19, q18, [sp, #80]
    2d48:	stp	q17, q16, [sp, #112]
    2d4c:	add	v0.2d, v0.2d, v2.2d
    2d50:	ldr	q2, [sp, #96]
    2d54:	add	v3.2d, v3.2d, v4.2d
    2d58:	ldp	q4, q16, [sp, #144]
    2d5c:	add	v0.2d, v0.2d, v3.2d
    2d60:	ldr	q3, [sp, #192]
    2d64:	add	v2.2d, v2.2d, v7.2d
    2d68:	ldr	q7, [sp, #176]
    2d6c:	adrp	x0, 1f000 <__FRAME_END__+0x18670>
    2d70:	ldr	x0, [x0, #4040]
    2d74:	add	v2.2d, v2.2d, v6.2d
    2d78:	add	v4.2d, v4.2d, v5.2d
    2d7c:	ldp	q6, q5, [sp, #208]
    2d80:	add	v3.2d, v3.2d, v7.2d
    2d84:	ldr	x2, [sp, #264]
    2d88:	ldr	x1, [x0]
    2d8c:	subs	x2, x2, x1
    2d90:	mov	x1, #0x0                   	// #0
    2d94:	add	v0.2d, v0.2d, v2.2d
    2d98:	ldr	q2, [sp, #240]
    2d9c:	add	v4.2d, v4.2d, v16.2d
    2da0:	add	v0.2d, v0.2d, v4.2d
    2da4:	add	v3.2d, v3.2d, v6.2d
    2da8:	add	v2.2d, v2.2d, v5.2d
    2dac:	add	v0.2d, v0.2d, v3.2d
    2db0:	add	v1.2d, v2.2d, v1.2d
    2db4:	add	v0.2d, v0.2d, v1.2d
    2db8:	mov	d1, v0.d[1]
    2dbc:	add	d0, d1, d0
    2dc0:	fmov	x0, d0
    2dc4:	b.ne	2dec <read_slice_acc16_k4+0x1fc>  // b.any
    2dc8:	ldp	x29, x30, [sp, #272]
    2dcc:	add	sp, sp, #0x120
    2dd0:	ret
    2dd4:	ldp	q0, q2, [sp, #16]
    2dd8:	movi	v1.4s, #0x0
    2ddc:	ldp	q4, q3, [sp, #48]
    2de0:	ldr	q7, [sp, #80]
    2de4:	ldp	q6, q5, [sp, #112]
    2de8:	b	2d4c <read_slice_acc16_k4+0x15c>
    2dec:	bl	12e0 <__stack_chk_fail@plt>

Disassembly of section .fini:

# ===== read_slice_acc16_k8 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002df0 <read_slice_acc16_k8>:
    2df0:	adrp	x4, 1f000 <__FRAME_END__+0x18670>
    2df4:	ldr	x4, [x4, #4040]
    2df8:	sub	sp, sp, #0x120
    2dfc:	movi	v0.4s, #0x0
    2e00:	mov	x3, x0
    2e04:	mov	x2, sp
    2e08:	lsr	x5, x1, #3
    2e0c:	stp	x29, x30, [sp, #272]
    2e10:	add	x29, sp, #0x110
    2e14:	ldr	x0, [x4]
    2e18:	str	x0, [sp, #264]
    2e1c:	mov	x0, #0x0                   	// #0
    2e20:	stp	q0, q0, [x2]
    2e24:	stp	q0, q0, [x2, #32]
    2e28:	stp	q0, q0, [x2, #64]
    2e2c:	stp	q0, q0, [x2, #96]
    2e30:	stp	q0, q0, [x2, #128]
    2e34:	stp	q0, q0, [x2, #160]
    2e38:	stp	q0, q0, [x2, #192]
    2e3c:	stp	q0, q0, [x2, #224]
    2e40:	cbz	x5, 2fe0 <read_slice_acc16_k8+0x1f0>
    2e44:	movi	v0.4s, #0x0
    2e48:	lsl	x2, x5, #3
    2e4c:	mov	x4, #0x0                   	// #0
    2e50:	mov	v2.16b, v0.16b
    2e54:	mov	v3.16b, v0.16b
    2e58:	mov	v4.16b, v0.16b
    2e5c:	mov	v5.16b, v0.16b
    2e60:	mov	v6.16b, v0.16b
    2e64:	mov	v7.16b, v0.16b
    2e68:	mov	v16.16b, v0.16b
    2e6c:	mov	v17.16b, v0.16b
    2e70:	mov	v18.16b, v0.16b
    2e74:	mov	v19.16b, v0.16b
    2e78:	mov	v20.16b, v0.16b
    2e7c:	mov	v21.16b, v0.16b
    2e80:	mov	v22.16b, v0.16b
    2e84:	mov	v23.16b, v0.16b
    2e88:	mov	v1.16b, v0.16b
    2e8c:	mov	x0, x3
    2e90:	mov	w1, #0x8                   	// #8
    2e94:	nop
    2e98:	nop
    2e9c:	nop
    2ea0:	ldp	q27, q26, [x0]
    2ea4:	subs	w1, w1, #0x1
    2ea8:	ldp	q25, q24, [x0, #32]
    2eac:	add	v1.2d, v1.2d, v27.2d
    2eb0:	add	v23.2d, v23.2d, v26.2d
    2eb4:	ldp	q27, q26, [x0, #64]
    2eb8:	add	v22.2d, v22.2d, v25.2d
    2ebc:	add	v21.2d, v21.2d, v24.2d
    2ec0:	ldp	q25, q24, [x0, #96]
    2ec4:	add	v20.2d, v20.2d, v27.2d
    2ec8:	add	v19.2d, v19.2d, v26.2d
    2ecc:	ldp	q27, q26, [x0, #128]
    2ed0:	add	v18.2d, v18.2d, v25.2d
    2ed4:	add	v17.2d, v17.2d, v24.2d
    2ed8:	ldp	q25, q24, [x0, #160]
    2edc:	add	v16.2d, v16.2d, v27.2d
    2ee0:	add	v7.2d, v7.2d, v26.2d
    2ee4:	ldp	q27, q26, [x0, #192]
    2ee8:	add	v6.2d, v6.2d, v25.2d
    2eec:	add	v5.2d, v5.2d, v24.2d
    2ef0:	ldp	q25, q24, [x0, #224]
    2ef4:	add	x0, x0, x2
    2ef8:	add	v4.2d, v4.2d, v27.2d
    2efc:	add	v3.2d, v3.2d, v26.2d
    2f00:	add	v2.2d, v2.2d, v25.2d
    2f04:	add	v0.2d, v0.2d, v24.2d
    2f08:	b.ne	2ea0 <read_slice_acc16_k8+0xb0>  // b.any
    2f0c:	add	x4, x4, #0x20
    2f10:	add	x3, x3, #0x100
    2f14:	cmp	x5, x4
    2f18:	b.hi	2e8c <read_slice_acc16_k8+0x9c>  // b.pmore
    2f1c:	stp	q7, q6, [sp, #144]
    2f20:	mov	v7.16b, v19.16b
    2f24:	mov	v6.16b, v17.16b
    2f28:	str	q0, [sp, #240]
    2f2c:	mov	v0.16b, v23.16b
    2f30:	stp	q5, q4, [sp, #176]
    2f34:	mov	v4.16b, v21.16b
    2f38:	mov	v5.16b, v16.16b
    2f3c:	stp	q3, q2, [sp, #208]
    2f40:	mov	v2.16b, v22.16b
    2f44:	mov	v3.16b, v20.16b
    2f48:	stp	q23, q22, [sp, #16]
    2f4c:	stp	q21, q20, [sp, #48]
    2f50:	stp	q19, q18, [sp, #80]
    2f54:	stp	q17, q16, [sp, #112]
    2f58:	add	v0.2d, v0.2d, v2.2d
    2f5c:	ldr	q2, [sp, #96]
    2f60:	add	v3.2d, v3.2d, v4.2d
    2f64:	ldp	q4, q16, [sp, #144]
    2f68:	add	v0.2d, v0.2d, v3.2d
    2f6c:	ldr	q3, [sp, #192]
    2f70:	add	v2.2d, v2.2d, v7.2d
    2f74:	ldr	q7, [sp, #176]
    2f78:	adrp	x0, 1f000 <__FRAME_END__+0x18670>
    2f7c:	ldr	x0, [x0, #4040]
    2f80:	add	v2.2d, v2.2d, v6.2d
    2f84:	add	v4.2d, v4.2d, v5.2d
    2f88:	ldp	q6, q5, [sp, #208]
    2f8c:	add	v3.2d, v3.2d, v7.2d
    2f90:	ldr	x2, [sp, #264]
    2f94:	ldr	x1, [x0]
    2f98:	subs	x2, x2, x1
    2f9c:	mov	x1, #0x0                   	// #0
    2fa0:	add	v0.2d, v0.2d, v2.2d
    2fa4:	ldr	q2, [sp, #240]
    2fa8:	add	v4.2d, v4.2d, v16.2d
    2fac:	add	v0.2d, v0.2d, v4.2d
    2fb0:	add	v3.2d, v3.2d, v6.2d
    2fb4:	add	v2.2d, v2.2d, v5.2d
    2fb8:	add	v0.2d, v0.2d, v3.2d
    2fbc:	add	v1.2d, v2.2d, v1.2d
    2fc0:	add	v0.2d, v0.2d, v1.2d
    2fc4:	mov	d1, v0.d[1]
    2fc8:	add	d0, d1, d0
    2fcc:	fmov	x0, d0
    2fd0:	b.ne	2ff8 <read_slice_acc16_k8+0x208>  // b.any
    2fd4:	ldp	x29, x30, [sp, #272]
    2fd8:	add	sp, sp, #0x120
    2fdc:	ret
    2fe0:	ldp	q0, q2, [sp, #16]
    2fe4:	movi	v1.4s, #0x0
    2fe8:	ldp	q4, q3, [sp, #48]
    2fec:	ldr	q7, [sp, #80]
    2ff0:	ldp	q6, q5, [sp, #112]
    2ff4:	b	2f58 <read_slice_acc16_k8+0x168>
    2ff8:	bl	12e0 <__stack_chk_fail@plt>

Disassembly of section .fini:

# ===== read_slice_acc24_k1 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

000000000000314c <read_slice_acc24_k1>:
    314c:	b	3000 <unsigned long read_slice_impl<24, 1>(unsigned long const*, unsigned long)>

Disassembly of section .fini:

# ===== read_slice_acc24_k2 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003260 <read_slice_acc24_k2>:
    3260:	b	3150 <unsigned long read_slice_impl<24, 2>(unsigned long const*, unsigned long)>

Disassembly of section .fini:

# ===== read_slice_acc24_k4 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

000000000000338c <read_slice_acc24_k4>:
    338c:	b	3264 <unsigned long read_slice_impl<24, 4>(unsigned long const*, unsigned long)>

Disassembly of section .fini:

# ===== read_slice_acc24_k8 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000034ac <read_slice_acc24_k8>:
    34ac:	b	3390 <unsigned long read_slice_impl<24, 8>(unsigned long const*, unsigned long)>

Disassembly of section .fini:
