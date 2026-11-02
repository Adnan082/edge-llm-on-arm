# ===== peak_smmla_a8: hot loop = the 11 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002ce8 <peak_smmla_a8>:
    2ce8:	adrp	x1, 20000 <__data_start>
    2cec:	add	x1, x1, #0x10
    2cf0:	ldr	b0, [x1, #2]
    2cf4:	ldr	b1, [x1, #3]
    2cf8:	dup	v0.16b, v0.b[0]
    2cfc:	dup	v1.16b, v1.b[0]
    2d00:	cbz	x0, 2d7c <peak_smmla_a8+0x94>
    2d04:	movi	v3.4s, #0x8
    2d08:	movi	v4.4s, #0x7
    2d0c:	mov	x1, #0x0                   	// #0
    2d10:	movi	v5.4s, #0x6
    2d14:	movi	v6.4s, #0x5
    2d18:	movi	v7.4s, #0x4
    2d1c:	movi	v16.4s, #0x3
    2d20:	movi	v17.4s, #0x2
    2d24:	movi	v2.4s, #0x1
    2d28:	add	x1, x1, #0x1
    2d2c:	smmla	v2.4s, v0.16b, v1.16b
    2d30:	smmla	v17.4s, v0.16b, v1.16b
    2d34:	smmla	v16.4s, v0.16b, v1.16b
    2d38:	smmla	v7.4s, v0.16b, v1.16b
    2d3c:	smmla	v6.4s, v0.16b, v1.16b
    2d40:	smmla	v5.4s, v0.16b, v1.16b
    2d44:	smmla	v4.4s, v0.16b, v1.16b
    2d48:	smmla	v3.4s, v0.16b, v1.16b
    2d4c:	cmp	x0, x1
    2d50:	b.ne	2d28 <peak_smmla_a8+0x40>  // b.any
    2d54:	add	v0.4s, v2.4s, v17.4s
    2d58:	add	v0.4s, v0.4s, v16.4s
    2d5c:	add	v0.4s, v0.4s, v7.4s
    2d60:	add	v0.4s, v0.4s, v6.4s
    2d64:	add	v0.4s, v0.4s, v5.4s
    2d68:	add	v0.4s, v0.4s, v4.4s
    2d6c:	add	v0.4s, v0.4s, v3.4s
    2d70:	addv	s0, v0.4s
    2d74:	fmov	w0, s0
    2d78:	ret
    2d7c:	mov	x0, #0x90                  	// #144
    2d80:	ret

Disassembly of section .fini:

# ===== peak_smmla_a16: hot loop = the 19 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002d84 <peak_smmla_a16>:
    2d84:	adrp	x1, 20000 <__data_start>
    2d88:	add	x1, x1, #0x10
    2d8c:	ldr	b0, [x1, #2]
    2d90:	ldr	b1, [x1, #3]
    2d94:	dup	v0.16b, v0.b[0]
    2d98:	dup	v1.16b, v1.b[0]
    2d9c:	cbz	x0, 2e78 <peak_smmla_a16+0xf4>
    2da0:	movi	v3.4s, #0x10
    2da4:	movi	v4.4s, #0xf
    2da8:	mov	x1, #0x0                   	// #0
    2dac:	movi	v5.4s, #0xe
    2db0:	movi	v6.4s, #0xd
    2db4:	movi	v7.4s, #0xc
    2db8:	movi	v16.4s, #0xb
    2dbc:	movi	v17.4s, #0xa
    2dc0:	movi	v18.4s, #0x9
    2dc4:	movi	v19.4s, #0x8
    2dc8:	movi	v20.4s, #0x7
    2dcc:	movi	v21.4s, #0x6
    2dd0:	movi	v22.4s, #0x5
    2dd4:	movi	v23.4s, #0x4
    2dd8:	movi	v24.4s, #0x3
    2ddc:	movi	v25.4s, #0x2
    2de0:	movi	v2.4s, #0x1
    2de4:	add	x1, x1, #0x1
    2de8:	smmla	v2.4s, v0.16b, v1.16b
    2dec:	smmla	v25.4s, v0.16b, v1.16b
    2df0:	smmla	v24.4s, v0.16b, v1.16b
    2df4:	smmla	v23.4s, v0.16b, v1.16b
    2df8:	smmla	v22.4s, v0.16b, v1.16b
    2dfc:	smmla	v21.4s, v0.16b, v1.16b
    2e00:	smmla	v20.4s, v0.16b, v1.16b
    2e04:	smmla	v19.4s, v0.16b, v1.16b
    2e08:	smmla	v18.4s, v0.16b, v1.16b
    2e0c:	smmla	v17.4s, v0.16b, v1.16b
    2e10:	smmla	v16.4s, v0.16b, v1.16b
    2e14:	smmla	v7.4s, v0.16b, v1.16b
    2e18:	smmla	v6.4s, v0.16b, v1.16b
    2e1c:	smmla	v5.4s, v0.16b, v1.16b
    2e20:	smmla	v4.4s, v0.16b, v1.16b
    2e24:	smmla	v3.4s, v0.16b, v1.16b
    2e28:	cmp	x0, x1
    2e2c:	b.ne	2de4 <peak_smmla_a16+0x60>  // b.any
    2e30:	add	v0.4s, v2.4s, v25.4s
    2e34:	add	v0.4s, v0.4s, v24.4s
    2e38:	add	v0.4s, v0.4s, v23.4s
    2e3c:	add	v0.4s, v0.4s, v22.4s
    2e40:	add	v0.4s, v0.4s, v21.4s
    2e44:	add	v0.4s, v0.4s, v20.4s
    2e48:	add	v0.4s, v0.4s, v19.4s
    2e4c:	add	v0.4s, v0.4s, v18.4s
    2e50:	add	v0.4s, v0.4s, v17.4s
    2e54:	add	v0.4s, v0.4s, v16.4s
    2e58:	add	v0.4s, v0.4s, v7.4s
    2e5c:	add	v0.4s, v0.4s, v6.4s
    2e60:	add	v0.4s, v0.4s, v5.4s
    2e64:	add	v0.4s, v0.4s, v4.4s
    2e68:	add	v0.4s, v0.4s, v3.4s
    2e6c:	addv	s0, v0.4s
    2e70:	fmov	w0, s0
    2e74:	ret
    2e78:	mov	x0, #0x220                 	// #544
    2e7c:	ret

Disassembly of section .fini:

# ===== peak_smmla_a28: hot loop = the 31 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002e80 <peak_smmla_a28>:
    2e80:	adrp	x1, 20000 <__data_start>
    2e84:	add	x1, x1, #0x10
    2e88:	ldr	b0, [x1, #2]
    2e8c:	ldr	b1, [x1, #3]
    2e90:	cbz	x0, 3020 <peak_smmla_a28+0x1a0>
    2e94:	stp	d8, d9, [sp, #-48]!
    2e98:	dup	v0.16b, v0.b[0]
    2e9c:	dup	v1.16b, v1.b[0]
    2ea0:	mov	x1, #0x0                   	// #0
    2ea4:	movi	v3.4s, #0x1c
    2ea8:	movi	v4.4s, #0x1b
    2eac:	stp	d10, d11, [sp, #16]
    2eb0:	movi	v5.4s, #0x1a
    2eb4:	movi	v6.4s, #0x19
    2eb8:	stp	d12, d13, [sp, #32]
    2ebc:	movi	v7.4s, #0x18
    2ec0:	movi	v16.4s, #0x17
    2ec4:	movi	v17.4s, #0x16
    2ec8:	movi	v18.4s, #0x15
    2ecc:	movi	v19.4s, #0x14
    2ed0:	movi	v20.4s, #0x13
    2ed4:	movi	v21.4s, #0x12
    2ed8:	movi	v22.4s, #0x11
    2edc:	movi	v23.4s, #0x10
    2ee0:	movi	v24.4s, #0xf
    2ee4:	movi	v25.4s, #0xe
    2ee8:	movi	v26.4s, #0xd
    2eec:	movi	v27.4s, #0xc
    2ef0:	movi	v28.4s, #0xb
    2ef4:	movi	v29.4s, #0xa
    2ef8:	movi	v30.4s, #0x9
    2efc:	movi	v31.4s, #0x8
    2f00:	movi	v8.4s, #0x7
    2f04:	movi	v9.4s, #0x6
    2f08:	movi	v10.4s, #0x5
    2f0c:	movi	v11.4s, #0x4
    2f10:	movi	v12.4s, #0x3
    2f14:	movi	v13.4s, #0x2
    2f18:	movi	v2.4s, #0x1
    2f1c:	nop
    2f20:	add	x1, x1, #0x1
    2f24:	smmla	v2.4s, v0.16b, v1.16b
    2f28:	smmla	v13.4s, v0.16b, v1.16b
    2f2c:	smmla	v12.4s, v0.16b, v1.16b
    2f30:	smmla	v11.4s, v0.16b, v1.16b
    2f34:	smmla	v10.4s, v0.16b, v1.16b
    2f38:	smmla	v9.4s, v0.16b, v1.16b
    2f3c:	smmla	v8.4s, v0.16b, v1.16b
    2f40:	smmla	v31.4s, v0.16b, v1.16b
    2f44:	smmla	v30.4s, v0.16b, v1.16b
    2f48:	smmla	v29.4s, v0.16b, v1.16b
    2f4c:	smmla	v28.4s, v0.16b, v1.16b
    2f50:	smmla	v27.4s, v0.16b, v1.16b
    2f54:	smmla	v26.4s, v0.16b, v1.16b
    2f58:	smmla	v25.4s, v0.16b, v1.16b
    2f5c:	smmla	v24.4s, v0.16b, v1.16b
    2f60:	smmla	v23.4s, v0.16b, v1.16b
    2f64:	smmla	v22.4s, v0.16b, v1.16b
    2f68:	smmla	v21.4s, v0.16b, v1.16b
    2f6c:	smmla	v20.4s, v0.16b, v1.16b
    2f70:	smmla	v19.4s, v0.16b, v1.16b
    2f74:	smmla	v18.4s, v0.16b, v1.16b
    2f78:	smmla	v17.4s, v0.16b, v1.16b
    2f7c:	smmla	v16.4s, v0.16b, v1.16b
    2f80:	smmla	v7.4s, v0.16b, v1.16b
    2f84:	smmla	v6.4s, v0.16b, v1.16b
    2f88:	smmla	v5.4s, v0.16b, v1.16b
    2f8c:	smmla	v4.4s, v0.16b, v1.16b
    2f90:	smmla	v3.4s, v0.16b, v1.16b
    2f94:	cmp	x0, x1
    2f98:	b.ne	2f20 <peak_smmla_a28+0xa0>  // b.any
    2f9c:	add	v0.4s, v2.4s, v13.4s
    2fa0:	add	v0.4s, v0.4s, v12.4s
    2fa4:	ldp	d12, d13, [sp, #32]
    2fa8:	add	v0.4s, v0.4s, v11.4s
    2fac:	add	v0.4s, v0.4s, v10.4s
    2fb0:	ldp	d10, d11, [sp, #16]
    2fb4:	add	v0.4s, v0.4s, v9.4s
    2fb8:	add	v0.4s, v0.4s, v8.4s
    2fbc:	ldp	d8, d9, [sp], #48
    2fc0:	add	v0.4s, v0.4s, v31.4s
    2fc4:	add	v0.4s, v0.4s, v30.4s
    2fc8:	add	v0.4s, v0.4s, v29.4s
    2fcc:	add	v0.4s, v0.4s, v28.4s
    2fd0:	add	v0.4s, v0.4s, v27.4s
    2fd4:	add	v0.4s, v0.4s, v26.4s
    2fd8:	add	v0.4s, v0.4s, v25.4s
    2fdc:	add	v0.4s, v0.4s, v24.4s
    2fe0:	add	v0.4s, v0.4s, v23.4s
    2fe4:	add	v0.4s, v0.4s, v22.4s
    2fe8:	add	v0.4s, v0.4s, v21.4s
    2fec:	add	v0.4s, v0.4s, v20.4s
    2ff0:	add	v0.4s, v0.4s, v19.4s
    2ff4:	add	v0.4s, v0.4s, v18.4s
    2ff8:	add	v0.4s, v0.4s, v17.4s
    2ffc:	add	v0.4s, v0.4s, v16.4s
    3000:	add	v0.4s, v0.4s, v7.4s
    3004:	add	v0.4s, v0.4s, v6.4s
    3008:	add	v0.4s, v0.4s, v5.4s
    300c:	add	v0.4s, v0.4s, v4.4s
    3010:	add	v0.4s, v0.4s, v3.4s
    3014:	addv	s0, v0.4s
    3018:	fmov	w0, s0
    301c:	ret
    3020:	mov	x0, #0x658                 	// #1624
    3024:	ret

Disassembly of section .fini:
