# ===== peak_fma32_a8: hot loop = the 11 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003740 <peak_fma32_a8>:
    3740:	adrp	x1, 20000 <__data_start>
    3744:	add	x1, x1, #0x10
    3748:	ldr	s0, [x1, #16]
    374c:	ldr	s1, [x1, #20]
    3750:	dup	v0.4s, v0.s[0]
    3754:	dup	v1.4s, v1.s[0]
    3758:	cbz	x0, 37e0 <peak_fma32_a8+0xa0>
    375c:	movi	v3.4s, #0x0
    3760:	mov	x1, #0x0                   	// #0
    3764:	mov	v4.16b, v3.16b
    3768:	mov	v5.16b, v3.16b
    376c:	mov	v6.16b, v3.16b
    3770:	mov	v7.16b, v3.16b
    3774:	mov	v16.16b, v3.16b
    3778:	mov	v17.16b, v3.16b
    377c:	mov	v2.16b, v3.16b
    3780:	add	x1, x1, #0x1
    3784:	fmla	v2.4s, v0.4s, v1.4s
    3788:	fmla	v17.4s, v0.4s, v1.4s
    378c:	fmla	v16.4s, v0.4s, v1.4s
    3790:	fmla	v7.4s, v0.4s, v1.4s
    3794:	fmla	v6.4s, v0.4s, v1.4s
    3798:	fmla	v5.4s, v0.4s, v1.4s
    379c:	fmla	v4.4s, v0.4s, v1.4s
    37a0:	fmla	v3.4s, v0.4s, v1.4s
    37a4:	cmp	x0, x1
    37a8:	b.ne	3780 <peak_fma32_a8+0x40>  // b.any
    37ac:	movi	v0.4s, #0x0
    37b0:	fadd	v0.4s, v2.4s, v0.4s
    37b4:	fadd	v0.4s, v0.4s, v17.4s
    37b8:	fadd	v0.4s, v0.4s, v16.4s
    37bc:	fadd	v0.4s, v0.4s, v7.4s
    37c0:	fadd	v0.4s, v0.4s, v6.4s
    37c4:	fadd	v0.4s, v0.4s, v5.4s
    37c8:	fadd	v0.4s, v0.4s, v4.4s
    37cc:	fadd	v0.4s, v0.4s, v3.4s
    37d0:	faddp	v0.4s, v0.4s, v0.4s
    37d4:	faddp	v0.4s, v0.4s, v0.4s
    37d8:	fmov	w0, s0
    37dc:	ret
    37e0:	mov	x0, #0x0                   	// #0
    37e4:	ret

Disassembly of section .fini:

# ===== peak_fma32_a16: hot loop = the 19 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000037e8 <peak_fma32_a16>:
    37e8:	adrp	x1, 20000 <__data_start>
    37ec:	add	x1, x1, #0x10
    37f0:	ldr	s0, [x1, #16]
    37f4:	ldr	s1, [x1, #20]
    37f8:	dup	v0.4s, v0.s[0]
    37fc:	dup	v1.4s, v1.s[0]
    3800:	cbz	x0, 38e8 <peak_fma32_a16+0x100>
    3804:	movi	v3.4s, #0x0
    3808:	mov	x1, #0x0                   	// #0
    380c:	mov	v4.16b, v3.16b
    3810:	mov	v5.16b, v3.16b
    3814:	mov	v6.16b, v3.16b
    3818:	mov	v7.16b, v3.16b
    381c:	mov	v16.16b, v3.16b
    3820:	mov	v17.16b, v3.16b
    3824:	mov	v18.16b, v3.16b
    3828:	mov	v19.16b, v3.16b
    382c:	mov	v20.16b, v3.16b
    3830:	mov	v21.16b, v3.16b
    3834:	mov	v22.16b, v3.16b
    3838:	mov	v23.16b, v3.16b
    383c:	mov	v24.16b, v3.16b
    3840:	mov	v25.16b, v3.16b
    3844:	mov	v2.16b, v3.16b
    3848:	add	x1, x1, #0x1
    384c:	fmla	v2.4s, v0.4s, v1.4s
    3850:	fmla	v25.4s, v0.4s, v1.4s
    3854:	fmla	v24.4s, v0.4s, v1.4s
    3858:	fmla	v23.4s, v0.4s, v1.4s
    385c:	fmla	v22.4s, v0.4s, v1.4s
    3860:	fmla	v21.4s, v0.4s, v1.4s
    3864:	fmla	v20.4s, v0.4s, v1.4s
    3868:	fmla	v19.4s, v0.4s, v1.4s
    386c:	fmla	v18.4s, v0.4s, v1.4s
    3870:	fmla	v17.4s, v0.4s, v1.4s
    3874:	fmla	v16.4s, v0.4s, v1.4s
    3878:	fmla	v7.4s, v0.4s, v1.4s
    387c:	fmla	v6.4s, v0.4s, v1.4s
    3880:	fmla	v5.4s, v0.4s, v1.4s
    3884:	fmla	v4.4s, v0.4s, v1.4s
    3888:	fmla	v3.4s, v0.4s, v1.4s
    388c:	cmp	x0, x1
    3890:	b.ne	3848 <peak_fma32_a16+0x60>  // b.any
    3894:	movi	v0.4s, #0x0
    3898:	fadd	v0.4s, v2.4s, v0.4s
    389c:	fadd	v0.4s, v0.4s, v25.4s
    38a0:	fadd	v0.4s, v0.4s, v24.4s
    38a4:	fadd	v0.4s, v0.4s, v23.4s
    38a8:	fadd	v0.4s, v0.4s, v22.4s
    38ac:	fadd	v0.4s, v0.4s, v21.4s
    38b0:	fadd	v0.4s, v0.4s, v20.4s
    38b4:	fadd	v0.4s, v0.4s, v19.4s
    38b8:	fadd	v0.4s, v0.4s, v18.4s
    38bc:	fadd	v0.4s, v0.4s, v17.4s
    38c0:	fadd	v0.4s, v0.4s, v16.4s
    38c4:	fadd	v0.4s, v0.4s, v7.4s
    38c8:	fadd	v0.4s, v0.4s, v6.4s
    38cc:	fadd	v0.4s, v0.4s, v5.4s
    38d0:	fadd	v0.4s, v0.4s, v4.4s
    38d4:	fadd	v0.4s, v0.4s, v3.4s
    38d8:	faddp	v0.4s, v0.4s, v0.4s
    38dc:	faddp	v0.4s, v0.4s, v0.4s
    38e0:	fmov	w0, s0
    38e4:	ret
    38e8:	mov	x0, #0x0                   	// #0
    38ec:	ret

Disassembly of section .fini:

# ===== peak_fma32_a28: hot loop = the 31 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000038f0 <peak_fma32_a28>:
    38f0:	adrp	x1, 20000 <__data_start>
    38f4:	add	x1, x1, #0x10
    38f8:	ldr	s0, [x1, #16]
    38fc:	ldr	s1, [x1, #20]
    3900:	cbz	x0, 3a98 <peak_fma32_a28+0x1a8>
    3904:	movi	v3.4s, #0x0
    3908:	stp	d8, d9, [sp, #-48]!
    390c:	dup	v0.4s, v0.s[0]
    3910:	mov	x1, #0x0                   	// #0
    3914:	dup	v1.4s, v1.s[0]
    3918:	stp	d10, d11, [sp, #16]
    391c:	stp	d12, d13, [sp, #32]
    3920:	mov	v4.16b, v3.16b
    3924:	mov	v5.16b, v3.16b
    3928:	mov	v6.16b, v3.16b
    392c:	mov	v7.16b, v3.16b
    3930:	mov	v16.16b, v3.16b
    3934:	mov	v17.16b, v3.16b
    3938:	mov	v18.16b, v3.16b
    393c:	mov	v19.16b, v3.16b
    3940:	mov	v20.16b, v3.16b
    3944:	mov	v21.16b, v3.16b
    3948:	mov	v22.16b, v3.16b
    394c:	mov	v23.16b, v3.16b
    3950:	mov	v24.16b, v3.16b
    3954:	mov	v25.16b, v3.16b
    3958:	mov	v26.16b, v3.16b
    395c:	mov	v27.16b, v3.16b
    3960:	mov	v28.16b, v3.16b
    3964:	mov	v29.16b, v3.16b
    3968:	mov	v30.16b, v3.16b
    396c:	mov	v31.16b, v3.16b
    3970:	mov	v8.16b, v3.16b
    3974:	mov	v9.16b, v3.16b
    3978:	mov	v10.16b, v3.16b
    397c:	mov	v11.16b, v3.16b
    3980:	mov	v12.16b, v3.16b
    3984:	mov	v13.16b, v3.16b
    3988:	mov	v2.16b, v3.16b
    398c:	add	x1, x1, #0x1
    3990:	fmla	v2.4s, v0.4s, v1.4s
    3994:	fmla	v13.4s, v0.4s, v1.4s
    3998:	fmla	v12.4s, v0.4s, v1.4s
    399c:	fmla	v11.4s, v0.4s, v1.4s
    39a0:	fmla	v10.4s, v0.4s, v1.4s
    39a4:	fmla	v9.4s, v0.4s, v1.4s
    39a8:	fmla	v8.4s, v0.4s, v1.4s
    39ac:	fmla	v31.4s, v0.4s, v1.4s
    39b0:	fmla	v30.4s, v0.4s, v1.4s
    39b4:	fmla	v29.4s, v0.4s, v1.4s
    39b8:	fmla	v28.4s, v0.4s, v1.4s
    39bc:	fmla	v27.4s, v0.4s, v1.4s
    39c0:	fmla	v26.4s, v0.4s, v1.4s
    39c4:	fmla	v25.4s, v0.4s, v1.4s
    39c8:	fmla	v24.4s, v0.4s, v1.4s
    39cc:	fmla	v23.4s, v0.4s, v1.4s
    39d0:	fmla	v22.4s, v0.4s, v1.4s
    39d4:	fmla	v21.4s, v0.4s, v1.4s
    39d8:	fmla	v20.4s, v0.4s, v1.4s
    39dc:	fmla	v19.4s, v0.4s, v1.4s
    39e0:	fmla	v18.4s, v0.4s, v1.4s
    39e4:	fmla	v17.4s, v0.4s, v1.4s
    39e8:	fmla	v16.4s, v0.4s, v1.4s
    39ec:	fmla	v7.4s, v0.4s, v1.4s
    39f0:	fmla	v6.4s, v0.4s, v1.4s
    39f4:	fmla	v5.4s, v0.4s, v1.4s
    39f8:	fmla	v4.4s, v0.4s, v1.4s
    39fc:	fmla	v3.4s, v0.4s, v1.4s
    3a00:	cmp	x0, x1
    3a04:	b.ne	398c <peak_fma32_a28+0x9c>  // b.any
    3a08:	movi	v0.4s, #0x0
    3a0c:	fadd	v0.4s, v2.4s, v0.4s
    3a10:	fadd	v0.4s, v0.4s, v13.4s
    3a14:	fadd	v0.4s, v0.4s, v12.4s
    3a18:	ldp	d12, d13, [sp, #32]
    3a1c:	fadd	v0.4s, v0.4s, v11.4s
    3a20:	fadd	v0.4s, v0.4s, v10.4s
    3a24:	ldp	d10, d11, [sp, #16]
    3a28:	fadd	v0.4s, v0.4s, v9.4s
    3a2c:	fadd	v0.4s, v0.4s, v8.4s
    3a30:	ldp	d8, d9, [sp], #48
    3a34:	fadd	v0.4s, v0.4s, v31.4s
    3a38:	fadd	v0.4s, v0.4s, v30.4s
    3a3c:	fadd	v0.4s, v0.4s, v29.4s
    3a40:	fadd	v0.4s, v0.4s, v28.4s
    3a44:	fadd	v0.4s, v0.4s, v27.4s
    3a48:	fadd	v0.4s, v0.4s, v26.4s
    3a4c:	fadd	v0.4s, v0.4s, v25.4s
    3a50:	fadd	v0.4s, v0.4s, v24.4s
    3a54:	fadd	v0.4s, v0.4s, v23.4s
    3a58:	fadd	v0.4s, v0.4s, v22.4s
    3a5c:	fadd	v0.4s, v0.4s, v21.4s
    3a60:	fadd	v0.4s, v0.4s, v20.4s
    3a64:	fadd	v0.4s, v0.4s, v19.4s
    3a68:	fadd	v0.4s, v0.4s, v18.4s
    3a6c:	fadd	v0.4s, v0.4s, v17.4s
    3a70:	fadd	v0.4s, v0.4s, v16.4s
    3a74:	fadd	v0.4s, v0.4s, v7.4s
    3a78:	fadd	v0.4s, v0.4s, v6.4s
    3a7c:	fadd	v0.4s, v0.4s, v5.4s
    3a80:	fadd	v0.4s, v0.4s, v4.4s
    3a84:	fadd	v0.4s, v0.4s, v3.4s
    3a88:	faddp	v0.4s, v0.4s, v0.4s
    3a8c:	faddp	v0.4s, v0.4s, v0.4s
    3a90:	fmov	w0, s0
    3a94:	ret
    3a98:	mov	x0, #0x0                   	// #0
    3a9c:	ret

Disassembly of section .fini:
