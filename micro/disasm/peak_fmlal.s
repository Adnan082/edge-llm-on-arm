# ===== peak_fmlal_a8: hot loop = the 11 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003aa0 <peak_fmlal_a8>:
    3aa0:	adrp	x1, 20000 <__data_start>
    3aa4:	add	x1, x1, #0x10
    3aa8:	ldr	s0, [x1, #16]
    3aac:	ldr	s1, [x1, #20]
    3ab0:	fcvt	h0, s0
    3ab4:	mov	z0.h, h0
    3ab8:	fcvt	h1, s1
    3abc:	mov	z1.h, h1
    3ac0:	cbz	x0, 3b48 <peak_fmlal_a8+0xa8>
    3ac4:	mov	x1, #0x0                   	// #0
    3ac8:	mov	z2.s, #0
    3acc:	mov	z3.d, z2.d
    3ad0:	mov	z4.d, z2.d
    3ad4:	mov	z5.d, z2.d
    3ad8:	mov	z6.d, z2.d
    3adc:	mov	z7.d, z2.d
    3ae0:	mov	z16.d, z2.d
    3ae4:	mov	z17.d, z2.d
    3ae8:	fmlalb	z17.s, z0.h, z1.h
    3aec:	fmlalt	z16.s, z0.h, z1.h
    3af0:	fmlalb	z7.s, z0.h, z1.h
    3af4:	fmlalt	z6.s, z0.h, z1.h
    3af8:	fmlalb	z5.s, z0.h, z1.h
    3afc:	fmlalt	z4.s, z0.h, z1.h
    3b00:	fmlalb	z3.s, z0.h, z1.h
    3b04:	fmlalt	z2.s, z0.h, z1.h
    3b08:	add	x1, x1, #0x1
    3b0c:	cmp	x0, x1
    3b10:	b.ne	3ae8 <peak_fmlal_a8+0x48>  // b.any
    3b14:	ptrue	p0.b
    3b18:	mov	z0.s, #0
    3b1c:	fadd	z0.s, z0.s, z17.s
    3b20:	fadd	z0.s, z0.s, z16.s
    3b24:	fadd	z0.s, z0.s, z7.s
    3b28:	fadd	z0.s, z0.s, z6.s
    3b2c:	fadd	z0.s, z0.s, z5.s
    3b30:	fadd	z0.s, z0.s, z4.s
    3b34:	fadd	z0.s, z0.s, z3.s
    3b38:	fadd	z0.s, z0.s, z2.s
    3b3c:	faddv	s0, p0, z0.s
    3b40:	fmov	w0, s0
    3b44:	ret
    3b48:	mov	z2.s, #0
    3b4c:	mov	z3.d, z2.d
    3b50:	mov	z4.d, z2.d
    3b54:	mov	z5.d, z2.d
    3b58:	mov	z6.d, z2.d
    3b5c:	mov	z7.d, z2.d
    3b60:	mov	z16.d, z2.d
    3b64:	mov	z17.d, z2.d
    3b68:	b	3b14 <peak_fmlal_a8+0x74>

Disassembly of section .fini:

# ===== peak_fmlal_a16: hot loop = the 19 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003b6c <peak_fmlal_a16>:
    3b6c:	adrp	x1, 20000 <__data_start>
    3b70:	add	x1, x1, #0x10
    3b74:	ldr	s0, [x1, #16]
    3b78:	ldr	s1, [x1, #20]
    3b7c:	fcvt	h0, s0
    3b80:	mov	z0.h, h0
    3b84:	fcvt	h1, s1
    3b88:	mov	z1.h, h1
    3b8c:	cbz	x0, 3c80 <peak_fmlal_a16+0x114>
    3b90:	mov	x1, #0x0                   	// #0
    3b94:	mov	z2.s, #0
    3b98:	mov	z3.d, z2.d
    3b9c:	mov	z4.d, z2.d
    3ba0:	mov	z5.d, z2.d
    3ba4:	mov	z6.d, z2.d
    3ba8:	mov	z7.d, z2.d
    3bac:	mov	z16.d, z2.d
    3bb0:	mov	z17.d, z2.d
    3bb4:	mov	z18.d, z2.d
    3bb8:	mov	z19.d, z2.d
    3bbc:	mov	z20.d, z2.d
    3bc0:	mov	z21.d, z2.d
    3bc4:	mov	z22.d, z2.d
    3bc8:	mov	z23.d, z2.d
    3bcc:	mov	z24.d, z2.d
    3bd0:	mov	z25.d, z2.d
    3bd4:	nop
    3bd8:	nop
    3bdc:	nop
    3be0:	fmlalb	z25.s, z0.h, z1.h
    3be4:	fmlalt	z24.s, z0.h, z1.h
    3be8:	fmlalb	z23.s, z0.h, z1.h
    3bec:	fmlalt	z22.s, z0.h, z1.h
    3bf0:	fmlalb	z21.s, z0.h, z1.h
    3bf4:	fmlalt	z20.s, z0.h, z1.h
    3bf8:	fmlalb	z19.s, z0.h, z1.h
    3bfc:	fmlalt	z18.s, z0.h, z1.h
    3c00:	fmlalb	z17.s, z0.h, z1.h
    3c04:	fmlalt	z16.s, z0.h, z1.h
    3c08:	fmlalb	z7.s, z0.h, z1.h
    3c0c:	fmlalt	z6.s, z0.h, z1.h
    3c10:	fmlalb	z5.s, z0.h, z1.h
    3c14:	fmlalt	z4.s, z0.h, z1.h
    3c18:	fmlalb	z3.s, z0.h, z1.h
    3c1c:	fmlalt	z2.s, z0.h, z1.h
    3c20:	add	x1, x1, #0x1
    3c24:	cmp	x0, x1
    3c28:	b.ne	3be0 <peak_fmlal_a16+0x74>  // b.any
    3c2c:	ptrue	p0.b
    3c30:	mov	z0.s, #0
    3c34:	fadd	z0.s, z0.s, z25.s
    3c38:	fadd	z0.s, z0.s, z24.s
    3c3c:	fadd	z0.s, z0.s, z23.s
    3c40:	fadd	z0.s, z0.s, z22.s
    3c44:	fadd	z0.s, z0.s, z21.s
    3c48:	fadd	z0.s, z0.s, z20.s
    3c4c:	fadd	z0.s, z0.s, z19.s
    3c50:	fadd	z0.s, z0.s, z18.s
    3c54:	fadd	z0.s, z0.s, z17.s
    3c58:	fadd	z0.s, z0.s, z16.s
    3c5c:	fadd	z0.s, z0.s, z7.s
    3c60:	fadd	z0.s, z0.s, z6.s
    3c64:	fadd	z0.s, z0.s, z5.s
    3c68:	fadd	z0.s, z0.s, z4.s
    3c6c:	fadd	z0.s, z0.s, z3.s
    3c70:	fadd	z0.s, z0.s, z2.s
    3c74:	faddv	s0, p0, z0.s
    3c78:	fmov	w0, s0
    3c7c:	ret
    3c80:	mov	z2.s, #0
    3c84:	mov	z3.d, z2.d
    3c88:	mov	z4.d, z2.d
    3c8c:	mov	z5.d, z2.d
    3c90:	mov	z6.d, z2.d
    3c94:	mov	z7.d, z2.d
    3c98:	mov	z16.d, z2.d
    3c9c:	mov	z17.d, z2.d
    3ca0:	mov	z18.d, z2.d
    3ca4:	mov	z19.d, z2.d
    3ca8:	mov	z20.d, z2.d
    3cac:	mov	z21.d, z2.d
    3cb0:	mov	z22.d, z2.d
    3cb4:	mov	z23.d, z2.d
    3cb8:	mov	z24.d, z2.d
    3cbc:	mov	z25.d, z2.d
    3cc0:	b	3c2c <peak_fmlal_a16+0xc0>

Disassembly of section .fini:

# ===== peak_fmlal_a28: hot loop = the 31 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003cc4 <peak_fmlal_a28>:
    3cc4:	adrp	x1, 20000 <__data_start>
    3cc8:	stp	d8, d9, [sp, #-48]!
    3ccc:	add	x1, x1, #0x10
    3cd0:	stp	d10, d11, [sp, #16]
    3cd4:	stp	d12, d13, [sp, #32]
    3cd8:	ldr	s0, [x1, #16]
    3cdc:	ldr	s1, [x1, #20]
    3ce0:	fcvt	h0, s0
    3ce4:	mov	z0.h, h0
    3ce8:	fcvt	h1, s1
    3cec:	mov	z1.h, h1
    3cf0:	cbz	x0, 3e74 <peak_fmlal_a28+0x1b0>
    3cf4:	mov	x1, #0x0                   	// #0
    3cf8:	mov	z2.s, #0
    3cfc:	mov	z3.d, z2.d
    3d00:	mov	z4.d, z2.d
    3d04:	mov	z5.d, z2.d
    3d08:	mov	z6.d, z2.d
    3d0c:	mov	z7.d, z2.d
    3d10:	mov	z16.d, z2.d
    3d14:	mov	z17.d, z2.d
    3d18:	mov	z18.d, z2.d
    3d1c:	mov	z19.d, z2.d
    3d20:	mov	z20.d, z2.d
    3d24:	mov	z21.d, z2.d
    3d28:	mov	z22.d, z2.d
    3d2c:	mov	z23.d, z2.d
    3d30:	mov	z24.d, z2.d
    3d34:	mov	z25.d, z2.d
    3d38:	mov	z26.d, z2.d
    3d3c:	mov	z27.d, z2.d
    3d40:	mov	z28.d, z2.d
    3d44:	mov	z29.d, z2.d
    3d48:	mov	z30.d, z2.d
    3d4c:	mov	z31.d, z2.d
    3d50:	mov	z8.d, z2.d
    3d54:	mov	z9.d, z2.d
    3d58:	mov	z10.d, z2.d
    3d5c:	mov	z11.d, z2.d
    3d60:	mov	z12.d, z2.d
    3d64:	mov	z13.d, z2.d
    3d68:	fmlalb	z13.s, z0.h, z1.h
    3d6c:	fmlalt	z12.s, z0.h, z1.h
    3d70:	fmlalb	z11.s, z0.h, z1.h
    3d74:	fmlalt	z10.s, z0.h, z1.h
    3d78:	fmlalb	z9.s, z0.h, z1.h
    3d7c:	fmlalt	z8.s, z0.h, z1.h
    3d80:	fmlalb	z31.s, z0.h, z1.h
    3d84:	fmlalt	z30.s, z0.h, z1.h
    3d88:	fmlalb	z29.s, z0.h, z1.h
    3d8c:	fmlalt	z28.s, z0.h, z1.h
    3d90:	fmlalb	z27.s, z0.h, z1.h
    3d94:	fmlalt	z26.s, z0.h, z1.h
    3d98:	fmlalb	z25.s, z0.h, z1.h
    3d9c:	fmlalt	z24.s, z0.h, z1.h
    3da0:	fmlalb	z23.s, z0.h, z1.h
    3da4:	fmlalt	z22.s, z0.h, z1.h
    3da8:	fmlalb	z21.s, z0.h, z1.h
    3dac:	fmlalt	z20.s, z0.h, z1.h
    3db0:	fmlalb	z19.s, z0.h, z1.h
    3db4:	fmlalt	z18.s, z0.h, z1.h
    3db8:	fmlalb	z17.s, z0.h, z1.h
    3dbc:	fmlalt	z16.s, z0.h, z1.h
    3dc0:	fmlalb	z7.s, z0.h, z1.h
    3dc4:	fmlalt	z6.s, z0.h, z1.h
    3dc8:	fmlalb	z5.s, z0.h, z1.h
    3dcc:	fmlalt	z4.s, z0.h, z1.h
    3dd0:	fmlalb	z3.s, z0.h, z1.h
    3dd4:	fmlalt	z2.s, z0.h, z1.h
    3dd8:	add	x1, x1, #0x1
    3ddc:	cmp	x0, x1
    3de0:	b.ne	3d68 <peak_fmlal_a28+0xa4>  // b.any
    3de4:	ptrue	p0.b
    3de8:	mov	z0.s, #0
    3dec:	fadd	z0.s, z0.s, z13.s
    3df0:	fadd	z0.s, z0.s, z12.s
    3df4:	ldp	d12, d13, [sp, #32]
    3df8:	fadd	z0.s, z0.s, z11.s
    3dfc:	fadd	z0.s, z0.s, z10.s
    3e00:	fadd	z0.s, z0.s, z9.s
    3e04:	fadd	z0.s, z0.s, z8.s
    3e08:	fadd	z0.s, z0.s, z31.s
    3e0c:	ldp	d10, d11, [sp, #16]
    3e10:	fadd	z0.s, z0.s, z30.s
    3e14:	fadd	z0.s, z0.s, z29.s
    3e18:	fadd	z0.s, z0.s, z28.s
    3e1c:	fadd	z0.s, z0.s, z27.s
    3e20:	fadd	z0.s, z0.s, z26.s
    3e24:	fadd	z0.s, z0.s, z25.s
    3e28:	fadd	z0.s, z0.s, z24.s
    3e2c:	fadd	z0.s, z0.s, z23.s
    3e30:	fadd	z0.s, z0.s, z22.s
    3e34:	ldp	d8, d9, [sp], #48
    3e38:	fadd	z0.s, z0.s, z21.s
    3e3c:	fadd	z0.s, z0.s, z20.s
    3e40:	fadd	z0.s, z0.s, z19.s
    3e44:	fadd	z0.s, z0.s, z18.s
    3e48:	fadd	z0.s, z0.s, z17.s
    3e4c:	fadd	z0.s, z0.s, z16.s
    3e50:	fadd	z0.s, z0.s, z7.s
    3e54:	fadd	z0.s, z0.s, z6.s
    3e58:	fadd	z0.s, z0.s, z5.s
    3e5c:	fadd	z0.s, z0.s, z4.s
    3e60:	fadd	z0.s, z0.s, z3.s
    3e64:	fadd	z0.s, z0.s, z2.s
    3e68:	faddv	s0, p0, z0.s
    3e6c:	fmov	w0, s0
    3e70:	ret
    3e74:	mov	z2.s, #0
    3e78:	mov	z3.d, z2.d
    3e7c:	mov	z4.d, z2.d
    3e80:	mov	z5.d, z2.d
    3e84:	mov	z6.d, z2.d
    3e88:	mov	z7.d, z2.d
    3e8c:	mov	z16.d, z2.d
    3e90:	mov	z17.d, z2.d
    3e94:	mov	z18.d, z2.d
    3e98:	mov	z19.d, z2.d
    3e9c:	mov	z20.d, z2.d
    3ea0:	mov	z21.d, z2.d
    3ea4:	mov	z22.d, z2.d
    3ea8:	mov	z23.d, z2.d
    3eac:	mov	z24.d, z2.d
    3eb0:	mov	z25.d, z2.d
    3eb4:	mov	z26.d, z2.d
    3eb8:	mov	z27.d, z2.d
    3ebc:	mov	z28.d, z2.d
    3ec0:	mov	z29.d, z2.d
    3ec4:	mov	z30.d, z2.d
    3ec8:	mov	z31.d, z2.d
    3ecc:	mov	z8.d, z2.d
    3ed0:	mov	z9.d, z2.d
    3ed4:	mov	z10.d, z2.d
    3ed8:	mov	z11.d, z2.d
    3edc:	mov	z12.d, z2.d
    3ee0:	mov	z13.d, z2.d
    3ee4:	b	3de4 <peak_fmlal_a28+0x120>

Disassembly of section .fini:
