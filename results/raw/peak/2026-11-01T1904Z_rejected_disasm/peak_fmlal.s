# ===== peak_fmlal_a8: hot loop = the 22 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003b40 <peak_fmlal_a8>:
    3b40:	adrp	x1, 20000 <__data_start>
    3b44:	add	x1, x1, #0x10
    3b48:	ldr	s0, [x1, #16]
    3b4c:	ldr	s1, [x1, #20]
    3b50:	fcvt	h0, s0
    3b54:	mov	z0.h, h0
    3b58:	fcvt	h1, s1
    3b5c:	mov	z1.h, h1
    3b60:	cbz	x0, 3be8 <peak_fmlal_a8+0xa8>
    3b64:	mov	x1, #0x0                   	// #0
    3b68:	mov	z2.s, #0
    3b6c:	mov	z3.d, z2.d
    3b70:	mov	z4.d, z2.d
    3b74:	mov	z5.d, z2.d
    3b78:	mov	z6.d, z2.d
    3b7c:	mov	z7.d, z2.d
    3b80:	mov	z16.d, z2.d
    3b84:	mov	z17.d, z2.d
    3b88:	add	x1, x1, #0x1
    3b8c:	fmlalb	z17.s, z0.h, z1.h
    3b90:	fmlalt	z16.s, z0.h, z1.h
    3b94:	fmlalb	z7.s, z0.h, z1.h
    3b98:	fmlalt	z6.s, z0.h, z1.h
    3b9c:	fmlalb	z5.s, z0.h, z1.h
    3ba0:	fmlalt	z4.s, z0.h, z1.h
    3ba4:	fmlalb	z3.s, z0.h, z1.h
    3ba8:	fmlalt	z2.s, z0.h, z1.h
    3bac:	cmp	x0, x1
    3bb0:	b.ne	3b88 <peak_fmlal_a8+0x48>  // b.any
    3bb4:	ptrue	p0.b
    3bb8:	mov	z0.s, #0
    3bbc:	fadd	z0.s, z0.s, z17.s
    3bc0:	fadd	z0.s, z0.s, z16.s
    3bc4:	fadd	z0.s, z0.s, z7.s
    3bc8:	fadd	z0.s, z0.s, z6.s
    3bcc:	fadd	z0.s, z0.s, z5.s
    3bd0:	fadd	z0.s, z0.s, z4.s
    3bd4:	fadd	z0.s, z0.s, z3.s
    3bd8:	fadd	z0.s, z0.s, z2.s
    3bdc:	faddv	s0, p0, z0.s
    3be0:	fmov	w0, s0
    3be4:	ret
    3be8:	mov	z2.s, #0
    3bec:	mov	z3.d, z2.d
    3bf0:	mov	z4.d, z2.d
    3bf4:	mov	z5.d, z2.d
    3bf8:	mov	z6.d, z2.d
    3bfc:	mov	z7.d, z2.d
    3c00:	mov	z16.d, z2.d
    3c04:	mov	z17.d, z2.d
    3c08:	b	3bb4 <peak_fmlal_a8+0x74>

Disassembly of section .fini:

# ===== peak_fmlal_a16: hot loop = the 38 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003c0c <peak_fmlal_a16>:
    3c0c:	adrp	x1, 20000 <__data_start>
    3c10:	add	x1, x1, #0x10
    3c14:	ldr	s0, [x1, #16]
    3c18:	ldr	s1, [x1, #20]
    3c1c:	fcvt	h0, s0
    3c20:	mov	z0.h, h0
    3c24:	fcvt	h1, s1
    3c28:	mov	z1.h, h1
    3c2c:	cbz	x0, 3d20 <peak_fmlal_a16+0x114>
    3c30:	mov	x1, #0x0                   	// #0
    3c34:	mov	z2.s, #0
    3c38:	mov	z3.d, z2.d
    3c3c:	mov	z4.d, z2.d
    3c40:	mov	z5.d, z2.d
    3c44:	mov	z6.d, z2.d
    3c48:	mov	z7.d, z2.d
    3c4c:	mov	z16.d, z2.d
    3c50:	mov	z17.d, z2.d
    3c54:	mov	z18.d, z2.d
    3c58:	mov	z19.d, z2.d
    3c5c:	mov	z20.d, z2.d
    3c60:	mov	z21.d, z2.d
    3c64:	mov	z22.d, z2.d
    3c68:	mov	z23.d, z2.d
    3c6c:	mov	z24.d, z2.d
    3c70:	mov	z25.d, z2.d
    3c74:	nop
    3c78:	nop
    3c7c:	nop
    3c80:	add	x1, x1, #0x1
    3c84:	fmlalb	z25.s, z0.h, z1.h
    3c88:	fmlalt	z24.s, z0.h, z1.h
    3c8c:	fmlalb	z23.s, z0.h, z1.h
    3c90:	fmlalt	z22.s, z0.h, z1.h
    3c94:	fmlalb	z21.s, z0.h, z1.h
    3c98:	fmlalt	z20.s, z0.h, z1.h
    3c9c:	fmlalb	z19.s, z0.h, z1.h
    3ca0:	fmlalt	z18.s, z0.h, z1.h
    3ca4:	fmlalb	z17.s, z0.h, z1.h
    3ca8:	fmlalt	z16.s, z0.h, z1.h
    3cac:	fmlalb	z7.s, z0.h, z1.h
    3cb0:	fmlalt	z6.s, z0.h, z1.h
    3cb4:	fmlalb	z5.s, z0.h, z1.h
    3cb8:	fmlalt	z4.s, z0.h, z1.h
    3cbc:	fmlalb	z3.s, z0.h, z1.h
    3cc0:	fmlalt	z2.s, z0.h, z1.h
    3cc4:	cmp	x0, x1
    3cc8:	b.ne	3c80 <peak_fmlal_a16+0x74>  // b.any
    3ccc:	ptrue	p0.b
    3cd0:	mov	z0.s, #0
    3cd4:	fadd	z0.s, z0.s, z25.s
    3cd8:	fadd	z0.s, z0.s, z24.s
    3cdc:	fadd	z0.s, z0.s, z23.s
    3ce0:	fadd	z0.s, z0.s, z22.s
    3ce4:	fadd	z0.s, z0.s, z21.s
    3ce8:	fadd	z0.s, z0.s, z20.s
    3cec:	fadd	z0.s, z0.s, z19.s
    3cf0:	fadd	z0.s, z0.s, z18.s
    3cf4:	fadd	z0.s, z0.s, z17.s
    3cf8:	fadd	z0.s, z0.s, z16.s
    3cfc:	fadd	z0.s, z0.s, z7.s
    3d00:	fadd	z0.s, z0.s, z6.s
    3d04:	fadd	z0.s, z0.s, z5.s
    3d08:	fadd	z0.s, z0.s, z4.s
    3d0c:	fadd	z0.s, z0.s, z3.s
    3d10:	fadd	z0.s, z0.s, z2.s
    3d14:	faddv	s0, p0, z0.s
    3d18:	fmov	w0, s0
    3d1c:	ret
    3d20:	mov	z2.s, #0
    3d24:	mov	z3.d, z2.d
    3d28:	mov	z4.d, z2.d
    3d2c:	mov	z5.d, z2.d
    3d30:	mov	z6.d, z2.d
    3d34:	mov	z7.d, z2.d
    3d38:	mov	z16.d, z2.d
    3d3c:	mov	z17.d, z2.d
    3d40:	mov	z18.d, z2.d
    3d44:	mov	z19.d, z2.d
    3d48:	mov	z20.d, z2.d
    3d4c:	mov	z21.d, z2.d
    3d50:	mov	z22.d, z2.d
    3d54:	mov	z23.d, z2.d
    3d58:	mov	z24.d, z2.d
    3d5c:	mov	z25.d, z2.d
    3d60:	b	3ccc <peak_fmlal_a16+0xc0>

Disassembly of section .fini:

# ===== peak_fmlal_a28: hot loop = the 65 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003d64 <peak_fmlal_a28>:
    3d64:	adrp	x1, 20000 <__data_start>
    3d68:	stp	d8, d9, [sp, #-48]!
    3d6c:	add	x1, x1, #0x10
    3d70:	stp	d10, d11, [sp, #16]
    3d74:	stp	d12, d13, [sp, #32]
    3d78:	ldr	s0, [x1, #16]
    3d7c:	ldr	s1, [x1, #20]
    3d80:	fcvt	h0, s0
    3d84:	mov	z0.h, h0
    3d88:	fcvt	h1, s1
    3d8c:	mov	z1.h, h1
    3d90:	cbz	x0, 3f14 <peak_fmlal_a28+0x1b0>
    3d94:	mov	x1, #0x0                   	// #0
    3d98:	mov	z2.s, #0
    3d9c:	mov	z3.d, z2.d
    3da0:	mov	z4.d, z2.d
    3da4:	mov	z5.d, z2.d
    3da8:	mov	z6.d, z2.d
    3dac:	mov	z7.d, z2.d
    3db0:	mov	z16.d, z2.d
    3db4:	mov	z17.d, z2.d
    3db8:	mov	z18.d, z2.d
    3dbc:	mov	z19.d, z2.d
    3dc0:	mov	z20.d, z2.d
    3dc4:	mov	z21.d, z2.d
    3dc8:	mov	z22.d, z2.d
    3dcc:	mov	z23.d, z2.d
    3dd0:	mov	z24.d, z2.d
    3dd4:	mov	z25.d, z2.d
    3dd8:	mov	z26.d, z2.d
    3ddc:	mov	z27.d, z2.d
    3de0:	mov	z28.d, z2.d
    3de4:	mov	z29.d, z2.d
    3de8:	mov	z30.d, z2.d
    3dec:	mov	z31.d, z2.d
    3df0:	mov	z8.d, z2.d
    3df4:	mov	z9.d, z2.d
    3df8:	mov	z10.d, z2.d
    3dfc:	mov	z11.d, z2.d
    3e00:	mov	z12.d, z2.d
    3e04:	mov	z13.d, z2.d
    3e08:	add	x1, x1, #0x1
    3e0c:	fmlalb	z13.s, z0.h, z1.h
    3e10:	fmlalt	z12.s, z0.h, z1.h
    3e14:	fmlalb	z11.s, z0.h, z1.h
    3e18:	fmlalt	z10.s, z0.h, z1.h
    3e1c:	fmlalb	z9.s, z0.h, z1.h
    3e20:	fmlalt	z8.s, z0.h, z1.h
    3e24:	fmlalb	z31.s, z0.h, z1.h
    3e28:	fmlalt	z30.s, z0.h, z1.h
    3e2c:	fmlalb	z29.s, z0.h, z1.h
    3e30:	fmlalt	z28.s, z0.h, z1.h
    3e34:	fmlalb	z27.s, z0.h, z1.h
    3e38:	fmlalt	z26.s, z0.h, z1.h
    3e3c:	fmlalb	z25.s, z0.h, z1.h
    3e40:	fmlalt	z24.s, z0.h, z1.h
    3e44:	fmlalb	z23.s, z0.h, z1.h
    3e48:	fmlalt	z22.s, z0.h, z1.h
    3e4c:	fmlalb	z21.s, z0.h, z1.h
    3e50:	fmlalt	z20.s, z0.h, z1.h
    3e54:	fmlalb	z19.s, z0.h, z1.h
    3e58:	fmlalt	z18.s, z0.h, z1.h
    3e5c:	fmlalb	z17.s, z0.h, z1.h
    3e60:	fmlalt	z16.s, z0.h, z1.h
    3e64:	fmlalb	z7.s, z0.h, z1.h
    3e68:	fmlalt	z6.s, z0.h, z1.h
    3e6c:	fmlalb	z5.s, z0.h, z1.h
    3e70:	fmlalt	z4.s, z0.h, z1.h
    3e74:	fmlalb	z3.s, z0.h, z1.h
    3e78:	fmlalt	z2.s, z0.h, z1.h
    3e7c:	cmp	x0, x1
    3e80:	b.ne	3e08 <peak_fmlal_a28+0xa4>  // b.any
    3e84:	ptrue	p0.b
    3e88:	mov	z0.s, #0
    3e8c:	fadd	z0.s, z0.s, z13.s
    3e90:	fadd	z0.s, z0.s, z12.s
    3e94:	ldp	d12, d13, [sp, #32]
    3e98:	fadd	z0.s, z0.s, z11.s
    3e9c:	fadd	z0.s, z0.s, z10.s
    3ea0:	fadd	z0.s, z0.s, z9.s
    3ea4:	fadd	z0.s, z0.s, z8.s
    3ea8:	fadd	z0.s, z0.s, z31.s
    3eac:	ldp	d10, d11, [sp, #16]
    3eb0:	fadd	z0.s, z0.s, z30.s
    3eb4:	fadd	z0.s, z0.s, z29.s
    3eb8:	fadd	z0.s, z0.s, z28.s
    3ebc:	fadd	z0.s, z0.s, z27.s
    3ec0:	fadd	z0.s, z0.s, z26.s
    3ec4:	fadd	z0.s, z0.s, z25.s
    3ec8:	fadd	z0.s, z0.s, z24.s
    3ecc:	fadd	z0.s, z0.s, z23.s
    3ed0:	fadd	z0.s, z0.s, z22.s
    3ed4:	ldp	d8, d9, [sp], #48
    3ed8:	fadd	z0.s, z0.s, z21.s
    3edc:	fadd	z0.s, z0.s, z20.s
    3ee0:	fadd	z0.s, z0.s, z19.s
    3ee4:	fadd	z0.s, z0.s, z18.s
    3ee8:	fadd	z0.s, z0.s, z17.s
    3eec:	fadd	z0.s, z0.s, z16.s
    3ef0:	fadd	z0.s, z0.s, z7.s
    3ef4:	fadd	z0.s, z0.s, z6.s
    3ef8:	fadd	z0.s, z0.s, z5.s
    3efc:	fadd	z0.s, z0.s, z4.s
    3f00:	fadd	z0.s, z0.s, z3.s
    3f04:	fadd	z0.s, z0.s, z2.s
    3f08:	faddv	s0, p0, z0.s
    3f0c:	fmov	w0, s0
    3f10:	ret
    3f14:	mov	z2.s, #0
    3f18:	mov	z3.d, z2.d
    3f1c:	mov	z4.d, z2.d
    3f20:	mov	z5.d, z2.d
    3f24:	mov	z6.d, z2.d
    3f28:	mov	z7.d, z2.d
    3f2c:	mov	z16.d, z2.d
    3f30:	mov	z17.d, z2.d
    3f34:	mov	z18.d, z2.d
    3f38:	mov	z19.d, z2.d
    3f3c:	mov	z20.d, z2.d
    3f40:	mov	z21.d, z2.d
    3f44:	mov	z22.d, z2.d
    3f48:	mov	z23.d, z2.d
    3f4c:	mov	z24.d, z2.d
    3f50:	mov	z25.d, z2.d
    3f54:	mov	z26.d, z2.d
    3f58:	mov	z27.d, z2.d
    3f5c:	mov	z28.d, z2.d
    3f60:	mov	z29.d, z2.d
    3f64:	mov	z30.d, z2.d
    3f68:	mov	z31.d, z2.d
    3f6c:	mov	z8.d, z2.d
    3f70:	mov	z9.d, z2.d
    3f74:	mov	z10.d, z2.d
    3f78:	mov	z11.d, z2.d
    3f7c:	mov	z12.d, z2.d
    3f80:	mov	z13.d, z2.d
    3f84:	b	3e84 <peak_fmlal_a28+0x120>

Disassembly of section .fini:
