# ===== peak_sdot_a8: hot loop = the 11 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000029a0 <peak_sdot_a8>:
    29a0:	adrp	x1, 20000 <__data_start>
    29a4:	add	x2, x1, #0x10
    29a8:	ldr	b0, [x1, #16]
    29ac:	ldr	b1, [x2, #1]
    29b0:	dup	v0.16b, v0.b[0]
    29b4:	dup	v1.16b, v1.b[0]
    29b8:	cbz	x0, 2a34 <peak_sdot_a8+0x94>
    29bc:	movi	v3.4s, #0x8
    29c0:	movi	v4.4s, #0x7
    29c4:	mov	x1, #0x0                   	// #0
    29c8:	movi	v5.4s, #0x6
    29cc:	movi	v6.4s, #0x5
    29d0:	movi	v7.4s, #0x4
    29d4:	movi	v16.4s, #0x3
    29d8:	movi	v17.4s, #0x2
    29dc:	movi	v2.4s, #0x1
    29e0:	add	x1, x1, #0x1
    29e4:	sdot	v2.4s, v0.16b, v1.16b
    29e8:	sdot	v17.4s, v0.16b, v1.16b
    29ec:	sdot	v16.4s, v0.16b, v1.16b
    29f0:	sdot	v7.4s, v0.16b, v1.16b
    29f4:	sdot	v6.4s, v0.16b, v1.16b
    29f8:	sdot	v5.4s, v0.16b, v1.16b
    29fc:	sdot	v4.4s, v0.16b, v1.16b
    2a00:	sdot	v3.4s, v0.16b, v1.16b
    2a04:	cmp	x0, x1
    2a08:	b.ne	29e0 <peak_sdot_a8+0x40>  // b.any
    2a0c:	add	v0.4s, v2.4s, v17.4s
    2a10:	add	v0.4s, v0.4s, v16.4s
    2a14:	add	v0.4s, v0.4s, v7.4s
    2a18:	add	v0.4s, v0.4s, v6.4s
    2a1c:	add	v0.4s, v0.4s, v5.4s
    2a20:	add	v0.4s, v0.4s, v4.4s
    2a24:	add	v0.4s, v0.4s, v3.4s
    2a28:	addv	s0, v0.4s
    2a2c:	fmov	w0, s0
    2a30:	ret
    2a34:	mov	x0, #0x90                  	// #144
    2a38:	ret

Disassembly of section .fini:

# ===== peak_sdot_a16: hot loop = the 19 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002a40 <peak_sdot_a16>:
    2a40:	adrp	x1, 20000 <__data_start>
    2a44:	add	x2, x1, #0x10
    2a48:	ldr	b0, [x1, #16]
    2a4c:	ldr	b1, [x2, #1]
    2a50:	dup	v0.16b, v0.b[0]
    2a54:	dup	v1.16b, v1.b[0]
    2a58:	cbz	x0, 2b34 <peak_sdot_a16+0xf4>
    2a5c:	movi	v3.4s, #0x10
    2a60:	movi	v4.4s, #0xf
    2a64:	mov	x1, #0x0                   	// #0
    2a68:	movi	v5.4s, #0xe
    2a6c:	movi	v6.4s, #0xd
    2a70:	movi	v7.4s, #0xc
    2a74:	movi	v16.4s, #0xb
    2a78:	movi	v17.4s, #0xa
    2a7c:	movi	v18.4s, #0x9
    2a80:	movi	v19.4s, #0x8
    2a84:	movi	v20.4s, #0x7
    2a88:	movi	v21.4s, #0x6
    2a8c:	movi	v22.4s, #0x5
    2a90:	movi	v23.4s, #0x4
    2a94:	movi	v24.4s, #0x3
    2a98:	movi	v25.4s, #0x2
    2a9c:	movi	v2.4s, #0x1
    2aa0:	add	x1, x1, #0x1
    2aa4:	sdot	v2.4s, v0.16b, v1.16b
    2aa8:	sdot	v25.4s, v0.16b, v1.16b
    2aac:	sdot	v24.4s, v0.16b, v1.16b
    2ab0:	sdot	v23.4s, v0.16b, v1.16b
    2ab4:	sdot	v22.4s, v0.16b, v1.16b
    2ab8:	sdot	v21.4s, v0.16b, v1.16b
    2abc:	sdot	v20.4s, v0.16b, v1.16b
    2ac0:	sdot	v19.4s, v0.16b, v1.16b
    2ac4:	sdot	v18.4s, v0.16b, v1.16b
    2ac8:	sdot	v17.4s, v0.16b, v1.16b
    2acc:	sdot	v16.4s, v0.16b, v1.16b
    2ad0:	sdot	v7.4s, v0.16b, v1.16b
    2ad4:	sdot	v6.4s, v0.16b, v1.16b
    2ad8:	sdot	v5.4s, v0.16b, v1.16b
    2adc:	sdot	v4.4s, v0.16b, v1.16b
    2ae0:	sdot	v3.4s, v0.16b, v1.16b
    2ae4:	cmp	x0, x1
    2ae8:	b.ne	2aa0 <peak_sdot_a16+0x60>  // b.any
    2aec:	add	v0.4s, v2.4s, v25.4s
    2af0:	add	v0.4s, v0.4s, v24.4s
    2af4:	add	v0.4s, v0.4s, v23.4s
    2af8:	add	v0.4s, v0.4s, v22.4s
    2afc:	add	v0.4s, v0.4s, v21.4s
    2b00:	add	v0.4s, v0.4s, v20.4s
    2b04:	add	v0.4s, v0.4s, v19.4s
    2b08:	add	v0.4s, v0.4s, v18.4s
    2b0c:	add	v0.4s, v0.4s, v17.4s
    2b10:	add	v0.4s, v0.4s, v16.4s
    2b14:	add	v0.4s, v0.4s, v7.4s
    2b18:	add	v0.4s, v0.4s, v6.4s
    2b1c:	add	v0.4s, v0.4s, v5.4s
    2b20:	add	v0.4s, v0.4s, v4.4s
    2b24:	add	v0.4s, v0.4s, v3.4s
    2b28:	addv	s0, v0.4s
    2b2c:	fmov	w0, s0
    2b30:	ret
    2b34:	mov	x0, #0x220                 	// #544
    2b38:	ret

Disassembly of section .fini:

# ===== peak_sdot_a28: hot loop = the 31 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002b40 <peak_sdot_a28>:
    2b40:	adrp	x1, 20000 <__data_start>
    2b44:	add	x2, x1, #0x10
    2b48:	ldr	b0, [x1, #16]
    2b4c:	ldr	b1, [x2, #1]
    2b50:	cbz	x0, 2ce0 <peak_sdot_a28+0x1a0>
    2b54:	stp	d8, d9, [sp, #-48]!
    2b58:	dup	v0.16b, v0.b[0]
    2b5c:	dup	v1.16b, v1.b[0]
    2b60:	mov	x1, #0x0                   	// #0
    2b64:	movi	v3.4s, #0x1c
    2b68:	movi	v4.4s, #0x1b
    2b6c:	stp	d10, d11, [sp, #16]
    2b70:	movi	v5.4s, #0x1a
    2b74:	movi	v6.4s, #0x19
    2b78:	stp	d12, d13, [sp, #32]
    2b7c:	movi	v7.4s, #0x18
    2b80:	movi	v16.4s, #0x17
    2b84:	movi	v17.4s, #0x16
    2b88:	movi	v18.4s, #0x15
    2b8c:	movi	v19.4s, #0x14
    2b90:	movi	v20.4s, #0x13
    2b94:	movi	v21.4s, #0x12
    2b98:	movi	v22.4s, #0x11
    2b9c:	movi	v23.4s, #0x10
    2ba0:	movi	v24.4s, #0xf
    2ba4:	movi	v25.4s, #0xe
    2ba8:	movi	v26.4s, #0xd
    2bac:	movi	v27.4s, #0xc
    2bb0:	movi	v28.4s, #0xb
    2bb4:	movi	v29.4s, #0xa
    2bb8:	movi	v30.4s, #0x9
    2bbc:	movi	v31.4s, #0x8
    2bc0:	movi	v8.4s, #0x7
    2bc4:	movi	v9.4s, #0x6
    2bc8:	movi	v10.4s, #0x5
    2bcc:	movi	v11.4s, #0x4
    2bd0:	movi	v12.4s, #0x3
    2bd4:	movi	v13.4s, #0x2
    2bd8:	movi	v2.4s, #0x1
    2bdc:	nop
    2be0:	add	x1, x1, #0x1
    2be4:	sdot	v2.4s, v0.16b, v1.16b
    2be8:	sdot	v13.4s, v0.16b, v1.16b
    2bec:	sdot	v12.4s, v0.16b, v1.16b
    2bf0:	sdot	v11.4s, v0.16b, v1.16b
    2bf4:	sdot	v10.4s, v0.16b, v1.16b
    2bf8:	sdot	v9.4s, v0.16b, v1.16b
    2bfc:	sdot	v8.4s, v0.16b, v1.16b
    2c00:	sdot	v31.4s, v0.16b, v1.16b
    2c04:	sdot	v30.4s, v0.16b, v1.16b
    2c08:	sdot	v29.4s, v0.16b, v1.16b
    2c0c:	sdot	v28.4s, v0.16b, v1.16b
    2c10:	sdot	v27.4s, v0.16b, v1.16b
    2c14:	sdot	v26.4s, v0.16b, v1.16b
    2c18:	sdot	v25.4s, v0.16b, v1.16b
    2c1c:	sdot	v24.4s, v0.16b, v1.16b
    2c20:	sdot	v23.4s, v0.16b, v1.16b
    2c24:	sdot	v22.4s, v0.16b, v1.16b
    2c28:	sdot	v21.4s, v0.16b, v1.16b
    2c2c:	sdot	v20.4s, v0.16b, v1.16b
    2c30:	sdot	v19.4s, v0.16b, v1.16b
    2c34:	sdot	v18.4s, v0.16b, v1.16b
    2c38:	sdot	v17.4s, v0.16b, v1.16b
    2c3c:	sdot	v16.4s, v0.16b, v1.16b
    2c40:	sdot	v7.4s, v0.16b, v1.16b
    2c44:	sdot	v6.4s, v0.16b, v1.16b
    2c48:	sdot	v5.4s, v0.16b, v1.16b
    2c4c:	sdot	v4.4s, v0.16b, v1.16b
    2c50:	sdot	v3.4s, v0.16b, v1.16b
    2c54:	cmp	x0, x1
    2c58:	b.ne	2be0 <peak_sdot_a28+0xa0>  // b.any
    2c5c:	add	v0.4s, v2.4s, v13.4s
    2c60:	add	v0.4s, v0.4s, v12.4s
    2c64:	ldp	d12, d13, [sp, #32]
    2c68:	add	v0.4s, v0.4s, v11.4s
    2c6c:	add	v0.4s, v0.4s, v10.4s
    2c70:	ldp	d10, d11, [sp, #16]
    2c74:	add	v0.4s, v0.4s, v9.4s
    2c78:	add	v0.4s, v0.4s, v8.4s
    2c7c:	ldp	d8, d9, [sp], #48
    2c80:	add	v0.4s, v0.4s, v31.4s
    2c84:	add	v0.4s, v0.4s, v30.4s
    2c88:	add	v0.4s, v0.4s, v29.4s
    2c8c:	add	v0.4s, v0.4s, v28.4s
    2c90:	add	v0.4s, v0.4s, v27.4s
    2c94:	add	v0.4s, v0.4s, v26.4s
    2c98:	add	v0.4s, v0.4s, v25.4s
    2c9c:	add	v0.4s, v0.4s, v24.4s
    2ca0:	add	v0.4s, v0.4s, v23.4s
    2ca4:	add	v0.4s, v0.4s, v22.4s
    2ca8:	add	v0.4s, v0.4s, v21.4s
    2cac:	add	v0.4s, v0.4s, v20.4s
    2cb0:	add	v0.4s, v0.4s, v19.4s
    2cb4:	add	v0.4s, v0.4s, v18.4s
    2cb8:	add	v0.4s, v0.4s, v17.4s
    2cbc:	add	v0.4s, v0.4s, v16.4s
    2cc0:	add	v0.4s, v0.4s, v7.4s
    2cc4:	add	v0.4s, v0.4s, v6.4s
    2cc8:	add	v0.4s, v0.4s, v5.4s
    2ccc:	add	v0.4s, v0.4s, v4.4s
    2cd0:	add	v0.4s, v0.4s, v3.4s
    2cd4:	addv	s0, v0.4s
    2cd8:	fmov	w0, s0
    2cdc:	ret
    2ce0:	mov	x0, #0x658                 	// #1624
    2ce4:	ret

Disassembly of section .fini:
