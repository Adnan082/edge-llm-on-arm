# ===== peak_smmla_a8: hot loop = the 11 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002ca8 <peak_smmla_a8>:
    2ca8:	adrp	x1, 20000 <__data_start>
    2cac:	add	x1, x1, #0x10
    2cb0:	ldr	b0, [x1, #2]
    2cb4:	ldr	b1, [x1, #3]
    2cb8:	dup	v0.16b, v0.b[0]
    2cbc:	dup	v1.16b, v1.b[0]
    2cc0:	cbz	x0, 2d3c <peak_smmla_a8+0x94>
    2cc4:	movi	v3.4s, #0x8
    2cc8:	movi	v4.4s, #0x7
    2ccc:	mov	x1, #0x0                   	// #0
    2cd0:	movi	v5.4s, #0x6
    2cd4:	movi	v6.4s, #0x5
    2cd8:	movi	v7.4s, #0x4
    2cdc:	movi	v16.4s, #0x3
    2ce0:	movi	v17.4s, #0x2
    2ce4:	movi	v2.4s, #0x1
    2ce8:	add	x1, x1, #0x1
    2cec:	smmla	v2.4s, v0.16b, v1.16b
    2cf0:	smmla	v17.4s, v0.16b, v1.16b
    2cf4:	smmla	v16.4s, v0.16b, v1.16b
    2cf8:	smmla	v7.4s, v0.16b, v1.16b
    2cfc:	smmla	v6.4s, v0.16b, v1.16b
    2d00:	smmla	v5.4s, v0.16b, v1.16b
    2d04:	smmla	v4.4s, v0.16b, v1.16b
    2d08:	smmla	v3.4s, v0.16b, v1.16b
    2d0c:	cmp	x0, x1
    2d10:	b.ne	2ce8 <peak_smmla_a8+0x40>  // b.any
    2d14:	add	v0.4s, v2.4s, v17.4s
    2d18:	add	v0.4s, v0.4s, v16.4s
    2d1c:	add	v0.4s, v0.4s, v7.4s
    2d20:	add	v0.4s, v0.4s, v6.4s
    2d24:	add	v0.4s, v0.4s, v5.4s
    2d28:	add	v0.4s, v0.4s, v4.4s
    2d2c:	add	v0.4s, v0.4s, v3.4s
    2d30:	addv	s0, v0.4s
    2d34:	fmov	w0, s0
    2d38:	ret
    2d3c:	mov	x0, #0x90                  	// #144
    2d40:	ret

Disassembly of section .fini:

# ===== peak_smmla_a16: hot loop = the 19 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002d44 <peak_smmla_a16>:
    2d44:	adrp	x1, 20000 <__data_start>
    2d48:	add	x1, x1, #0x10
    2d4c:	ldr	b0, [x1, #2]
    2d50:	ldr	b1, [x1, #3]
    2d54:	dup	v0.16b, v0.b[0]
    2d58:	dup	v1.16b, v1.b[0]
    2d5c:	cbz	x0, 2e38 <peak_smmla_a16+0xf4>
    2d60:	movi	v3.4s, #0x10
    2d64:	movi	v4.4s, #0xf
    2d68:	mov	x1, #0x0                   	// #0
    2d6c:	movi	v5.4s, #0xe
    2d70:	movi	v6.4s, #0xd
    2d74:	movi	v7.4s, #0xc
    2d78:	movi	v16.4s, #0xb
    2d7c:	movi	v17.4s, #0xa
    2d80:	movi	v18.4s, #0x9
    2d84:	movi	v19.4s, #0x8
    2d88:	movi	v20.4s, #0x7
    2d8c:	movi	v21.4s, #0x6
    2d90:	movi	v22.4s, #0x5
    2d94:	movi	v23.4s, #0x4
    2d98:	movi	v24.4s, #0x3
    2d9c:	movi	v25.4s, #0x2
    2da0:	movi	v2.4s, #0x1
    2da4:	add	x1, x1, #0x1
    2da8:	smmla	v2.4s, v0.16b, v1.16b
    2dac:	smmla	v25.4s, v0.16b, v1.16b
    2db0:	smmla	v24.4s, v0.16b, v1.16b
    2db4:	smmla	v23.4s, v0.16b, v1.16b
    2db8:	smmla	v22.4s, v0.16b, v1.16b
    2dbc:	smmla	v21.4s, v0.16b, v1.16b
    2dc0:	smmla	v20.4s, v0.16b, v1.16b
    2dc4:	smmla	v19.4s, v0.16b, v1.16b
    2dc8:	smmla	v18.4s, v0.16b, v1.16b
    2dcc:	smmla	v17.4s, v0.16b, v1.16b
    2dd0:	smmla	v16.4s, v0.16b, v1.16b
    2dd4:	smmla	v7.4s, v0.16b, v1.16b
    2dd8:	smmla	v6.4s, v0.16b, v1.16b
    2ddc:	smmla	v5.4s, v0.16b, v1.16b
    2de0:	smmla	v4.4s, v0.16b, v1.16b
    2de4:	smmla	v3.4s, v0.16b, v1.16b
    2de8:	cmp	x0, x1
    2dec:	b.ne	2da4 <peak_smmla_a16+0x60>  // b.any
    2df0:	add	v0.4s, v2.4s, v25.4s
    2df4:	add	v0.4s, v0.4s, v24.4s
    2df8:	add	v0.4s, v0.4s, v23.4s
    2dfc:	add	v0.4s, v0.4s, v22.4s
    2e00:	add	v0.4s, v0.4s, v21.4s
    2e04:	add	v0.4s, v0.4s, v20.4s
    2e08:	add	v0.4s, v0.4s, v19.4s
    2e0c:	add	v0.4s, v0.4s, v18.4s
    2e10:	add	v0.4s, v0.4s, v17.4s
    2e14:	add	v0.4s, v0.4s, v16.4s
    2e18:	add	v0.4s, v0.4s, v7.4s
    2e1c:	add	v0.4s, v0.4s, v6.4s
    2e20:	add	v0.4s, v0.4s, v5.4s
    2e24:	add	v0.4s, v0.4s, v4.4s
    2e28:	add	v0.4s, v0.4s, v3.4s
    2e2c:	addv	s0, v0.4s
    2e30:	fmov	w0, s0
    2e34:	ret
    2e38:	mov	x0, #0x220                 	// #544
    2e3c:	ret

Disassembly of section .fini:

# ===== peak_smmla_a28: hot loop = the 31 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002e40 <peak_smmla_a28>:
    2e40:	adrp	x1, 20000 <__data_start>
    2e44:	add	x1, x1, #0x10
    2e48:	ldr	b0, [x1, #2]
    2e4c:	ldr	b1, [x1, #3]
    2e50:	cbz	x0, 2fe0 <peak_smmla_a28+0x1a0>
    2e54:	stp	d8, d9, [sp, #-48]!
    2e58:	dup	v0.16b, v0.b[0]
    2e5c:	dup	v1.16b, v1.b[0]
    2e60:	mov	x1, #0x0                   	// #0
    2e64:	movi	v3.4s, #0x1c
    2e68:	movi	v4.4s, #0x1b
    2e6c:	stp	d10, d11, [sp, #16]
    2e70:	movi	v5.4s, #0x1a
    2e74:	movi	v6.4s, #0x19
    2e78:	stp	d12, d13, [sp, #32]
    2e7c:	movi	v7.4s, #0x18
    2e80:	movi	v16.4s, #0x17
    2e84:	movi	v17.4s, #0x16
    2e88:	movi	v18.4s, #0x15
    2e8c:	movi	v19.4s, #0x14
    2e90:	movi	v20.4s, #0x13
    2e94:	movi	v21.4s, #0x12
    2e98:	movi	v22.4s, #0x11
    2e9c:	movi	v23.4s, #0x10
    2ea0:	movi	v24.4s, #0xf
    2ea4:	movi	v25.4s, #0xe
    2ea8:	movi	v26.4s, #0xd
    2eac:	movi	v27.4s, #0xc
    2eb0:	movi	v28.4s, #0xb
    2eb4:	movi	v29.4s, #0xa
    2eb8:	movi	v30.4s, #0x9
    2ebc:	movi	v31.4s, #0x8
    2ec0:	movi	v8.4s, #0x7
    2ec4:	movi	v9.4s, #0x6
    2ec8:	movi	v10.4s, #0x5
    2ecc:	movi	v11.4s, #0x4
    2ed0:	movi	v12.4s, #0x3
    2ed4:	movi	v13.4s, #0x2
    2ed8:	movi	v2.4s, #0x1
    2edc:	nop
    2ee0:	add	x1, x1, #0x1
    2ee4:	smmla	v2.4s, v0.16b, v1.16b
    2ee8:	smmla	v13.4s, v0.16b, v1.16b
    2eec:	smmla	v12.4s, v0.16b, v1.16b
    2ef0:	smmla	v11.4s, v0.16b, v1.16b
    2ef4:	smmla	v10.4s, v0.16b, v1.16b
    2ef8:	smmla	v9.4s, v0.16b, v1.16b
    2efc:	smmla	v8.4s, v0.16b, v1.16b
    2f00:	smmla	v31.4s, v0.16b, v1.16b
    2f04:	smmla	v30.4s, v0.16b, v1.16b
    2f08:	smmla	v29.4s, v0.16b, v1.16b
    2f0c:	smmla	v28.4s, v0.16b, v1.16b
    2f10:	smmla	v27.4s, v0.16b, v1.16b
    2f14:	smmla	v26.4s, v0.16b, v1.16b
    2f18:	smmla	v25.4s, v0.16b, v1.16b
    2f1c:	smmla	v24.4s, v0.16b, v1.16b
    2f20:	smmla	v23.4s, v0.16b, v1.16b
    2f24:	smmla	v22.4s, v0.16b, v1.16b
    2f28:	smmla	v21.4s, v0.16b, v1.16b
    2f2c:	smmla	v20.4s, v0.16b, v1.16b
    2f30:	smmla	v19.4s, v0.16b, v1.16b
    2f34:	smmla	v18.4s, v0.16b, v1.16b
    2f38:	smmla	v17.4s, v0.16b, v1.16b
    2f3c:	smmla	v16.4s, v0.16b, v1.16b
    2f40:	smmla	v7.4s, v0.16b, v1.16b
    2f44:	smmla	v6.4s, v0.16b, v1.16b
    2f48:	smmla	v5.4s, v0.16b, v1.16b
    2f4c:	smmla	v4.4s, v0.16b, v1.16b
    2f50:	smmla	v3.4s, v0.16b, v1.16b
    2f54:	cmp	x0, x1
    2f58:	b.ne	2ee0 <peak_smmla_a28+0xa0>  // b.any
    2f5c:	add	v0.4s, v2.4s, v13.4s
    2f60:	add	v0.4s, v0.4s, v12.4s
    2f64:	ldp	d12, d13, [sp, #32]
    2f68:	add	v0.4s, v0.4s, v11.4s
    2f6c:	add	v0.4s, v0.4s, v10.4s
    2f70:	ldp	d10, d11, [sp, #16]
    2f74:	add	v0.4s, v0.4s, v9.4s
    2f78:	add	v0.4s, v0.4s, v8.4s
    2f7c:	ldp	d8, d9, [sp], #48
    2f80:	add	v0.4s, v0.4s, v31.4s
    2f84:	add	v0.4s, v0.4s, v30.4s
    2f88:	add	v0.4s, v0.4s, v29.4s
    2f8c:	add	v0.4s, v0.4s, v28.4s
    2f90:	add	v0.4s, v0.4s, v27.4s
    2f94:	add	v0.4s, v0.4s, v26.4s
    2f98:	add	v0.4s, v0.4s, v25.4s
    2f9c:	add	v0.4s, v0.4s, v24.4s
    2fa0:	add	v0.4s, v0.4s, v23.4s
    2fa4:	add	v0.4s, v0.4s, v22.4s
    2fa8:	add	v0.4s, v0.4s, v21.4s
    2fac:	add	v0.4s, v0.4s, v20.4s
    2fb0:	add	v0.4s, v0.4s, v19.4s
    2fb4:	add	v0.4s, v0.4s, v18.4s
    2fb8:	add	v0.4s, v0.4s, v17.4s
    2fbc:	add	v0.4s, v0.4s, v16.4s
    2fc0:	add	v0.4s, v0.4s, v7.4s
    2fc4:	add	v0.4s, v0.4s, v6.4s
    2fc8:	add	v0.4s, v0.4s, v5.4s
    2fcc:	add	v0.4s, v0.4s, v4.4s
    2fd0:	add	v0.4s, v0.4s, v3.4s
    2fd4:	addv	s0, v0.4s
    2fd8:	fmov	w0, s0
    2fdc:	ret
    2fe0:	mov	x0, #0x658                 	// #1624
    2fe4:	ret

Disassembly of section .fini:
