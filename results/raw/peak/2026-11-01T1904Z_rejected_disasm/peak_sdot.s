# ===== peak_sdot_a8: hot loop = the 11 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002960 <peak_sdot_a8>:
    2960:	adrp	x1, 20000 <__data_start>
    2964:	add	x2, x1, #0x10
    2968:	ldr	b0, [x1, #16]
    296c:	ldr	b1, [x2, #1]
    2970:	dup	v0.16b, v0.b[0]
    2974:	dup	v1.16b, v1.b[0]
    2978:	cbz	x0, 29f4 <peak_sdot_a8+0x94>
    297c:	movi	v3.4s, #0x8
    2980:	movi	v4.4s, #0x7
    2984:	mov	x1, #0x0                   	// #0
    2988:	movi	v5.4s, #0x6
    298c:	movi	v6.4s, #0x5
    2990:	movi	v7.4s, #0x4
    2994:	movi	v16.4s, #0x3
    2998:	movi	v17.4s, #0x2
    299c:	movi	v2.4s, #0x1
    29a0:	add	x1, x1, #0x1
    29a4:	sdot	v2.4s, v0.16b, v1.16b
    29a8:	sdot	v17.4s, v0.16b, v1.16b
    29ac:	sdot	v16.4s, v0.16b, v1.16b
    29b0:	sdot	v7.4s, v0.16b, v1.16b
    29b4:	sdot	v6.4s, v0.16b, v1.16b
    29b8:	sdot	v5.4s, v0.16b, v1.16b
    29bc:	sdot	v4.4s, v0.16b, v1.16b
    29c0:	sdot	v3.4s, v0.16b, v1.16b
    29c4:	cmp	x0, x1
    29c8:	b.ne	29a0 <peak_sdot_a8+0x40>  // b.any
    29cc:	add	v0.4s, v2.4s, v17.4s
    29d0:	add	v0.4s, v0.4s, v16.4s
    29d4:	add	v0.4s, v0.4s, v7.4s
    29d8:	add	v0.4s, v0.4s, v6.4s
    29dc:	add	v0.4s, v0.4s, v5.4s
    29e0:	add	v0.4s, v0.4s, v4.4s
    29e4:	add	v0.4s, v0.4s, v3.4s
    29e8:	addv	s0, v0.4s
    29ec:	fmov	w0, s0
    29f0:	ret
    29f4:	mov	x0, #0x90                  	// #144
    29f8:	ret

Disassembly of section .fini:

# ===== peak_sdot_a16: hot loop = the 19 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002a00 <peak_sdot_a16>:
    2a00:	adrp	x1, 20000 <__data_start>
    2a04:	add	x2, x1, #0x10
    2a08:	ldr	b0, [x1, #16]
    2a0c:	ldr	b1, [x2, #1]
    2a10:	dup	v0.16b, v0.b[0]
    2a14:	dup	v1.16b, v1.b[0]
    2a18:	cbz	x0, 2af4 <peak_sdot_a16+0xf4>
    2a1c:	movi	v3.4s, #0x10
    2a20:	movi	v4.4s, #0xf
    2a24:	mov	x1, #0x0                   	// #0
    2a28:	movi	v5.4s, #0xe
    2a2c:	movi	v6.4s, #0xd
    2a30:	movi	v7.4s, #0xc
    2a34:	movi	v16.4s, #0xb
    2a38:	movi	v17.4s, #0xa
    2a3c:	movi	v18.4s, #0x9
    2a40:	movi	v19.4s, #0x8
    2a44:	movi	v20.4s, #0x7
    2a48:	movi	v21.4s, #0x6
    2a4c:	movi	v22.4s, #0x5
    2a50:	movi	v23.4s, #0x4
    2a54:	movi	v24.4s, #0x3
    2a58:	movi	v25.4s, #0x2
    2a5c:	movi	v2.4s, #0x1
    2a60:	add	x1, x1, #0x1
    2a64:	sdot	v2.4s, v0.16b, v1.16b
    2a68:	sdot	v25.4s, v0.16b, v1.16b
    2a6c:	sdot	v24.4s, v0.16b, v1.16b
    2a70:	sdot	v23.4s, v0.16b, v1.16b
    2a74:	sdot	v22.4s, v0.16b, v1.16b
    2a78:	sdot	v21.4s, v0.16b, v1.16b
    2a7c:	sdot	v20.4s, v0.16b, v1.16b
    2a80:	sdot	v19.4s, v0.16b, v1.16b
    2a84:	sdot	v18.4s, v0.16b, v1.16b
    2a88:	sdot	v17.4s, v0.16b, v1.16b
    2a8c:	sdot	v16.4s, v0.16b, v1.16b
    2a90:	sdot	v7.4s, v0.16b, v1.16b
    2a94:	sdot	v6.4s, v0.16b, v1.16b
    2a98:	sdot	v5.4s, v0.16b, v1.16b
    2a9c:	sdot	v4.4s, v0.16b, v1.16b
    2aa0:	sdot	v3.4s, v0.16b, v1.16b
    2aa4:	cmp	x0, x1
    2aa8:	b.ne	2a60 <peak_sdot_a16+0x60>  // b.any
    2aac:	add	v0.4s, v2.4s, v25.4s
    2ab0:	add	v0.4s, v0.4s, v24.4s
    2ab4:	add	v0.4s, v0.4s, v23.4s
    2ab8:	add	v0.4s, v0.4s, v22.4s
    2abc:	add	v0.4s, v0.4s, v21.4s
    2ac0:	add	v0.4s, v0.4s, v20.4s
    2ac4:	add	v0.4s, v0.4s, v19.4s
    2ac8:	add	v0.4s, v0.4s, v18.4s
    2acc:	add	v0.4s, v0.4s, v17.4s
    2ad0:	add	v0.4s, v0.4s, v16.4s
    2ad4:	add	v0.4s, v0.4s, v7.4s
    2ad8:	add	v0.4s, v0.4s, v6.4s
    2adc:	add	v0.4s, v0.4s, v5.4s
    2ae0:	add	v0.4s, v0.4s, v4.4s
    2ae4:	add	v0.4s, v0.4s, v3.4s
    2ae8:	addv	s0, v0.4s
    2aec:	fmov	w0, s0
    2af0:	ret
    2af4:	mov	x0, #0x220                 	// #544
    2af8:	ret

Disassembly of section .fini:

# ===== peak_sdot_a28: hot loop = the 31 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002b00 <peak_sdot_a28>:
    2b00:	adrp	x1, 20000 <__data_start>
    2b04:	add	x2, x1, #0x10
    2b08:	ldr	b0, [x1, #16]
    2b0c:	ldr	b1, [x2, #1]
    2b10:	cbz	x0, 2ca0 <peak_sdot_a28+0x1a0>
    2b14:	stp	d8, d9, [sp, #-48]!
    2b18:	dup	v0.16b, v0.b[0]
    2b1c:	dup	v1.16b, v1.b[0]
    2b20:	mov	x1, #0x0                   	// #0
    2b24:	movi	v3.4s, #0x1c
    2b28:	movi	v4.4s, #0x1b
    2b2c:	stp	d10, d11, [sp, #16]
    2b30:	movi	v5.4s, #0x1a
    2b34:	movi	v6.4s, #0x19
    2b38:	stp	d12, d13, [sp, #32]
    2b3c:	movi	v7.4s, #0x18
    2b40:	movi	v16.4s, #0x17
    2b44:	movi	v17.4s, #0x16
    2b48:	movi	v18.4s, #0x15
    2b4c:	movi	v19.4s, #0x14
    2b50:	movi	v20.4s, #0x13
    2b54:	movi	v21.4s, #0x12
    2b58:	movi	v22.4s, #0x11
    2b5c:	movi	v23.4s, #0x10
    2b60:	movi	v24.4s, #0xf
    2b64:	movi	v25.4s, #0xe
    2b68:	movi	v26.4s, #0xd
    2b6c:	movi	v27.4s, #0xc
    2b70:	movi	v28.4s, #0xb
    2b74:	movi	v29.4s, #0xa
    2b78:	movi	v30.4s, #0x9
    2b7c:	movi	v31.4s, #0x8
    2b80:	movi	v8.4s, #0x7
    2b84:	movi	v9.4s, #0x6
    2b88:	movi	v10.4s, #0x5
    2b8c:	movi	v11.4s, #0x4
    2b90:	movi	v12.4s, #0x3
    2b94:	movi	v13.4s, #0x2
    2b98:	movi	v2.4s, #0x1
    2b9c:	nop
    2ba0:	add	x1, x1, #0x1
    2ba4:	sdot	v2.4s, v0.16b, v1.16b
    2ba8:	sdot	v13.4s, v0.16b, v1.16b
    2bac:	sdot	v12.4s, v0.16b, v1.16b
    2bb0:	sdot	v11.4s, v0.16b, v1.16b
    2bb4:	sdot	v10.4s, v0.16b, v1.16b
    2bb8:	sdot	v9.4s, v0.16b, v1.16b
    2bbc:	sdot	v8.4s, v0.16b, v1.16b
    2bc0:	sdot	v31.4s, v0.16b, v1.16b
    2bc4:	sdot	v30.4s, v0.16b, v1.16b
    2bc8:	sdot	v29.4s, v0.16b, v1.16b
    2bcc:	sdot	v28.4s, v0.16b, v1.16b
    2bd0:	sdot	v27.4s, v0.16b, v1.16b
    2bd4:	sdot	v26.4s, v0.16b, v1.16b
    2bd8:	sdot	v25.4s, v0.16b, v1.16b
    2bdc:	sdot	v24.4s, v0.16b, v1.16b
    2be0:	sdot	v23.4s, v0.16b, v1.16b
    2be4:	sdot	v22.4s, v0.16b, v1.16b
    2be8:	sdot	v21.4s, v0.16b, v1.16b
    2bec:	sdot	v20.4s, v0.16b, v1.16b
    2bf0:	sdot	v19.4s, v0.16b, v1.16b
    2bf4:	sdot	v18.4s, v0.16b, v1.16b
    2bf8:	sdot	v17.4s, v0.16b, v1.16b
    2bfc:	sdot	v16.4s, v0.16b, v1.16b
    2c00:	sdot	v7.4s, v0.16b, v1.16b
    2c04:	sdot	v6.4s, v0.16b, v1.16b
    2c08:	sdot	v5.4s, v0.16b, v1.16b
    2c0c:	sdot	v4.4s, v0.16b, v1.16b
    2c10:	sdot	v3.4s, v0.16b, v1.16b
    2c14:	cmp	x0, x1
    2c18:	b.ne	2ba0 <peak_sdot_a28+0xa0>  // b.any
    2c1c:	add	v0.4s, v2.4s, v13.4s
    2c20:	add	v0.4s, v0.4s, v12.4s
    2c24:	ldp	d12, d13, [sp, #32]
    2c28:	add	v0.4s, v0.4s, v11.4s
    2c2c:	add	v0.4s, v0.4s, v10.4s
    2c30:	ldp	d10, d11, [sp, #16]
    2c34:	add	v0.4s, v0.4s, v9.4s
    2c38:	add	v0.4s, v0.4s, v8.4s
    2c3c:	ldp	d8, d9, [sp], #48
    2c40:	add	v0.4s, v0.4s, v31.4s
    2c44:	add	v0.4s, v0.4s, v30.4s
    2c48:	add	v0.4s, v0.4s, v29.4s
    2c4c:	add	v0.4s, v0.4s, v28.4s
    2c50:	add	v0.4s, v0.4s, v27.4s
    2c54:	add	v0.4s, v0.4s, v26.4s
    2c58:	add	v0.4s, v0.4s, v25.4s
    2c5c:	add	v0.4s, v0.4s, v24.4s
    2c60:	add	v0.4s, v0.4s, v23.4s
    2c64:	add	v0.4s, v0.4s, v22.4s
    2c68:	add	v0.4s, v0.4s, v21.4s
    2c6c:	add	v0.4s, v0.4s, v20.4s
    2c70:	add	v0.4s, v0.4s, v19.4s
    2c74:	add	v0.4s, v0.4s, v18.4s
    2c78:	add	v0.4s, v0.4s, v17.4s
    2c7c:	add	v0.4s, v0.4s, v16.4s
    2c80:	add	v0.4s, v0.4s, v7.4s
    2c84:	add	v0.4s, v0.4s, v6.4s
    2c88:	add	v0.4s, v0.4s, v5.4s
    2c8c:	add	v0.4s, v0.4s, v4.4s
    2c90:	add	v0.4s, v0.4s, v3.4s
    2c94:	addv	s0, v0.4s
    2c98:	fmov	w0, s0
    2c9c:	ret
    2ca0:	mov	x0, #0x658                 	// #1624
    2ca4:	ret

Disassembly of section .fini:
