# ===== peak_fma32_a8: hot loop = the 11 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000037d0 <peak_fma32_a8>:
    37d0:	adrp	x1, 20000 <__data_start>
    37d4:	add	x1, x1, #0x10
    37d8:	ldr	s0, [x1, #16]
    37dc:	ldr	s1, [x1, #20]
    37e0:	dup	v0.4s, v0.s[0]
    37e4:	dup	v1.4s, v1.s[0]
    37e8:	cbz	x0, 3870 <peak_fma32_a8+0xa0>
    37ec:	movi	v3.4s, #0x0
    37f0:	mov	x1, #0x0                   	// #0
    37f4:	mov	v4.16b, v3.16b
    37f8:	mov	v5.16b, v3.16b
    37fc:	mov	v6.16b, v3.16b
    3800:	mov	v7.16b, v3.16b
    3804:	mov	v16.16b, v3.16b
    3808:	mov	v17.16b, v3.16b
    380c:	mov	v2.16b, v3.16b
    3810:	add	x1, x1, #0x1
    3814:	fmla	v2.4s, v0.4s, v1.4s
    3818:	fmla	v17.4s, v0.4s, v1.4s
    381c:	fmla	v16.4s, v0.4s, v1.4s
    3820:	fmla	v7.4s, v0.4s, v1.4s
    3824:	fmla	v6.4s, v0.4s, v1.4s
    3828:	fmla	v5.4s, v0.4s, v1.4s
    382c:	fmla	v4.4s, v0.4s, v1.4s
    3830:	fmla	v3.4s, v0.4s, v1.4s
    3834:	cmp	x0, x1
    3838:	b.ne	3810 <peak_fma32_a8+0x40>  // b.any
    383c:	movi	v0.4s, #0x0
    3840:	fadd	v0.4s, v2.4s, v0.4s
    3844:	fadd	v0.4s, v0.4s, v17.4s
    3848:	fadd	v0.4s, v0.4s, v16.4s
    384c:	fadd	v0.4s, v0.4s, v7.4s
    3850:	fadd	v0.4s, v0.4s, v6.4s
    3854:	fadd	v0.4s, v0.4s, v5.4s
    3858:	fadd	v0.4s, v0.4s, v4.4s
    385c:	fadd	v0.4s, v0.4s, v3.4s
    3860:	faddp	v0.4s, v0.4s, v0.4s
    3864:	faddp	v0.4s, v0.4s, v0.4s
    3868:	fmov	w0, s0
    386c:	ret
    3870:	mov	x0, #0x0                   	// #0
    3874:	ret

Disassembly of section .fini:

# ===== peak_fma32_a16: hot loop = the 19 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003880 <peak_fma32_a16>:
    3880:	adrp	x1, 20000 <__data_start>
    3884:	add	x1, x1, #0x10
    3888:	ldr	s0, [x1, #16]
    388c:	ldr	s1, [x1, #20]
    3890:	dup	v0.4s, v0.s[0]
    3894:	dup	v1.4s, v1.s[0]
    3898:	cbz	x0, 3980 <peak_fma32_a16+0x100>
    389c:	movi	v3.4s, #0x0
    38a0:	mov	x1, #0x0                   	// #0
    38a4:	mov	v4.16b, v3.16b
    38a8:	mov	v5.16b, v3.16b
    38ac:	mov	v6.16b, v3.16b
    38b0:	mov	v7.16b, v3.16b
    38b4:	mov	v16.16b, v3.16b
    38b8:	mov	v17.16b, v3.16b
    38bc:	mov	v18.16b, v3.16b
    38c0:	mov	v19.16b, v3.16b
    38c4:	mov	v20.16b, v3.16b
    38c8:	mov	v21.16b, v3.16b
    38cc:	mov	v22.16b, v3.16b
    38d0:	mov	v23.16b, v3.16b
    38d4:	mov	v24.16b, v3.16b
    38d8:	mov	v25.16b, v3.16b
    38dc:	mov	v2.16b, v3.16b
    38e0:	add	x1, x1, #0x1
    38e4:	fmla	v2.4s, v0.4s, v1.4s
    38e8:	fmla	v25.4s, v0.4s, v1.4s
    38ec:	fmla	v24.4s, v0.4s, v1.4s
    38f0:	fmla	v23.4s, v0.4s, v1.4s
    38f4:	fmla	v22.4s, v0.4s, v1.4s
    38f8:	fmla	v21.4s, v0.4s, v1.4s
    38fc:	fmla	v20.4s, v0.4s, v1.4s
    3900:	fmla	v19.4s, v0.4s, v1.4s
    3904:	fmla	v18.4s, v0.4s, v1.4s
    3908:	fmla	v17.4s, v0.4s, v1.4s
    390c:	fmla	v16.4s, v0.4s, v1.4s
    3910:	fmla	v7.4s, v0.4s, v1.4s
    3914:	fmla	v6.4s, v0.4s, v1.4s
    3918:	fmla	v5.4s, v0.4s, v1.4s
    391c:	fmla	v4.4s, v0.4s, v1.4s
    3920:	fmla	v3.4s, v0.4s, v1.4s
    3924:	cmp	x0, x1
    3928:	b.ne	38e0 <peak_fma32_a16+0x60>  // b.any
    392c:	movi	v0.4s, #0x0
    3930:	fadd	v0.4s, v2.4s, v0.4s
    3934:	fadd	v0.4s, v0.4s, v25.4s
    3938:	fadd	v0.4s, v0.4s, v24.4s
    393c:	fadd	v0.4s, v0.4s, v23.4s
    3940:	fadd	v0.4s, v0.4s, v22.4s
    3944:	fadd	v0.4s, v0.4s, v21.4s
    3948:	fadd	v0.4s, v0.4s, v20.4s
    394c:	fadd	v0.4s, v0.4s, v19.4s
    3950:	fadd	v0.4s, v0.4s, v18.4s
    3954:	fadd	v0.4s, v0.4s, v17.4s
    3958:	fadd	v0.4s, v0.4s, v16.4s
    395c:	fadd	v0.4s, v0.4s, v7.4s
    3960:	fadd	v0.4s, v0.4s, v6.4s
    3964:	fadd	v0.4s, v0.4s, v5.4s
    3968:	fadd	v0.4s, v0.4s, v4.4s
    396c:	fadd	v0.4s, v0.4s, v3.4s
    3970:	faddp	v0.4s, v0.4s, v0.4s
    3974:	faddp	v0.4s, v0.4s, v0.4s
    3978:	fmov	w0, s0
    397c:	ret
    3980:	mov	x0, #0x0                   	// #0
    3984:	ret

Disassembly of section .fini:

# ===== peak_fma32_a28: hot loop = the 31 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003988 <peak_fma32_a28>:
    3988:	adrp	x1, 20000 <__data_start>
    398c:	add	x1, x1, #0x10
    3990:	ldr	s0, [x1, #16]
    3994:	ldr	s1, [x1, #20]
    3998:	cbz	x0, 3b30 <peak_fma32_a28+0x1a8>
    399c:	movi	v3.4s, #0x0
    39a0:	stp	d8, d9, [sp, #-48]!
    39a4:	dup	v0.4s, v0.s[0]
    39a8:	mov	x1, #0x0                   	// #0
    39ac:	dup	v1.4s, v1.s[0]
    39b0:	stp	d10, d11, [sp, #16]
    39b4:	stp	d12, d13, [sp, #32]
    39b8:	mov	v4.16b, v3.16b
    39bc:	mov	v5.16b, v3.16b
    39c0:	mov	v6.16b, v3.16b
    39c4:	mov	v7.16b, v3.16b
    39c8:	mov	v16.16b, v3.16b
    39cc:	mov	v17.16b, v3.16b
    39d0:	mov	v18.16b, v3.16b
    39d4:	mov	v19.16b, v3.16b
    39d8:	mov	v20.16b, v3.16b
    39dc:	mov	v21.16b, v3.16b
    39e0:	mov	v22.16b, v3.16b
    39e4:	mov	v23.16b, v3.16b
    39e8:	mov	v24.16b, v3.16b
    39ec:	mov	v25.16b, v3.16b
    39f0:	mov	v26.16b, v3.16b
    39f4:	mov	v27.16b, v3.16b
    39f8:	mov	v28.16b, v3.16b
    39fc:	mov	v29.16b, v3.16b
    3a00:	mov	v30.16b, v3.16b
    3a04:	mov	v31.16b, v3.16b
    3a08:	mov	v8.16b, v3.16b
    3a0c:	mov	v9.16b, v3.16b
    3a10:	mov	v10.16b, v3.16b
    3a14:	mov	v11.16b, v3.16b
    3a18:	mov	v12.16b, v3.16b
    3a1c:	mov	v13.16b, v3.16b
    3a20:	mov	v2.16b, v3.16b
    3a24:	add	x1, x1, #0x1
    3a28:	fmla	v2.4s, v0.4s, v1.4s
    3a2c:	fmla	v13.4s, v0.4s, v1.4s
    3a30:	fmla	v12.4s, v0.4s, v1.4s
    3a34:	fmla	v11.4s, v0.4s, v1.4s
    3a38:	fmla	v10.4s, v0.4s, v1.4s
    3a3c:	fmla	v9.4s, v0.4s, v1.4s
    3a40:	fmla	v8.4s, v0.4s, v1.4s
    3a44:	fmla	v31.4s, v0.4s, v1.4s
    3a48:	fmla	v30.4s, v0.4s, v1.4s
    3a4c:	fmla	v29.4s, v0.4s, v1.4s
    3a50:	fmla	v28.4s, v0.4s, v1.4s
    3a54:	fmla	v27.4s, v0.4s, v1.4s
    3a58:	fmla	v26.4s, v0.4s, v1.4s
    3a5c:	fmla	v25.4s, v0.4s, v1.4s
    3a60:	fmla	v24.4s, v0.4s, v1.4s
    3a64:	fmla	v23.4s, v0.4s, v1.4s
    3a68:	fmla	v22.4s, v0.4s, v1.4s
    3a6c:	fmla	v21.4s, v0.4s, v1.4s
    3a70:	fmla	v20.4s, v0.4s, v1.4s
    3a74:	fmla	v19.4s, v0.4s, v1.4s
    3a78:	fmla	v18.4s, v0.4s, v1.4s
    3a7c:	fmla	v17.4s, v0.4s, v1.4s
    3a80:	fmla	v16.4s, v0.4s, v1.4s
    3a84:	fmla	v7.4s, v0.4s, v1.4s
    3a88:	fmla	v6.4s, v0.4s, v1.4s
    3a8c:	fmla	v5.4s, v0.4s, v1.4s
    3a90:	fmla	v4.4s, v0.4s, v1.4s
    3a94:	fmla	v3.4s, v0.4s, v1.4s
    3a98:	cmp	x0, x1
    3a9c:	b.ne	3a24 <peak_fma32_a28+0x9c>  // b.any
    3aa0:	movi	v0.4s, #0x0
    3aa4:	fadd	v0.4s, v2.4s, v0.4s
    3aa8:	fadd	v0.4s, v0.4s, v13.4s
    3aac:	fadd	v0.4s, v0.4s, v12.4s
    3ab0:	ldp	d12, d13, [sp, #32]
    3ab4:	fadd	v0.4s, v0.4s, v11.4s
    3ab8:	fadd	v0.4s, v0.4s, v10.4s
    3abc:	ldp	d10, d11, [sp, #16]
    3ac0:	fadd	v0.4s, v0.4s, v9.4s
    3ac4:	fadd	v0.4s, v0.4s, v8.4s
    3ac8:	ldp	d8, d9, [sp], #48
    3acc:	fadd	v0.4s, v0.4s, v31.4s
    3ad0:	fadd	v0.4s, v0.4s, v30.4s
    3ad4:	fadd	v0.4s, v0.4s, v29.4s
    3ad8:	fadd	v0.4s, v0.4s, v28.4s
    3adc:	fadd	v0.4s, v0.4s, v27.4s
    3ae0:	fadd	v0.4s, v0.4s, v26.4s
    3ae4:	fadd	v0.4s, v0.4s, v25.4s
    3ae8:	fadd	v0.4s, v0.4s, v24.4s
    3aec:	fadd	v0.4s, v0.4s, v23.4s
    3af0:	fadd	v0.4s, v0.4s, v22.4s
    3af4:	fadd	v0.4s, v0.4s, v21.4s
    3af8:	fadd	v0.4s, v0.4s, v20.4s
    3afc:	fadd	v0.4s, v0.4s, v19.4s
    3b00:	fadd	v0.4s, v0.4s, v18.4s
    3b04:	fadd	v0.4s, v0.4s, v17.4s
    3b08:	fadd	v0.4s, v0.4s, v16.4s
    3b0c:	fadd	v0.4s, v0.4s, v7.4s
    3b10:	fadd	v0.4s, v0.4s, v6.4s
    3b14:	fadd	v0.4s, v0.4s, v5.4s
    3b18:	fadd	v0.4s, v0.4s, v4.4s
    3b1c:	fadd	v0.4s, v0.4s, v3.4s
    3b20:	faddp	v0.4s, v0.4s, v0.4s
    3b24:	faddp	v0.4s, v0.4s, v0.4s
    3b28:	fmov	w0, s0
    3b2c:	ret
    3b30:	mov	x0, #0x0                   	// #0
    3b34:	ret

Disassembly of section .fini:
