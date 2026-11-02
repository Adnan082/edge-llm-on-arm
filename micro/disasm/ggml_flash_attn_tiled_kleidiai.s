# ===== ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int) =====
   86660:	stp	x29, x30, [sp, #-160]!
   86664:	mov	x29, sp
   86668:	stp	x19, x20, [sp, #16]
   8666c:	stp	x21, x22, [sp, #32]
   86670:	stp	x23, x24, [sp, #48]
   86674:	stp	x25, x26, [sp, #64]
   86678:	stp	x27, x28, [sp, #80]
   8667c:	sub	sp, sp, #0x500
   86680:	str	xzr, [sp, #1024]
   86684:	adrp	x4, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   86688:	ldr	x4, [x4, #3280]
   8668c:	mov	x5, x1
   86690:	str	x0, [sp, #424]
   86694:	ldr	x0, [x1, #160]
   86698:	stp	w2, w3, [sp, #248]
   8669c:	ldr	x9, [x1, #152]
   866a0:	str	x0, [sp, #136]
   866a4:	ldr	x0, [x4]
   866a8:	str	x0, [sp, #1272]
   866ac:	mov	x0, #0x0                   	// #0
   866b0:	ldr	x0, [x1, #168]
   866b4:	str	x0, [sp, #80]
   866b8:	ldr	x0, [x1, #176]
   866bc:	str	x0, [sp, #192]
   866c0:	ldr	x0, [x1, #184]
   866c4:	str	x0, [sp, #304]
   866c8:	cbz	x9, 87e24 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x17c4>
   866cc:	ldp	x1, x22, [x9, #32]
   866d0:	ldp	x25, x0, [x9, #16]
   866d4:	ldr	x2, [x9, #56]
   866d8:	stp	x1, x2, [sp, #144]
   866dc:	ldr	x2, [x9, #64]
   866e0:	ldr	x1, [x9, #48]
   866e4:	str	x2, [sp, #320]
   866e8:	ldr	x2, [x9, #72]
   866ec:	str	x2, [sp, #280]
   866f0:	ldr	x2, [sp, #136]
   866f4:	cbz	x2, 87e48 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x17e8>
   866f8:	ldr	x3, [x2, #16]
   866fc:	ldp	x26, x21, [x2, #32]
   86700:	str	x3, [sp, #88]
   86704:	ldr	x3, [x2, #24]
   86708:	str	x3, [sp, #40]
   8670c:	ldr	x3, [x2, #48]
   86710:	str	x3, [sp, #8]
   86714:	ldr	x3, [x2, #56]
   86718:	str	x3, [sp, #208]
   8671c:	ldp	x3, x2, [x2, #64]
   86720:	str	x2, [sp, #288]
   86724:	ldr	x2, [sp, #80]
   86728:	str	x3, [sp, #328]
   8672c:	cbz	x2, 87e70 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1810>
   86730:	ldr	x3, [x2, #16]
   86734:	ldp	x28, x20, [x2, #32]
   86738:	str	x3, [sp, #32]
   8673c:	ldr	x3, [x2, #56]
   86740:	ldr	x24, [x2, #48]
   86744:	str	x3, [sp, #160]
   86748:	ldp	x3, x2, [x2, #64]
   8674c:	str	x2, [sp, #296]
   86750:	str	x3, [sp, #336]
   86754:	ldp	x2, x3, [x5, #16]
   86758:	ldp	x19, x23, [x5, #64]
   8675c:	str	x3, [sp, #312]
   86760:	ldr	x3, [x5, #32]
   86764:	ldr	x27, [x5, #48]
   86768:	str	x3, [sp, #200]
   8676c:	ldr	x3, [x5, #56]
   86770:	str	x3, [sp, #48]
   86774:	ldr	x3, [sp, #32]
   86778:	cmp	x2, x3
   8677c:	b.ne	88278 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1c18>  // b.any
   86780:	ldr	x2, [sp, #200]
   86784:	cmp	x0, x2
   86788:	b.ne	8821c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1bbc>  // b.any
   8678c:	ldr	w0, [x9]
   86790:	stp	x9, x1, [sp, #16]
   86794:	str	x5, [sp, #56]
   86798:	bl	200e0 <ggml_type_size@plt>
   8679c:	ldp	x9, x1, [sp, #16]
   867a0:	ldr	x5, [sp, #56]
   867a4:	cmp	x1, x0
   867a8:	b.ne	881c0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1b60>  // b.any
   867ac:	ldr	x0, [sp, #136]
   867b0:	stp	x9, x5, [sp, #16]
   867b4:	ldr	w0, [x0]
   867b8:	bl	200e0 <ggml_type_size@plt>
   867bc:	ldp	x1, x9, [sp, #8]
   867c0:	ldr	x5, [sp, #24]
   867c4:	cmp	x1, x0
   867c8:	b.ne	88164 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1b04>  // b.any
   867cc:	ldr	x0, [sp, #80]
   867d0:	stp	x9, x5, [sp, #8]
   867d4:	ldr	w0, [x0]
   867d8:	bl	200e0 <ggml_type_size@plt>
   867dc:	cmp	x24, x0
   867e0:	ldp	x9, x5, [sp, #8]
   867e4:	b.ne	88108 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1aa8>  // b.any
   867e8:	ldr	x0, [sp, #88]
   867ec:	cmp	x25, x0
   867f0:	b.ne	880ac <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1a4c>  // b.any
   867f4:	cmp	x27, #0x4
   867f8:	b.ne	88050 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x19f0>  // b.any
   867fc:	ldr	x0, [sp, #48]
   86800:	cmp	x0, #0x3
   86804:	b.ls	87ff4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1994>  // b.plast
   86808:	cmp	x0, x19
   8680c:	b.hi	87f3c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x18dc>  // b.pmore
   86810:	cmp	x19, x23
   86814:	b.hi	87ee0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1880>  // b.pmore
   86818:	ldr	x0, [sp, #136]
   8681c:	ldr	w1, [x0]
   86820:	ldr	x0, [sp, #80]
   86824:	str	w1, [sp, #344]
   86828:	ldr	w0, [x0]
   8682c:	cmp	w1, w0
   86830:	b.ne	87f98 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1938>  // b.any
   86834:	ldr	x0, [sp, #144]
   86838:	str	d8, [sp, #1376]
   8683c:	str	d9, [sp, #1384]
   86840:	str	d10, [sp, #1392]
   86844:	str	d11, [sp, #1400]
   86848:	sdiv	x1, x0, x26
   8684c:	str	d14, [sp, #1424]
   86850:	str	d15, [sp, #1432]
   86854:	ldr	s14, [x5, #92]
   86858:	sdiv	x0, x0, x28
   8685c:	ldr	s10, [x5, #84]
   86860:	ldr	w19, [x5, #88]
   86864:	fcmp	s14, #0.0
   86868:	str	x1, [sp, #448]
   8686c:	sdiv	x1, x22, x21
   86870:	str	x0, [sp, #464]
   86874:	sdiv	x0, x22, x20
   86878:	str	x1, [sp, #456]
   8687c:	str	x0, [sp, #472]
   86880:	b.ne	87e90 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1830>  // b.any
   86884:	ldr	x20, [sp, #144]
   86888:	stp	x9, x5, [sp, #8]
   8688c:	ucvtf	d0, w20
   86890:	bl	21200 <log2@plt>
   86894:	fmov	d1, d0
   86898:	mov	w1, #0x1                   	// #1
   8689c:	fmov	s11, w19
   868a0:	fmov	s0, #2.000000000000000000e+00
   868a4:	fcvtmu	w0, d1
   868a8:	fneg	s1, s11
   868ac:	lsl	w0, w1, w0
   868b0:	fmov	s2, w0
   868b4:	str	w0, [sp, #348]
   868b8:	ucvtf	s8, s2
   868bc:	fdiv	s1, s1, s8
   868c0:	bl	20bd0 <powf@plt>
   868c4:	fmov	s1, #5.000000000000000000e-01
   868c8:	fmov	s15, s0
   868cc:	fmov	s0, #2.000000000000000000e+00
   868d0:	fnmul	s1, s1, s11
   868d4:	fdiv	s1, s1, s8
   868d8:	bl	20bd0 <powf@plt>
   868dc:	ldr	x0, [sp, #424]
   868e0:	str	s0, [sp, #484]
   868e4:	ldr	w1, [sp, #252]
   868e8:	ldr	w6, [x0]
   868ec:	ldr	w0, [sp, #248]
   868f0:	cmp	w0, w1
   868f4:	b.ge	875e4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xf84>  // b.tcont
   868f8:	ldr	x7, [sp, #32]
   868fc:	mov	x2, #0x2010                	// #8208
   86900:	sxtw	x6, w6
   86904:	mvni	v9.2s, #0x80, lsl #16
   86908:	str	d12, [sp, #1408]
   8690c:	mvni	v12.2s, #0x7f, msl #16
   86910:	ldr	x5, [sp, #88]
   86914:	str	d13, [sp, #1416]
   86918:	ldr	x8, [sp, #200]
   8691c:	lsl	x26, x7, #2
   86920:	mov	w22, w7
   86924:	sbfiz	x28, x7, #2, #32
   86928:	add	x0, x7, x5
   8692c:	add	x1, x5, x7, lsl #1
   86930:	lsr	x4, x5, #2
   86934:	add	x0, x2, x0, lsl #7
   86938:	and	x2, x5, #0xfffffffffffffffc
   8693c:	sxtw	x18, w5
   86940:	add	x9, x2, #0x1
   86944:	mul	x3, x20, x8
   86948:	mov	w12, w8
   8694c:	mul	w11, w20, w8
   86950:	add	x10, x2, #0x2
   86954:	mov	x19, x18
   86958:	mul	x0, x0, x6
   8695c:	lsl	x6, x9, #2
   86960:	str	x9, [sp, #384]
   86964:	str	x3, [sp, #432]
   86968:	lsr	x3, x5, #3
   8696c:	str	x6, [sp, #544]
   86970:	lsl	x6, x9, #6
   86974:	ldr	x9, [sp, #312]
   86978:	str	x6, [sp, #376]
   8697c:	ldr	x6, [sp, #48]
   86980:	str	x10, [sp, #368]
   86984:	str	w12, [sp, #480]
   86988:	mul	x8, x8, x9
   8698c:	str	w11, [sp, #600]
   86990:	mul	x6, x6, x9
   86994:	str	x8, [sp, #592]
   86998:	lsl	x8, x2, #2
   8699c:	lsl	x2, x2, #6
   869a0:	str	x2, [sp, #392]
   869a4:	lsl	x2, x0, #2
   869a8:	str	x8, [sp, #552]
   869ac:	add	x8, x0, x5, lsl #6
   869b0:	add	x0, x0, x1, lsl #6
   869b4:	lsl	x1, x3, #11
   869b8:	str	x6, [sp, #416]
   869bc:	lsl	x6, x10, #2
   869c0:	str	x2, [sp, #440]
   869c4:	lsl	x2, x4, #4
   869c8:	add	x0, x0, #0x2, lsl #12
   869cc:	str	x1, [sp, #240]
   869d0:	lsl	x1, x5, #8
   869d4:	lsl	x0, x0, #2
   869d8:	str	x8, [sp, #224]
   869dc:	lsl	x8, x8, #2
   869e0:	str	x6, [sp, #536]
   869e4:	lsl	x6, x10, #6
   869e8:	str	x0, [sp, #560]
   869ec:	lsl	x0, x7, #8
   869f0:	str	x2, [sp, #232]
   869f4:	str	x0, [sp, #272]
   869f8:	lsl	x0, x5, #2
   869fc:	str	x6, [sp, #360]
   86a00:	stp	x1, x0, [sp, #176]
   86a04:	sxtw	x0, w7
   86a08:	add	x1, x8, #0x4, lsl #12
   86a0c:	str	x0, [sp, #496]
   86a10:	ldr	x0, [sp, #160]
   86a14:	str	x1, [sp, #512]
   86a18:	lsl	x0, x0, #6
   86a1c:	str	x0, [sp, #408]
   86a20:	ldr	x0, [sp, #208]
   86a24:	str	s15, [sp, #604]
   86a28:	fmov	s15, s10
   86a2c:	ldr	x9, [sp, #8]
   86a30:	str	x8, [sp, #608]
   86a34:	lsl	x0, x0, #6
   86a38:	str	x0, [sp, #400]
   86a3c:	sub	x0, x5, #0x1
   86a40:	mov	x27, x9
   86a44:	str	x0, [sp, #488]
   86a48:	and	x0, x5, #0xfffffffffffffff8
   86a4c:	str	x0, [sp, #504]
   86a50:	sbfiz	x0, x5, #2, #32
   86a54:	ldr	x5, [sp, #16]
   86a58:	str	x0, [sp, #576]
   86a5c:	str	x5, [sp, #616]
   86a60:	ldp	w6, w1, [sp, #248]
   86a64:	mov	w5, #0x40                  	// #64
   86a68:	ldr	x0, [sp, #432]
   86a6c:	ldr	w8, [sp, #600]
   86a70:	sxtw	x2, w6
   86a74:	sub	w1, w1, w6
   86a78:	ldr	w7, [sp, #480]
   86a7c:	sdiv	x0, x2, x0
   86a80:	sub	w3, w7, w6
   86a84:	sxtw	x4, w0
   86a88:	mul	w0, w8, w0
   86a8c:	ldr	x8, [sp, #144]
   86a90:	str	x4, [sp, #64]
   86a94:	sub	w6, w6, w0
   86a98:	mul	x4, x4, x8
   86a9c:	ldr	x8, [sp, #200]
   86aa0:	msub	x2, x4, x8, x2
   86aa4:	sdiv	x2, x2, x8
   86aa8:	str	x2, [sp, #120]
   86aac:	mul	w2, w7, w2
   86ab0:	add	w0, w0, w2
   86ab4:	sub	w2, w6, w2
   86ab8:	add	w0, w0, w3
   86abc:	cmp	w0, w1
   86ac0:	csel	w0, w0, w1, le
   86ac4:	str	w0, [sp, #8]
   86ac8:	cmp	w0, w5
   86acc:	csel	w1, w0, w5, le
   86ad0:	str	w1, [sp, #16]
   86ad4:	str	w2, [sp, #24]
   86ad8:	cmp	w0, #0x0
   86adc:	b.le	87ea4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1844>
   86ae0:	fcmpe	s11, #0.0
   86ae4:	b.gt	87c4c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x15ec>
   86ae8:	fmov	s13, #1.000000000000000000e+00
   86aec:	movi	v0.4s, #0x0
   86af0:	mvni	v1.4s, #0x7f, msl #16
   86af4:	add	x23, sp, #0x3f8
   86af8:	ldr	x4, [sp, #272]
   86afc:	mov	w1, #0x0                   	// #0
   86b00:	stp	q0, q0, [x23]
   86b04:	stp	q0, q0, [x23, #32]
   86b08:	stp	q0, q0, [x23, #64]
   86b0c:	stp	q0, q0, [x23, #96]
   86b10:	stp	q0, q0, [x23, #128]
   86b14:	stp	q0, q0, [x23, #160]
   86b18:	stp	q0, q0, [x23, #192]
   86b1c:	stp	q1, q1, [sp, #752]
   86b20:	stp	q1, q1, [sp, #784]
   86b24:	stp	q1, q1, [sp, #816]
   86b28:	stp	q1, q1, [sp, #848]
   86b2c:	stp	q1, q1, [sp, #880]
   86b30:	stp	q1, q1, [sp, #912]
   86b34:	stp	q1, q1, [sp, #944]
   86b38:	stp	q1, q1, [sp, #976]
   86b3c:	stp	q0, q0, [x23, #224]
   86b40:	ldr	x0, [sp, #424]
   86b44:	mov	x2, x4
   86b48:	ldr	x3, [sp, #440]
   86b4c:	ldr	x0, [x0, #16]
   86b50:	add	x20, x0, x3
   86b54:	str	x0, [sp, #128]
   86b58:	ldr	x0, [sp, #176]
   86b5c:	str	x20, [sp, #352]
   86b60:	add	x21, x20, x0
   86b64:	add	x3, x21, #0x8, lsl #12
   86b68:	add	x24, x21, #0x4, lsl #12
   86b6c:	add	x5, x3, x4
   86b70:	mov	x0, x3
   86b74:	str	x3, [sp, #216]
   86b78:	add	x3, x3, x4, lsl #1
   86b7c:	str	x24, [sp, #104]
   86b80:	mov	x25, x3
   86b84:	str	x5, [sp, #168]
   86b88:	bl	1f8e0 <memset@plt>
   86b8c:	mov	x0, x24
   86b90:	mov	x2, #0x4000                	// #16384
   86b94:	mov	w1, #0x0                   	// #0
   86b98:	bl	1f8e0 <memset@plt>
   86b9c:	ldr	x1, [sp, #64]
   86ba0:	mov	x5, x20
   86ba4:	mov	w4, #0x0                   	// #0
   86ba8:	ldp	x3, x2, [sp, #448]
   86bac:	str	x21, [sp, #112]
   86bb0:	ldrsw	x0, [sp, #120]
   86bb4:	sdiv	x2, x1, x2
   86bb8:	str	x19, [sp, #264]
   86bbc:	mov	x19, x27
   86bc0:	mov	x27, x23
   86bc4:	ldr	x24, [sp, #184]
   86bc8:	sdiv	x3, x0, x3
   86bcc:	str	x0, [sp, #72]
   86bd0:	str	x2, [sp, #56]
   86bd4:	ldrsw	x2, [sp, #24]
   86bd8:	str	x3, [sp, #24]
   86bdc:	ldr	x3, [sp, #464]
   86be0:	str	x2, [sp, #256]
   86be4:	sdiv	x20, x0, x3
   86be8:	ldr	x3, [sp, #472]
   86bec:	sdiv	x3, x1, x3
   86bf0:	mov	x23, x20
   86bf4:	mov	w20, w4
   86bf8:	str	x3, [sp, #96]
   86bfc:	ldr	x3, [sp, #280]
   86c00:	mul	x3, x1, x3
   86c04:	ldr	x1, [sp, #320]
   86c08:	madd	x3, x0, x1, x3
   86c0c:	ldr	x0, [sp, #152]
   86c10:	madd	x3, x0, x2, x3
   86c14:	mov	x21, x3
   86c18:	ldr	x1, [x19, #248]
   86c1c:	mov	x0, x5
   86c20:	mov	x2, x24
   86c24:	add	w20, w20, #0x1
   86c28:	add	x1, x1, x21
   86c2c:	bl	1efe0 <memcpy@plt>
   86c30:	add	x5, x0, x24
   86c34:	ldr	x0, [sp, #152]
   86c38:	add	x21, x21, x0
   86c3c:	ldr	w0, [sp, #16]
   86c40:	cmp	w0, w20
   86c44:	b.gt	86c18 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x5b8>
   86c48:	ldr	w0, [sp, #8]
   86c4c:	mov	x20, x23
   86c50:	mov	x23, x27
   86c54:	mov	x27, x19
   86c58:	ldr	x21, [sp, #112]
   86c5c:	ldr	x19, [sp, #264]
   86c60:	cmp	w0, #0x3f
   86c64:	b.gt	86cb0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x650>
   86c68:	ldr	w4, [sp, #16]
   86c6c:	str	x19, [sp, #8]
   86c70:	ldr	x0, [sp, #88]
   86c74:	ldr	x24, [sp, #184]
   86c78:	sxtw	x3, w4
   86c7c:	mov	w19, w4
   86c80:	mul	x3, x3, x0
   86c84:	ldr	x0, [sp, #352]
   86c88:	add	x3, x0, x3, lsl #2
   86c8c:	mov	x0, x3
   86c90:	mov	x2, x24
   86c94:	mov	w1, #0x0                   	// #0
   86c98:	add	w19, w19, #0x1
   86c9c:	bl	1f8e0 <memset@plt>
   86ca0:	add	x3, x0, x24
   86ca4:	cmp	w19, #0x40
   86ca8:	b.ne	86c8c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x62c>  // b.any
   86cac:	ldr	x19, [sp, #8]
   86cb0:	mov	w1, #0x0                   	// #0
   86cb4:	mov	x0, x25
   86cb8:	ldr	x2, [sp, #176]
   86cbc:	bl	1f8e0 <memset@plt>
   86cc0:	ldr	x0, [sp, #168]
   86cc4:	mov	w1, #0x0                   	// #0
   86cc8:	ldr	x2, [sp, #272]
   86ccc:	bl	1f8e0 <memset@plt>
   86cd0:	ldr	x0, [sp, #40]
   86cd4:	cmp	x0, #0x0
   86cd8:	b.le	87480 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xe20>
   86cdc:	ldr	x4, [sp, #288]
   86ce0:	sxtw	x2, w20
   86ce4:	mov	x10, x25
   86ce8:	str	x27, [sp, #624]
   86cec:	mov	w27, w22
   86cf0:	ldrsw	x1, [sp, #56]
   86cf4:	ldr	x5, [sp, #560]
   86cf8:	ldrsw	x0, [sp, #96]
   86cfc:	mul	x1, x1, x4
   86d00:	ldr	x4, [sp, #128]
   86d04:	ldrsw	x3, [sp, #24]
   86d08:	str	xzr, [sp, #24]
   86d0c:	ldr	x18, [sp, #88]
   86d10:	add	x5, x4, x5
   86d14:	ldr	x9, [sp, #104]
   86d18:	str	x5, [sp, #568]
   86d1c:	ldr	x5, [sp, #608]
   86d20:	ldr	x8, [sp, #496]
   86d24:	add	x5, x4, x5
   86d28:	str	x5, [sp, #528]
   86d2c:	ldr	x5, [sp, #296]
   86d30:	mul	x0, x0, x5
   86d34:	ldr	x5, [sp, #512]
   86d38:	add	x4, x4, x5
   86d3c:	str	x4, [sp, #520]
   86d40:	ldr	x4, [sp, #16]
   86d44:	ubfiz	x4, x4, #8, #26
   86d48:	str	x4, [sp, #584]
   86d4c:	ldr	x4, [sp, #328]
   86d50:	madd	x1, x3, x4, x1
   86d54:	mov	x4, x21
   86d58:	str	x1, [sp, #96]
   86d5c:	ldr	x1, [sp, #336]
   86d60:	madd	x0, x2, x1, x0
   86d64:	str	x0, [sp, #56]
   86d68:	ldr	x0, [sp, #24]
   86d6c:	ldr	x2, [sp, #40]
   86d70:	ldr	x6, [sp, #192]
   86d74:	sub	x20, x2, x0
   86d78:	mov	x0, #0x40                  	// #64
   86d7c:	cmp	x20, x0
   86d80:	csel	x21, x20, x0, le
   86d84:	mov	w3, w21
   86d88:	cbz	x6, 86fac <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x94c>
   86d8c:	ldr	x5, [sp, #224]
   86d90:	sub	w0, w0, w21
   86d94:	mov	w22, #0x3f                  	// #63
   86d98:	mvni	v1.4s, #0x7f, msl #16
   86d9c:	ldp	x11, x2, [x6, #32]
   86da0:	and	w15, w0, #0xfffffff8
   86da4:	lsr	w14, w0, #3
   86da8:	and	w0, w0, #0x7
   86dac:	sub	w22, w22, w21
   86db0:	add	w15, w15, w21
   86db4:	cmp	w22, #0x7
   86db8:	csel	w15, w21, w15, ls	// ls = plast
   86dbc:	ldp	x24, x12, [x6, #56]
   86dc0:	add	w16, w15, #0x1
   86dc4:	add	w17, w15, #0x2
   86dc8:	add	x7, x21, x5
   86dcc:	add	w25, w15, #0x3
   86dd0:	add	w30, w15, #0x4
   86dd4:	add	w13, w15, #0x5
   86dd8:	str	w0, [sp, #264]
   86ddc:	ldr	x5, [sp, #128]
   86de0:	str	x12, [sp, #8]
   86de4:	add	x7, x5, x7, lsl #2
   86de8:	ldr	x5, [x6, #72]
   86dec:	ldr	x6, [x6, #248]
   86df0:	stp	x5, x6, [sp, #104]
   86df4:	ldr	x5, [sp, #64]
   86df8:	ldp	x6, x12, [sp, #64]
   86dfc:	sdiv	x1, x5, x2
   86e00:	add	w5, w15, #0x6
   86e04:	sdiv	x0, x12, x11
   86e08:	mov	w12, #0x0                   	// #0
   86e0c:	msub	x1, x1, x2, x6
   86e10:	ldr	x6, [sp, #104]
   86e14:	str	w27, [sp, #104]
   86e18:	add	w27, w15, #0x7
   86e1c:	ldr	x2, [sp, #72]
   86e20:	mul	x1, x1, x6
   86e24:	ldr	x6, [sp, #8]
   86e28:	str	x26, [sp, #8]
   86e2c:	msub	x0, x0, x11, x2
   86e30:	ldr	x2, [sp, #256]
   86e34:	ldr	w26, [sp, #264]
   86e38:	madd	x0, x0, x6, x1
   86e3c:	ldr	x1, [sp, #24]
   86e40:	mul	x2, x24, x2
   86e44:	ldr	x6, [sp, #112]
   86e48:	str	x18, [sp, #112]
   86e4c:	ldr	w18, [sp, #16]
   86e50:	add	x2, x2, x1, lsl #1
   86e54:	mov	w1, #0x1                   	// #1
   86e58:	add	x0, x0, x2
   86e5c:	add	x2, x6, x0
   86e60:	mov	x6, x9
   86e64:	lsl	w11, w12, #6
   86e68:	mov	x0, #0x0                   	// #0
   86e6c:	ldr	h0, [x2, x0, lsl #1]
   86e70:	fcvt	s0, h0
   86e74:	fmul	s0, s0, s13
   86e78:	fcmp	s0, s9
   86e7c:	str	s0, [x6, x0, lsl #2]
   86e80:	add	x0, x0, #0x1
   86e84:	csel	w1, wzr, w1, pl	// pl = nfrst
   86e88:	cmp	w3, w0
   86e8c:	b.gt	86e6c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x80c>
   86e90:	cmp	x20, #0x3f
   86e94:	b.gt	86f84 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>
   86e98:	cmp	w22, #0x7
   86e9c:	b.ls	86f0c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8ac>  // b.plast
   86ea0:	str	q1, [x7, #16384]
   86ea4:	str	q1, [x7, #16400]
   86ea8:	cmp	w14, #0x1
   86eac:	b.ls	86f08 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8a8>  // b.plast
   86eb0:	str	q1, [x7, #16416]
   86eb4:	str	q1, [x7, #16432]
   86eb8:	cmp	w14, #0x2
   86ebc:	b.eq	86f08 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8a8>  // b.none
   86ec0:	str	q1, [x7, #16448]
   86ec4:	str	q1, [x7, #16464]
   86ec8:	cmp	w14, #0x3
   86ecc:	b.eq	86f08 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8a8>  // b.none
   86ed0:	str	q1, [x7, #16480]
   86ed4:	str	q1, [x7, #16496]
   86ed8:	cmp	w14, #0x4
   86edc:	b.eq	86f08 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8a8>  // b.none
   86ee0:	str	q1, [x7, #16512]
   86ee4:	str	q1, [x7, #16528]
   86ee8:	cmp	w14, #0x5
   86eec:	b.eq	86f08 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8a8>  // b.none
   86ef0:	str	q1, [x7, #16544]
   86ef4:	str	q1, [x7, #16560]
   86ef8:	cmp	w14, #0x7
   86efc:	b.ne	86f08 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8a8>  // b.any
   86f00:	str	q1, [x7, #16576]
   86f04:	str	q1, [x7, #16592]
   86f08:	cbz	w26, 86f84 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>
   86f0c:	add	w0, w11, w15
   86f10:	str	s12, [x9, w0, sxtw #2]
   86f14:	cmp	w16, #0x40
   86f18:	b.eq	86f84 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   86f1c:	add	w0, w11, w16
   86f20:	str	s12, [x9, w0, sxtw #2]
   86f24:	cmp	w17, #0x40
   86f28:	b.eq	86f84 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   86f2c:	add	w0, w11, w17
   86f30:	str	s12, [x9, w0, sxtw #2]
   86f34:	cmp	w25, #0x40
   86f38:	b.eq	86f84 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   86f3c:	add	w0, w11, w25
   86f40:	str	s12, [x9, w0, sxtw #2]
   86f44:	cmp	w30, #0x40
   86f48:	b.eq	86f84 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   86f4c:	add	w0, w11, w30
   86f50:	str	s12, [x9, w0, sxtw #2]
   86f54:	cmp	w13, #0x40
   86f58:	b.eq	86f84 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   86f5c:	add	w0, w11, w13
   86f60:	str	s12, [x9, w0, sxtw #2]
   86f64:	cmp	w5, #0x40
   86f68:	b.eq	86f84 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   86f6c:	add	w0, w11, w5
   86f70:	str	s12, [x9, w0, sxtw #2]
   86f74:	cmp	w27, #0x40
   86f78:	b.eq	86f84 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   86f7c:	add	w11, w11, w27
   86f80:	str	s12, [x9, w11, sxtw #2]
   86f84:	add	w12, w12, #0x1
   86f88:	add	x7, x7, #0x100
   86f8c:	add	x2, x2, x24
   86f90:	add	x6, x6, #0x100
   86f94:	cmp	w18, w12
   86f98:	b.gt	86e64 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x804>
   86f9c:	ldr	x26, [sp, #8]
   86fa0:	ldr	x18, [sp, #112]
   86fa4:	ldr	w27, [sp, #104]
   86fa8:	tbnz	w1, #0, 87440 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xde0>
   86fac:	str	x4, [sp, #264]
   86fb0:	mov	x2, x10
   86fb4:	mov	x7, #0x0                   	// #0
   86fb8:	ldr	x0, [sp, #136]
   86fbc:	and	x17, x18, #0x3
   86fc0:	mov	x22, x20
   86fc4:	str	x8, [sp, #632]
   86fc8:	ldr	x15, [sp, #184]
   86fcc:	ldr	x13, [sp, #208]
   86fd0:	ldr	x1, [x0, #248]
   86fd4:	ldr	x0, [sp, #176]
   86fd8:	ldr	x14, [sp, #488]
   86fdc:	ldr	x24, [sp, #504]
   86fe0:	sub	x16, x0, #0xfc
   86fe4:	ldr	x0, [sp, #96]
   86fe8:	ldr	x4, [sp, #536]
   86fec:	ldr	x8, [sp, #544]
   86ff0:	add	x1, x1, x0
   86ff4:	ldr	x25, [sp, #552]
   86ff8:	ldr	x6, [sp, #568]
   86ffc:	ldr	w12, [sp, #344]
   87000:	cmp	w12, #0x1
   87004:	b.eq	87714 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x10b4>  // b.none
   87008:	cmp	x18, #0x0
   8700c:	b.le	87048 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   87010:	cmp	x14, #0x2
   87014:	b.ls	87920 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x12c0>  // b.plast
   87018:	add	x0, x16, x6
   8701c:	add	x5, x15, x1
   87020:	cmp	x1, x0
   87024:	mov	x0, #0x0                   	// #0
   87028:	ccmp	x6, x5, #0x2, cc	// cc = lo, ul, last
   8702c:	b.cs	87880 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1220>  // b.hs, b.nlast
   87030:	ldr	s0, [x1, x0, lsl #2]
   87034:	lsl	x5, x0, #8
   87038:	add	x0, x0, #0x1
   8703c:	str	s0, [x2, x5]
   87040:	cmp	x18, x0
   87044:	b.ne	87030 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9d0>  // b.any
   87048:	add	x7, x7, #0x1
   8704c:	add	x1, x1, x13
   87050:	add	x2, x2, #0x4
   87054:	add	x6, x6, #0x4
   87058:	cmp	w3, w7
   8705c:	b.gt	87000 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9a0>
   87060:	ldr	x4, [sp, #264]
   87064:	mov	x2, #0x4000                	// #16384
   87068:	mov	w1, #0x0                   	// #0
   8706c:	str	w3, [sp, #8]
   87070:	mov	x20, x22
   87074:	ldr	x8, [sp, #632]
   87078:	stp	x18, x10, [sp, #104]
   8707c:	mov	x0, x4
   87080:	str	x9, [sp, #632]
   87084:	str	x8, [sp, #264]
   87088:	bl	1f8e0 <memset@plt>
   8708c:	ldp	x18, x10, [sp, #104]
   87090:	mov	x4, x0
   87094:	mov	x2, x0
   87098:	mov	x12, x0
   8709c:	ldr	x8, [sp, #264]
   870a0:	ldr	x7, [sp, #352]
   870a4:	ldr	x1, [sp, #576]
   870a8:	ldr	x9, [sp, #632]
   870ac:	ldr	w3, [sp, #8]
   870b0:	mov	x5, x10
   870b4:	mov	x6, #0x0                   	// #0
   870b8:	nop
   870bc:	nop
   870c0:	ldr	s0, [x12, x6, lsl #2]
   870c4:	cmp	x19, #0x0
   870c8:	b.le	870ec <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xa8c>
   870cc:	mov	x0, #0x0                   	// #0
   870d0:	lsl	x11, x0, #8
   870d4:	ldr	s2, [x7, x0, lsl #2]
   870d8:	add	x0, x0, #0x1
   870dc:	ldr	s1, [x5, x11]
   870e0:	fmadd	s0, s2, s1, s0
   870e4:	cmp	x0, x19
   870e8:	b.ne	870d0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xa70>  // b.any
   870ec:	str	s0, [x12, x6, lsl #2]
   870f0:	add	x6, x6, #0x1
   870f4:	add	x5, x5, #0x4
   870f8:	cmp	x6, #0x40
   870fc:	b.ne	870c0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xa60>  // b.any
   87100:	add	x12, x12, #0x100
   87104:	add	x7, x7, x1
   87108:	cmp	x9, x12
   8710c:	b.ne	870b0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xa50>  // b.any
   87110:	str	x9, [sp, #8]
   87114:	stp	x2, x8, [sp, #104]
   87118:	str	w3, [sp, #264]
   8711c:	str	x10, [sp, #632]
   87120:	str	x4, [sp, #640]
   87124:	str	x18, [sp, #648]
   87128:	bl	21300 <ggml_cpu_get_sve_cnt@plt>
   8712c:	mov	z1.s, s15
   87130:	lsl	w0, w0, #3
   87134:	ldr	x9, [sp, #8]
   87138:	add	w6, w0, #0x1f
   8713c:	cmp	w0, #0x0
   87140:	csel	w0, w6, w0, lt	// lt = tstop
   87144:	ldp	x2, x8, [sp, #104]
   87148:	asr	w6, w0, #5
   8714c:	neg	w0, w6, lsl #1
   87150:	lsl	w7, w6, #1
   87154:	ldr	x10, [sp, #632]
   87158:	and	w1, w0, #0x1000
   8715c:	ldr	x4, [sp, #640]
   87160:	ldr	x18, [sp, #648]
   87164:	ldr	w3, [sp, #264]
   87168:	tbz	w0, #12, 87c74 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1614>
   8716c:	add	x0, x4, w6, sxtw #2
   87170:	sbfiz	x11, x7, #2, #32
   87174:	mov	x1, x4
   87178:	ptrue	p0.b
   8717c:	mov	w6, #0x0                   	// #0
   87180:	ld1w	{z0.s}, p0/z, [x1]
   87184:	fmul	z0.s, p0/m, z0.s, z1.s
   87188:	st1w	{z0.s}, p0, [x1]
   8718c:	add	w6, w6, w7
   87190:	add	x1, x1, x11
   87194:	ld1w	{z0.s}, p0/z, [x0]
   87198:	fmul	z0.s, p0/m, z0.s, z1.s
   8719c:	st1w	{z0.s}, p0, [x0]
   871a0:	add	x0, x0, x11
   871a4:	cmp	w6, #0xfff
   871a8:	b.le	87180 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb20>
   871ac:	fcmp	s14, #0.0
   871b0:	b.ne	87928 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x12c8>  // b.any
   871b4:	cmp	x20, #0x3f
   871b8:	b.le	87a18 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x13b8>
   871bc:	ldr	x0, [sp, #192]
   871c0:	cbnz	x0, 87b68 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1508>
   871c4:	ldr	x22, [sp, #216]
   871c8:	add	x24, x4, #0x100
   871cc:	movi	v0.4s, #0x0
   871d0:	add	x5, sp, #0x2b0
   871d4:	str	x10, [sp, #264]
   871d8:	add	x10, sp, #0x280
   871dc:	mov	x20, x24
   871e0:	mov	x21, #0x1                   	// #1
   871e4:	add	x25, sp, #0x2f0
   871e8:	stp	x18, x4, [sp, #104]
   871ec:	stp	x8, x19, [x10]
   871f0:	mov	x19, x5
   871f4:	stp	x24, x2, [x10, #16]
   871f8:	mov	x24, x21
   871fc:	mov	x21, x22
   87200:	str	x22, [sp, #672]
   87204:	mov	x22, x20
   87208:	mov	w20, w27
   8720c:	stp	q0, q0, [x5]
   87210:	stp	q0, q0, [x5, #32]
   87214:	str	w3, [sp, #632]
   87218:	str	x9, [sp, #680]
   8721c:	nop
   87220:	mvni	v1.2s, #0x7f, msl #16
   87224:	sub	x2, x22, #0x100
   87228:	mov	x0, x2
   8722c:	ldr	s0, [x0], #4
   87230:	fcmpe	s0, s1
   87234:	fcsel	s1, s1, s0, mi	// mi = first
   87238:	cmp	x22, x0
   8723c:	b.ne	8722c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xbcc>  // b.any
   87240:	fcmp	s1, s12
   87244:	b.eq	87638 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xfd8>  // b.none
   87248:	add	x0, x25, x24, lsl #2
   8724c:	lsl	x27, x24, #2
   87250:	ldur	s0, [x0, #-4]
   87254:	fmaxnm	s8, s0, s1
   87258:	fcmpe	s0, s8
   8725c:	b.mi	87648 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xfe8>  // b.first
   87260:	add	x4, x25, x27
   87264:	fmov	s0, s8
   87268:	mov	x1, x2
   8726c:	mov	w0, #0x40                  	// #64
   87270:	stur	s8, [x4, #-4]
   87274:	bl	1f600 <ggml_vec_soft_max_f32@plt>
   87278:	add	x7, x27, x23
   8727c:	ldur	s1, [x7, #-4]
   87280:	fcvt	d1, s1
   87284:	fadd	d1, d1, d0
   87288:	fcvt	s1, d1
   8728c:	stur	s1, [x7, #-4]
   87290:	add	x24, x24, #0x1
   87294:	add	x22, x22, #0x100
   87298:	add	x21, x21, x26
   8729c:	cmp	x24, #0x41
   872a0:	b.ne	87220 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xbc0>  // b.any
   872a4:	ldr	w0, [sp, #344]
   872a8:	add	x9, sp, #0x280
   872ac:	mov	x5, x19
   872b0:	ldp	x8, x19, [x9]
   872b4:	mov	w27, w20
   872b8:	ldp	x24, x2, [x9, #16]
   872bc:	ldp	x18, x4, [sp, #104]
   872c0:	ldr	x10, [sp, #264]
   872c4:	ldr	x11, [sp, #672]
   872c8:	ldr	x9, [sp, #680]
   872cc:	ldr	w3, [sp, #632]
   872d0:	cmp	w0, #0x1
   872d4:	b.eq	87b98 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1538>  // b.none
   872d8:	add	x7, sp, #0x278
   872dc:	ldp	x22, x6, [sp, #160]
   872e0:	mov	w20, #0x0                   	// #0
   872e4:	stp	x19, x24, [x7]
   872e8:	mov	w19, w3
   872ec:	ldr	x21, [sp, #56]
   872f0:	str	x23, [sp, #672]
   872f4:	mov	w23, w20
   872f8:	mov	x20, x26
   872fc:	mov	x26, x9
   87300:	str	x18, [sp, #8]
   87304:	stp	x2, x11, [x7, #16]
   87308:	mov	x24, x21
   8730c:	ldr	x21, [sp, #80]
   87310:	stp	x4, x10, [sp, #104]
   87314:	str	x8, [sp, #264]
   87318:	str	x5, [sp, #664]
   8731c:	ldr	x1, [x21, #248]
   87320:	mov	x0, x6
   87324:	mov	x2, x20
   87328:	add	w23, w23, #0x1
   8732c:	add	x1, x1, x24
   87330:	add	x24, x24, x22
   87334:	bl	1efe0 <memcpy@plt>
   87338:	add	x6, x0, x20
   8733c:	cmp	w19, w23
   87340:	b.gt	8731c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xcbc>
   87344:	add	x5, sp, #0x278
   87348:	ldr	x18, [sp, #8]
   8734c:	mov	x9, x26
   87350:	ldp	x19, x24, [x5]
   87354:	mov	x26, x20
   87358:	ldp	x2, x11, [x5, #16]
   8735c:	ldp	x4, x10, [sp, #104]
   87360:	ldr	x8, [sp, #264]
   87364:	ldr	x5, [sp, #664]
   87368:	ldr	x23, [sp, #672]
   8736c:	movi	v0.4s, #0x0
   87370:	mov	x22, x5
   87374:	mov	x0, x4
   87378:	b	8738c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd2c>
   8737c:	add	x22, x22, #0x1
   87380:	add	x0, x0, #0x100
   87384:	cmp	x25, x22
   87388:	b.eq	873c4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd64>  // b.none
   8738c:	ldrb	w1, [x22]
   87390:	tbz	w1, #0, 8737c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd1c>
   87394:	add	x22, x22, #0x1
   87398:	stp	q0, q0, [x0]
   8739c:	stp	q0, q0, [x0, #32]
   873a0:	stp	q0, q0, [x0, #64]
   873a4:	stp	q0, q0, [x0, #96]
   873a8:	stp	q0, q0, [x0, #128]
   873ac:	stp	q0, q0, [x0, #160]
   873b0:	stp	q0, q0, [x0, #192]
   873b4:	stp	q0, q0, [x0, #224]
   873b8:	add	x0, x0, #0x100
   873bc:	cmp	x25, x22
   873c0:	b.ne	8738c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd2c>  // b.any
   873c4:	cmp	x8, #0x0
   873c8:	b.le	87440 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xde0>
   873cc:	ldr	x3, [sp, #168]
   873d0:	mov	x0, #0x4100                	// #16640
   873d4:	add	x1, x4, x0
   873d8:	nop
   873dc:	nop
   873e0:	mov	x6, x3
   873e4:	mov	x5, #0x0                   	// #0
   873e8:	ldr	s0, [x11, x5, lsl #2]
   873ec:	mov	x7, x6
   873f0:	mov	x0, x2
   873f4:	nop
   873f8:	nop
   873fc:	nop
   87400:	ldr	s1, [x7]
   87404:	add	x7, x7, x28
   87408:	ldr	s2, [x0], #4
   8740c:	fmadd	s0, s2, s1, s0
   87410:	cmp	x24, x0
   87414:	b.ne	87400 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xda0>  // b.any
   87418:	str	s0, [x11, x5, lsl #2]
   8741c:	add	x5, x5, #0x1
   87420:	add	x6, x6, #0x4
   87424:	cmp	x5, x8
   87428:	b.ne	873e8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd88>  // b.any
   8742c:	add	x24, x24, #0x100
   87430:	add	x11, x11, x28
   87434:	add	x2, x2, #0x100
   87438:	cmp	x1, x24
   8743c:	b.ne	873e0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd80>  // b.any
   87440:	ldr	x1, [sp, #56]
   87444:	ldr	x2, [sp, #408]
   87448:	ldr	x0, [sp, #24]
   8744c:	add	x1, x1, x2
   87450:	ldr	x2, [sp, #400]
   87454:	str	x1, [sp, #56]
   87458:	add	x0, x0, #0x40
   8745c:	ldr	x1, [sp, #96]
   87460:	str	x0, [sp, #24]
   87464:	add	x1, x1, x2
   87468:	str	x1, [sp, #96]
   8746c:	ldr	x1, [sp, #40]
   87470:	cmp	x1, x0
   87474:	b.gt	86d68 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x708>
   87478:	mov	w22, w27
   8747c:	ldr	x27, [sp, #624]
   87480:	ldr	x0, [sp, #304]
   87484:	cbnz	x0, 87ca4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1644>
   87488:	ldp	x1, x2, [sp, #64]
   8748c:	mov	x21, x23
   87490:	fmov	s13, #1.000000000000000000e+00
   87494:	mov	w23, #0x0                   	// #0
   87498:	mov	w20, w23
   8749c:	mov	x23, x19
   874a0:	ldr	x0, [sp, #592]
   874a4:	ldr	x3, [sp, #312]
   874a8:	madd	x0, x0, x1, x2
   874ac:	ldr	x2, [sp, #256]
   874b0:	ldr	x1, [sp, #216]
   874b4:	madd	x0, x2, x3, x0
   874b8:	ldr	x2, [sp, #48]
   874bc:	mov	x19, x1
   874c0:	mul	x25, x0, x2
   874c4:	mov	x24, x25
   874c8:	mov	w25, w22
   874cc:	mov	x22, x21
   874d0:	ldr	x21, [sp, #616]
   874d4:	movi	v8.2s, #0x0
   874d8:	ldr	s0, [x22]
   874dc:	fcmp	s0, s8
   874e0:	b.eq	874e8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xe88>  // b.none
   874e4:	fdiv	s8, s13, s0
   874e8:	bl	21300 <ggml_cpu_get_sve_cnt@plt>
   874ec:	mov	z8.s, s8
   874f0:	lsl	w0, w0, #3
   874f4:	cmp	w0, #0x0
   874f8:	add	w6, w0, #0x1f
   874fc:	csel	w6, w6, w0, lt	// lt = tstop
   87500:	asr	w6, w6, #5
   87504:	neg	w0, w6, lsl #1
   87508:	lsl	w7, w6, #1
   8750c:	ands	w0, w0, w25
   87510:	b.le	87554 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xef4>
   87514:	sbfiz	x5, x7, #2, #32
   87518:	mov	x3, x19
   8751c:	ptrue	p0.b
   87520:	add	x2, x19, w6, sxtw #2
   87524:	mov	w4, #0x0                   	// #0
   87528:	ld1w	{z0.s}, p0/z, [x3]
   8752c:	fmul	z0.s, p0/m, z0.s, z8.s
   87530:	st1w	{z0.s}, p0, [x3]
   87534:	add	w4, w4, w7
   87538:	add	x3, x3, x5
   8753c:	ld1w	{z0.s}, p0/z, [x2]
   87540:	fmul	z0.s, p0/m, z0.s, z8.s
   87544:	st1w	{z0.s}, p0, [x2]
   87548:	add	x2, x2, x5
   8754c:	cmp	w0, w4
   87550:	b.gt	87528 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xec8>
   87554:	sbfiz	x3, x6, #2, #32
   87558:	add	x2, x19, w0, sxtw #2
   8755c:	cmp	w25, w0
   87560:	b.le	87584 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xf24>
   87564:	whilelt	p0.s, w0, w25
   87568:	add	w0, w0, w6
   8756c:	ld1w	{z0.s}, p0/z, [x2]
   87570:	fmul	z0.s, p0/m, z0.s, z8.s
   87574:	st1w	{z0.s}, p0, [x2]
   87578:	add	x2, x2, x3
   8757c:	cmp	w25, w0
   87580:	b.gt	87564 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xf04>
   87584:	ldr	x0, [x21, #248]
   87588:	mov	x1, x19
   8758c:	add	w20, w20, #0x1
   87590:	add	x22, x22, #0x4
   87594:	add	x19, x19, x26
   87598:	ldr	x2, [sp, #48]
   8759c:	add	x0, x0, x24
   875a0:	bl	1efe0 <memcpy@plt>
   875a4:	ldr	x0, [sp, #416]
   875a8:	add	x24, x24, x0
   875ac:	ldr	w0, [sp, #16]
   875b0:	cmp	w0, w20
   875b4:	b.gt	874d4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xe74>
   875b8:	ldr	w1, [sp, #16]
   875bc:	mov	w22, w25
   875c0:	mov	x19, x23
   875c4:	ldr	w0, [sp, #248]
   875c8:	add	w0, w0, w1
   875cc:	ldr	w1, [sp, #252]
   875d0:	str	w0, [sp, #248]
   875d4:	cmp	w1, w0
   875d8:	b.gt	86a60 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x400>
   875dc:	ldr	d12, [sp, #1408]
   875e0:	ldr	d13, [sp, #1416]
   875e4:	adrp	x0, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   875e8:	ldr	x0, [x0, #3280]
   875ec:	ldr	x2, [sp, #1272]
   875f0:	ldr	x1, [x0]
   875f4:	subs	x2, x2, x1
   875f8:	mov	x1, #0x0                   	// #0
   875fc:	b.ne	87e98 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1838>  // b.any
   87600:	ldr	d8, [sp, #1376]
   87604:	ldr	d9, [sp, #1384]
   87608:	ldr	d10, [sp, #1392]
   8760c:	ldr	d11, [sp, #1400]
   87610:	ldr	d14, [sp, #1424]
   87614:	ldr	d15, [sp, #1432]
   87618:	add	sp, sp, #0x500
   8761c:	ldp	x19, x20, [sp, #16]
   87620:	ldp	x21, x22, [sp, #32]
   87624:	ldp	x23, x24, [sp, #48]
   87628:	ldp	x25, x26, [sp, #64]
   8762c:	ldp	x27, x28, [sp, #80]
   87630:	ldp	x29, x30, [sp], #160
   87634:	ret
   87638:	add	x0, x24, x19
   8763c:	mov	w1, #0x1                   	// #1
   87640:	sturb	w1, [x0, #-1]
   87644:	b	87290 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xc30>
   87648:	fsub	s0, s0, s8
   8764c:	str	x2, [sp, #8]
   87650:	bl	20eb0 <expf@plt>
   87654:	fmov	s10, s0
   87658:	bl	21300 <ggml_cpu_get_sve_cnt@plt>
   8765c:	mov	z2.s, s10
   87660:	lsl	w0, w0, #3
   87664:	ldr	x2, [sp, #8]
   87668:	cmp	w0, #0x0
   8766c:	add	w12, w0, #0x1f
   87670:	csel	w12, w12, w0, lt	// lt = tstop
   87674:	asr	w12, w12, #5
   87678:	neg	w0, w12, lsl #1
   8767c:	lsl	w13, w12, #1
   87680:	ands	w0, w0, w20
   87684:	b.le	876cc <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x106c>
   87688:	sbfiz	x11, x13, #2, #32
   8768c:	mov	x4, x21
   87690:	ptrue	p0.b
   87694:	add	x1, x21, w12, sxtw #2
   87698:	mov	w5, #0x0                   	// #0
   8769c:	nop
   876a0:	ld1w	{z1.s}, p0/z, [x4]
   876a4:	fmul	z1.s, p0/m, z1.s, z2.s
   876a8:	st1w	{z1.s}, p0, [x4]
   876ac:	add	w5, w5, w13
   876b0:	add	x4, x4, x11
   876b4:	ld1w	{z1.s}, p0/z, [x1]
   876b8:	fmul	z1.s, p0/m, z1.s, z2.s
   876bc:	st1w	{z1.s}, p0, [x1]
   876c0:	add	x1, x1, x11
   876c4:	cmp	w0, w5
   876c8:	b.gt	876a0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1040>
   876cc:	sbfiz	x4, x12, #2, #32
   876d0:	add	x1, x21, w0, sxtw #2
   876d4:	cmp	w20, w0
   876d8:	b.le	87700 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x10a0>
   876dc:	nop
   876e0:	whilelt	p0.s, w0, w20
   876e4:	add	w0, w0, w12
   876e8:	ld1w	{z1.s}, p0/z, [x1]
   876ec:	fmul	z1.s, p0/m, z1.s, z2.s
   876f0:	st1w	{z1.s}, p0, [x1]
   876f4:	add	x1, x1, x4
   876f8:	cmp	w20, w0
   876fc:	b.gt	876e0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1080>
   87700:	add	x0, x27, x23
   87704:	ldur	s0, [x0, #-4]
   87708:	fmul	s0, s0, s10
   8770c:	stur	s0, [x0, #-4]
   87710:	b	87260 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xc00>
   87714:	cmp	x18, #0x0
   87718:	b.le	87048 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   8771c:	cmp	x14, #0x6
   87720:	b.ls	87c44 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x15e4>  // b.plast
   87724:	ldr	x0, [sp, #240]
   87728:	mov	x5, x1
   8772c:	str	w12, [sp, #8]
   87730:	stp	x15, x22, [sp, #104]
   87734:	add	x20, x6, x0
   87738:	mov	x0, x6
   8773c:	nop
   87740:	ldr	q0, [x5], #16
   87744:	add	x30, x0, #0x100
   87748:	add	x22, x0, #0x200
   8774c:	add	x15, x0, #0x300
   87750:	add	x12, x0, #0x500
   87754:	add	x11, x0, #0x600
   87758:	fcvtl	v1.4s, v0.4h
   8775c:	fcvtl2	v0.4s, v0.8h
   87760:	str	s1, [x0]
   87764:	st1	{v1.s}[1], [x30]
   87768:	st1	{v1.s}[2], [x22]
   8776c:	st1	{v1.s}[3], [x15]
   87770:	str	s0, [x0, #1024]
   87774:	st1	{v0.s}[1], [x12]
   87778:	add	x12, x0, #0x700
   8777c:	add	x0, x0, #0x800
   87780:	st1	{v0.s}[2], [x11]
   87784:	st1	{v0.s}[3], [x12]
   87788:	cmp	x20, x0
   8778c:	b.ne	87740 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x10e0>  // b.any
   87790:	ldp	x15, x22, [sp, #104]
   87794:	ldr	w12, [sp, #8]
   87798:	cmp	x18, x24
   8779c:	b.eq	87048 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>  // b.none
   877a0:	mov	x0, x24
   877a4:	lsl	x5, x0, #1
   877a8:	add	x11, x7, x0, lsl #6
   877ac:	add	x20, x0, #0x1
   877b0:	ldr	h0, [x1, x5]
   877b4:	fcvt	s0, h0
   877b8:	str	s0, [x10, x11, lsl #2]
   877bc:	cmp	x18, x20
   877c0:	b.le	87048 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   877c4:	add	x5, x1, x5
   877c8:	add	x30, x11, #0x40
   877cc:	add	x20, x0, #0x2
   877d0:	ldr	h0, [x5, #2]
   877d4:	fcvt	s0, h0
   877d8:	str	s0, [x10, x30, lsl #2]
   877dc:	cmp	x18, x20
   877e0:	b.le	87048 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   877e4:	ldr	h0, [x5, #4]
   877e8:	add	x30, x11, #0x80
   877ec:	add	x20, x0, #0x3
   877f0:	fcvt	s0, h0
   877f4:	str	s0, [x10, x30, lsl #2]
   877f8:	cmp	x18, x20
   877fc:	b.le	87048 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   87800:	ldr	h0, [x5, #6]
   87804:	add	x30, x11, #0xc0
   87808:	add	x20, x0, #0x4
   8780c:	fcvt	s0, h0
   87810:	str	s0, [x10, x30, lsl #2]
   87814:	cmp	x18, x20
   87818:	b.le	87048 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   8781c:	ldr	h0, [x5, #8]
   87820:	add	x30, x11, #0x100
   87824:	add	x20, x0, #0x5
   87828:	fcvt	s0, h0
   8782c:	str	s0, [x10, x30, lsl #2]
   87830:	cmp	x18, x20
   87834:	b.le	87048 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   87838:	ldr	h0, [x5, #10]
   8783c:	add	x20, x11, #0x140
   87840:	add	x0, x0, #0x6
   87844:	fcvt	s0, h0
   87848:	str	s0, [x10, x20, lsl #2]
   8784c:	cmp	x18, x0
   87850:	b.le	87048 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   87854:	ldr	h0, [x5, #12]
   87858:	add	x11, x11, #0x180
   8785c:	add	x7, x7, #0x1
   87860:	add	x1, x1, x13
   87864:	add	x2, x2, #0x4
   87868:	add	x6, x6, #0x4
   8786c:	fcvt	s0, h0
   87870:	str	s0, [x10, x11, lsl #2]
   87874:	cmp	w3, w7
   87878:	b.gt	87000 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9a0>
   8787c:	b	87060 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xa00>
   87880:	ldr	x0, [sp, #232]
   87884:	mov	x5, x6
   87888:	add	x11, x1, x0
   8788c:	mov	x0, x1
   87890:	ldp	s3, s2, [x0, #4]
   87894:	ldr	s1, [x0, #12]
   87898:	ldr	s0, [x0], #16
   8789c:	str	s3, [x5, #256]
   878a0:	str	s2, [x5, #512]
   878a4:	str	s1, [x5, #768]
   878a8:	str	s0, [x5]
   878ac:	add	x5, x5, #0x400
   878b0:	cmp	x11, x0
   878b4:	b.ne	87890 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1230>  // b.any
   878b8:	cbz	x17, 87048 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   878bc:	ldr	x0, [sp, #392]
   878c0:	ldr	s0, [x1, x25]
   878c4:	add	x0, x7, x0
   878c8:	str	s0, [x10, x0, lsl #2]
   878cc:	ldr	x0, [sp, #384]
   878d0:	cmp	x18, x0
   878d4:	b.le	87048 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   878d8:	ldr	x0, [sp, #376]
   878dc:	ldr	s0, [x1, x8]
   878e0:	add	x0, x7, x0
   878e4:	str	s0, [x10, x0, lsl #2]
   878e8:	ldr	x0, [sp, #368]
   878ec:	cmp	x18, x0
   878f0:	b.le	87048 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   878f4:	ldr	x0, [sp, #360]
   878f8:	add	x2, x2, #0x4
   878fc:	add	x6, x6, #0x4
   87900:	ldr	s0, [x1, x4]
   87904:	add	x1, x1, x13
   87908:	add	x0, x7, x0
   8790c:	add	x7, x7, #0x1
   87910:	str	s0, [x10, x0, lsl #2]
   87914:	cmp	w3, w7
   87918:	b.gt	87000 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9a0>
   8791c:	b	87060 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xa00>
   87920:	mov	x0, #0x0                   	// #0
   87924:	b	87030 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9d0>
   87928:	mov	w24, w3
   8792c:	mov	x25, x8
   87930:	str	x20, [sp, #8]
   87934:	mov	x22, x2
   87938:	mov	x20, x9
   8793c:	str	x19, [sp, #632]
   87940:	mov	x19, x4
   87944:	stp	x18, x4, [sp, #104]
   87948:	str	x10, [sp, #264]
   8794c:	ldr	s0, [x19]
   87950:	bl	1f000 <tanhf@plt>
   87954:	str	s0, [x19], #4
   87958:	cmp	x20, x19
   8795c:	b.ne	8794c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x12ec>  // b.any
   87960:	ldp	x18, x4, [sp, #104]
   87964:	mov	x9, x20
   87968:	stp	x9, x22, [sp, #104]
   8796c:	ldr	x10, [sp, #264]
   87970:	str	x25, [sp, #264]
   87974:	ldr	x20, [sp, #8]
   87978:	str	w24, [sp, #640]
   8797c:	ldr	x19, [sp, #632]
   87980:	str	x10, [sp, #648]
   87984:	str	x4, [sp, #656]
   87988:	str	x18, [sp, #664]
   8798c:	bl	21300 <ggml_cpu_get_sve_cnt@plt>
   87990:	mov	z1.s, s14
   87994:	lsl	w0, w0, #3
   87998:	ldp	x9, x2, [sp, #104]
   8799c:	add	w6, w0, #0x1f
   879a0:	cmp	w0, #0x0
   879a4:	csel	w0, w6, w0, lt	// lt = tstop
   879a8:	asr	w6, w0, #5
   879ac:	neg	w0, w6, lsl #1
   879b0:	lsl	w7, w6, #1
   879b4:	ldr	x8, [sp, #264]
   879b8:	and	w1, w0, #0x1000
   879bc:	ldr	x10, [sp, #648]
   879c0:	ldr	x4, [sp, #656]
   879c4:	ldr	x18, [sp, #664]
   879c8:	ldr	w3, [sp, #640]
   879cc:	tbz	w0, #12, 87df4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1794>
   879d0:	add	x0, x4, w6, sxtw #2
   879d4:	sbfiz	x11, x7, #2, #32
   879d8:	mov	x1, x4
   879dc:	ptrue	p0.b
   879e0:	mov	w6, #0x0                   	// #0
   879e4:	ld1w	{z0.s}, p0/z, [x1]
   879e8:	fmul	z0.s, p0/m, z0.s, z1.s
   879ec:	st1w	{z0.s}, p0, [x1]
   879f0:	add	w6, w6, w7
   879f4:	add	x1, x1, x11
   879f8:	ld1w	{z0.s}, p0/z, [x0]
   879fc:	fmul	z0.s, p0/m, z0.s, z1.s
   87a00:	st1w	{z0.s}, p0, [x0]
   87a04:	add	x0, x0, x11
   87a08:	cmp	w6, #0xfff
   87a0c:	b.le	879e4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1384>
   87a10:	cmp	x20, #0x3f
   87a14:	b.gt	871bc <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb5c>
   87a18:	mov	w0, #0x40                  	// #64
   87a1c:	ldr	x5, [sp, #128]
   87a20:	mov	w20, #0x3f                  	// #63
   87a24:	mvni	v0.4s, #0x7f, msl #16
   87a28:	sub	w1, w0, w21
   87a2c:	sub	w20, w20, w21
   87a30:	ldr	x0, [sp, #224]
   87a34:	and	w15, w1, #0xfffffff8
   87a38:	cmp	w20, #0x7
   87a3c:	add	w15, w15, w21
   87a40:	lsr	w6, w1, #3
   87a44:	csel	w15, w21, w15, ls	// ls = plast
   87a48:	add	w11, w15, #0x1
   87a4c:	add	w12, w15, #0x2
   87a50:	add	w14, w15, #0x3
   87a54:	add	w16, w15, #0x4
   87a58:	add	w17, w15, #0x5
   87a5c:	add	w22, w15, #0x6
   87a60:	add	x0, x21, x0
   87a64:	add	w24, w15, #0x7
   87a68:	add	x0, x5, x0, lsl #2
   87a6c:	and	w21, w1, #0x7
   87a70:	mov	w1, #0x0                   	// #0
   87a74:	nop
   87a78:	nop
   87a7c:	nop
   87a80:	cmp	w20, #0x7
   87a84:	b.ls	87ad8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1478>  // b.plast
   87a88:	stp	q0, q0, [x0]
   87a8c:	cmp	w6, #0x1
   87a90:	b.eq	87ad4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1474>  // b.none
   87a94:	stp	q0, q0, [x0, #32]
   87a98:	cmp	w6, #0x2
   87a9c:	b.eq	87ad4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1474>  // b.none
   87aa0:	stp	q0, q0, [x0, #64]
   87aa4:	cmp	w6, #0x3
   87aa8:	b.eq	87ad4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1474>  // b.none
   87aac:	stp	q0, q0, [x0, #96]
   87ab0:	cmp	w6, #0x4
   87ab4:	b.eq	87ad4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1474>  // b.none
   87ab8:	stp	q0, q0, [x0, #128]
   87abc:	cmp	w6, #0x5
   87ac0:	b.eq	87ad4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1474>  // b.none
   87ac4:	stp	q0, q0, [x0, #160]
   87ac8:	cmp	w6, #0x7
   87acc:	b.ne	87ad4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1474>  // b.any
   87ad0:	stp	q0, q0, [x0, #192]
   87ad4:	cbz	w21, 87c30 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x15d0>
   87ad8:	add	w5, w1, w15
   87adc:	str	s12, [x4, w5, sxtw #2]
   87ae0:	cmp	w11, #0x40
   87ae4:	b.eq	87b50 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   87ae8:	add	w5, w1, w11
   87aec:	str	s12, [x4, w5, sxtw #2]
   87af0:	cmp	w12, #0x40
   87af4:	b.eq	87b50 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   87af8:	add	w5, w1, w12
   87afc:	str	s12, [x4, w5, sxtw #2]
   87b00:	cmp	w14, #0x40
   87b04:	b.eq	87b50 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   87b08:	add	w5, w1, w14
   87b0c:	str	s12, [x4, w5, sxtw #2]
   87b10:	cmp	w16, #0x40
   87b14:	b.eq	87b50 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   87b18:	add	w5, w1, w16
   87b1c:	str	s12, [x4, w5, sxtw #2]
   87b20:	cmp	w17, #0x40
   87b24:	b.eq	87b50 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   87b28:	add	w5, w1, w17
   87b2c:	str	s12, [x4, w5, sxtw #2]
   87b30:	cmp	w22, #0x40
   87b34:	b.eq	87b50 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   87b38:	add	w5, w1, w22
   87b3c:	str	s12, [x4, w5, sxtw #2]
   87b40:	cmp	w24, #0x40
   87b44:	b.eq	87b50 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   87b48:	add	w5, w1, w24
   87b4c:	str	s12, [x4, w5, sxtw #2]
   87b50:	add	w1, w1, #0x40
   87b54:	add	x0, x0, #0x100
   87b58:	cmp	w1, #0x1, lsl #12
   87b5c:	b.ne	87a80 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1420>  // b.any
   87b60:	ldr	x0, [sp, #192]
   87b64:	cbz	x0, 871c4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb64>
   87b68:	ldr	x5, [sp, #520]
   87b6c:	mov	x0, #0x0                   	// #0
   87b70:	ldr	x1, [sp, #528]
   87b74:	ldr	x6, [sp, #584]
   87b78:	ldr	q0, [x5, x0]
   87b7c:	ldr	q1, [x1, x0]
   87b80:	fadd	v0.4s, v0.4s, v1.4s
   87b84:	str	q0, [x1, x0]
   87b88:	add	x0, x0, #0x10
   87b8c:	cmp	x6, x0
   87b90:	b.ne	87b78 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1518>  // b.any
   87b94:	b	871c4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb64>
   87b98:	ldr	x22, [sp, #168]
   87b9c:	mov	w20, #0x0                   	// #0
   87ba0:	stp	x4, x10, [sp, #104]
   87ba4:	add	x4, sp, #0x278
   87ba8:	ldr	x21, [sp, #56]
   87bac:	stp	x19, x24, [x4]
   87bb0:	ldr	x19, [sp, #160]
   87bb4:	str	x23, [sp, #672]
   87bb8:	mov	x23, x22
   87bbc:	mov	w22, w20
   87bc0:	ldr	x20, [sp, #80]
   87bc4:	mov	x24, x21
   87bc8:	mov	w21, w3
   87bcc:	str	x18, [sp, #8]
   87bd0:	stp	x2, x11, [x4, #16]
   87bd4:	str	x8, [sp, #264]
   87bd8:	str	x5, [sp, #664]
   87bdc:	str	x9, [sp, #680]
   87be0:	ldr	x0, [x20, #248]
   87be4:	mov	x1, x23
   87be8:	add	w22, w22, #0x1
   87bec:	add	x23, x23, x26
   87bf0:	ldr	x2, [sp, #32]
   87bf4:	add	x0, x0, x24
   87bf8:	add	x24, x24, x19
   87bfc:	bl	20900 <ggml_cpu_fp16_to_fp32@plt>
   87c00:	cmp	w21, w22
   87c04:	b.gt	87be0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1580>
   87c08:	add	x1, sp, #0x278
   87c0c:	ldr	x18, [sp, #8]
   87c10:	ldp	x19, x24, [x1]
   87c14:	ldp	x2, x11, [x1, #16]
   87c18:	ldp	x4, x10, [sp, #104]
   87c1c:	ldr	x8, [sp, #264]
   87c20:	ldr	x5, [sp, #664]
   87c24:	ldr	x23, [sp, #672]
   87c28:	ldr	x9, [sp, #680]
   87c2c:	b	8736c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd0c>
   87c30:	add	w1, w1, #0x40
   87c34:	add	x0, x0, #0x100
   87c38:	cmp	w1, #0x1, lsl #12
   87c3c:	b.ne	87a88 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1428>  // b.any
   87c40:	b	871bc <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb5c>
   87c44:	mov	x0, #0x0                   	// #0
   87c48:	b	877a4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1144>
   87c4c:	ldr	x0, [sp, #120]
   87c50:	ldr	w2, [sp, #348]
   87c54:	cmp	w0, w2
   87c58:	b.cs	87dcc <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x176c>  // b.hs, b.nlast
   87c5c:	add	w0, w0, #0x1
   87c60:	ldr	s0, [sp, #604]
   87c64:	ucvtf	s1, w0
   87c68:	bl	20bd0 <powf@plt>
   87c6c:	fmov	s13, s0
   87c70:	b	86aec <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x48c>
   87c74:	sbfiz	x11, x6, #2, #32
   87c78:	mov	x0, x4
   87c7c:	mov	w7, #0x1000                	// #4096
   87c80:	whilelt	p0.s, w1, w7
   87c84:	add	w1, w1, w6
   87c88:	ld1w	{z0.s}, p0/z, [x0]
   87c8c:	fmul	z0.s, p0/m, z0.s, z1.s
   87c90:	st1w	{z0.s}, p0, [x0]
   87c94:	add	x0, x0, x11
   87c98:	cmp	w1, #0xfff
   87c9c:	b.le	87c80 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1620>
   87ca0:	b	871ac <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb4c>
   87ca4:	ldr	x1, [sp, #120]
   87ca8:	mov	x25, #0x1                   	// #1
   87cac:	add	x24, sp, #0x2f0
   87cb0:	ldr	x0, [x0, #248]
   87cb4:	ldr	x21, [sp, #216]
   87cb8:	ldr	s13, [x0, w1, uxtw #2]
   87cbc:	mov	x0, x25
   87cc0:	mov	x25, x21
   87cc4:	mov	x21, x19
   87cc8:	mov	x19, x0
   87ccc:	add	x0, x24, x19, lsl #2
   87cd0:	lsl	x20, x19, #2
   87cd4:	ldur	s0, [x0, #-4]
   87cd8:	fcmpe	s0, s13
   87cdc:	b.mi	87d1c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x16bc>  // b.first
   87ce0:	fsub	s0, s13, s0
   87ce4:	bl	20eb0 <expf@plt>
   87ce8:	fmov	s8, #1.000000000000000000e+00
   87cec:	add	x20, x20, x23
   87cf0:	ldr	w1, [sp, #16]
   87cf4:	add	x19, x19, #0x1
   87cf8:	sub	w0, w19, #0x1
   87cfc:	add	x25, x25, x26
   87d00:	ldur	s1, [x20, #-4]
   87d04:	fmadd	s0, s1, s8, s0
   87d08:	stur	s0, [x20, #-4]
   87d0c:	cmp	w1, w0
   87d10:	b.gt	87ccc <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x166c>
   87d14:	mov	x19, x21
   87d18:	b	87488 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xe28>
   87d1c:	fsub	s0, s0, s13
   87d20:	bl	20eb0 <expf@plt>
   87d24:	fmov	s8, s0
   87d28:	bl	21300 <ggml_cpu_get_sve_cnt@plt>
   87d2c:	mov	z1.s, s8
   87d30:	lsl	w0, w0, #3
   87d34:	cmp	w0, #0x0
   87d38:	add	w4, w0, #0x1f
   87d3c:	csel	w4, w4, w0, lt	// lt = tstop
   87d40:	asr	w4, w4, #5
   87d44:	neg	w0, w4, lsl #1
   87d48:	lsl	w6, w4, #1
   87d4c:	ands	w0, w0, w22
   87d50:	b.le	87d94 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1734>
   87d54:	sbfiz	x5, x6, #2, #32
   87d58:	mov	x2, x25
   87d5c:	ptrue	p0.b
   87d60:	add	x1, x25, w4, sxtw #2
   87d64:	mov	w3, #0x0                   	// #0
   87d68:	ld1w	{z0.s}, p0/z, [x2]
   87d6c:	fmul	z0.s, p0/m, z0.s, z1.s
   87d70:	st1w	{z0.s}, p0, [x2]
   87d74:	add	w3, w3, w6
   87d78:	add	x2, x2, x5
   87d7c:	ld1w	{z0.s}, p0/z, [x1]
   87d80:	fmul	z0.s, p0/m, z0.s, z1.s
   87d84:	st1w	{z0.s}, p0, [x1]
   87d88:	add	x1, x1, x5
   87d8c:	cmp	w0, w3
   87d90:	b.gt	87d68 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1708>
   87d94:	sbfiz	x2, x4, #2, #32
   87d98:	add	x1, x25, w0, sxtw #2
   87d9c:	cmp	w22, w0
   87da0:	b.le	87dc4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1764>
   87da4:	whilelt	p0.s, w0, w22
   87da8:	add	w0, w0, w4
   87dac:	ld1w	{z0.s}, p0/z, [x1]
   87db0:	fmul	z0.s, p0/m, z0.s, z1.s
   87db4:	st1w	{z0.s}, p0, [x1]
   87db8:	add	x1, x1, x2
   87dbc:	cmp	w22, w0
   87dc0:	b.gt	87da4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1744>
   87dc4:	fmov	s0, #1.000000000000000000e+00
   87dc8:	b	87cec <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x168c>
   87dcc:	ldr	w0, [sp, #120]
   87dd0:	ldr	w1, [sp, #348]
   87dd4:	ldr	s0, [sp, #484]
   87dd8:	sub	w0, w0, w1
   87ddc:	lsl	w0, w0, #1
   87de0:	add	w0, w0, #0x1
   87de4:	ucvtf	s1, w0
   87de8:	bl	20bd0 <powf@plt>
   87dec:	fmov	s13, s0
   87df0:	b	86aec <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x48c>
   87df4:	sbfiz	x11, x6, #2, #32
   87df8:	mov	x0, x4
   87dfc:	mov	w7, #0x1000                	// #4096
   87e00:	whilelt	p0.s, w1, w7
   87e04:	add	w1, w1, w6
   87e08:	ld1w	{z0.s}, p0/z, [x0]
   87e0c:	fmul	z0.s, p0/m, z0.s, z1.s
   87e10:	st1w	{z0.s}, p0, [x0]
   87e14:	add	x0, x0, x11
   87e18:	cmp	w1, #0xfff
   87e1c:	b.le	87e00 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x17a0>
   87e20:	b	871b4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb54>
   87e24:	ldr	x2, [sp, #136]
   87e28:	mov	x1, #0x0                   	// #0
   87e2c:	mov	x22, #0x0                   	// #0
   87e30:	stp	xzr, xzr, [sp, #144]
   87e34:	mov	x0, #0x0                   	// #0
   87e38:	mov	x25, #0x0                   	// #0
   87e3c:	str	xzr, [sp, #280]
   87e40:	str	xzr, [sp, #320]
   87e44:	cbnz	x2, 866f8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x98>
   87e48:	ldr	x2, [sp, #80]
   87e4c:	mov	x21, #0x0                   	// #0
   87e50:	mov	x26, #0x0                   	// #0
   87e54:	str	xzr, [sp, #8]
   87e58:	str	xzr, [sp, #40]
   87e5c:	str	xzr, [sp, #88]
   87e60:	str	xzr, [sp, #208]
   87e64:	str	xzr, [sp, #288]
   87e68:	str	xzr, [sp, #328]
   87e6c:	cbnz	x2, 86730 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd0>
   87e70:	mov	x24, #0x0                   	// #0
   87e74:	mov	x20, #0x0                   	// #0
   87e78:	str	xzr, [sp, #32]
   87e7c:	mov	x28, #0x0                   	// #0
   87e80:	str	xzr, [sp, #160]
   87e84:	str	xzr, [sp, #296]
   87e88:	str	xzr, [sp, #336]
   87e8c:	b	86754 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xf4>
   87e90:	fdiv	s10, s10, s14
   87e94:	b	86884 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x224>
   87e98:	str	d12, [sp, #1408]
   87e9c:	str	d13, [sp, #1416]
   87ea0:	bl	1f4c0 <__stack_chk_fail@plt>
   87ea4:	adrp	x0, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   87ea8:	ldr	x0, [x0, #3280]
   87eac:	ldr	x2, [sp, #1272]
   87eb0:	ldr	x1, [x0]
   87eb4:	subs	x2, x2, x1
   87eb8:	mov	x1, #0x0                   	// #0
   87ebc:	b.ne	87ea0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   87ec0:	adrp	x3, f5000 <_fini+0x78c>
   87ec4:	adrp	x2, f4000 <label_14+0x8>
   87ec8:	adrp	x0, f5000 <_fini+0x78c>
   87ecc:	add	x3, x3, #0xf50
   87ed0:	add	x2, x2, #0xa38
   87ed4:	add	x0, x0, #0xb70
   87ed8:	mov	w1, #0x23c9                	// #9161
   87edc:	bl	20fc0 <ggml_abort@plt>
   87ee0:	adrp	x0, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   87ee4:	ldr	x0, [x0, #3280]
   87ee8:	ldr	x2, [sp, #1272]
   87eec:	ldr	x1, [x0]
   87ef0:	subs	x2, x2, x1
   87ef4:	mov	x1, #0x0                   	// #0
   87ef8:	str	d8, [sp, #1376]
   87efc:	str	d9, [sp, #1384]
   87f00:	str	d10, [sp, #1392]
   87f04:	str	d11, [sp, #1400]
   87f08:	str	d12, [sp, #1408]
   87f0c:	str	d13, [sp, #1416]
   87f10:	str	d14, [sp, #1424]
   87f14:	str	d15, [sp, #1432]
   87f18:	b.ne	87ea0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   87f1c:	adrp	x3, f4000 <label_14+0x8>
   87f20:	adrp	x2, f4000 <label_14+0x8>
   87f24:	adrp	x0, f5000 <_fini+0x78c>
   87f28:	add	x3, x3, #0xcf8
   87f2c:	add	x2, x2, #0xa38
   87f30:	add	x0, x0, #0xb70
   87f34:	mov	w1, #0x2399                	// #9113
   87f38:	bl	20fc0 <ggml_abort@plt>
   87f3c:	adrp	x0, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   87f40:	ldr	x0, [x0, #3280]
   87f44:	ldr	x2, [sp, #1272]
   87f48:	ldr	x1, [x0]
   87f4c:	subs	x2, x2, x1
   87f50:	mov	x1, #0x0                   	// #0
   87f54:	str	d8, [sp, #1376]
   87f58:	str	d9, [sp, #1384]
   87f5c:	str	d10, [sp, #1392]
   87f60:	str	d11, [sp, #1400]
   87f64:	str	d12, [sp, #1408]
   87f68:	str	d13, [sp, #1416]
   87f6c:	str	d14, [sp, #1424]
   87f70:	str	d15, [sp, #1432]
   87f74:	b.ne	87ea0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   87f78:	adrp	x3, f4000 <label_14+0x8>
   87f7c:	adrp	x2, f4000 <label_14+0x8>
   87f80:	adrp	x0, f5000 <_fini+0x78c>
   87f84:	add	x3, x3, #0xce8
   87f88:	add	x2, x2, #0xa38
   87f8c:	add	x0, x0, #0xb70
   87f90:	mov	w1, #0x2398                	// #9112
   87f94:	bl	20fc0 <ggml_abort@plt>
   87f98:	adrp	x0, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   87f9c:	ldr	x0, [x0, #3280]
   87fa0:	ldr	x2, [sp, #1272]
   87fa4:	ldr	x1, [x0]
   87fa8:	subs	x2, x2, x1
   87fac:	mov	x1, #0x0                   	// #0
   87fb0:	str	d8, [sp, #1376]
   87fb4:	str	d9, [sp, #1384]
   87fb8:	str	d10, [sp, #1392]
   87fbc:	str	d11, [sp, #1400]
   87fc0:	str	d12, [sp, #1408]
   87fc4:	str	d13, [sp, #1416]
   87fc8:	str	d14, [sp, #1424]
   87fcc:	str	d15, [sp, #1432]
   87fd0:	b.ne	87ea0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   87fd4:	adrp	x3, f5000 <_fini+0x78c>
   87fd8:	adrp	x2, f4000 <label_14+0x8>
   87fdc:	adrp	x0, f5000 <_fini+0x78c>
   87fe0:	add	x3, x3, #0xf38
   87fe4:	add	x2, x2, #0xa38
   87fe8:	add	x0, x0, #0xb70
   87fec:	mov	w1, #0x239b                	// #9115
   87ff0:	bl	20fc0 <ggml_abort@plt>
   87ff4:	adrp	x0, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   87ff8:	ldr	x0, [x0, #3280]
   87ffc:	ldr	x2, [sp, #1272]
   88000:	ldr	x1, [x0]
   88004:	subs	x2, x2, x1
   88008:	mov	x1, #0x0                   	// #0
   8800c:	str	d8, [sp, #1376]
   88010:	str	d9, [sp, #1384]
   88014:	str	d10, [sp, #1392]
   88018:	str	d11, [sp, #1400]
   8801c:	str	d12, [sp, #1408]
   88020:	str	d13, [sp, #1416]
   88024:	str	d14, [sp, #1424]
   88028:	str	d15, [sp, #1432]
   8802c:	b.ne	87ea0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   88030:	adrp	x3, f4000 <label_14+0x8>
   88034:	adrp	x2, f4000 <label_14+0x8>
   88038:	adrp	x0, f5000 <_fini+0x78c>
   8803c:	add	x3, x3, #0xcd8
   88040:	add	x2, x2, #0xa38
   88044:	add	x0, x0, #0xb70
   88048:	mov	w1, #0x2397                	// #9111
   8804c:	bl	20fc0 <ggml_abort@plt>
   88050:	adrp	x0, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   88054:	ldr	x0, [x0, #3280]
   88058:	ldr	x2, [sp, #1272]
   8805c:	ldr	x1, [x0]
   88060:	subs	x2, x2, x1
   88064:	mov	x1, #0x0                   	// #0
   88068:	str	d8, [sp, #1376]
   8806c:	str	d9, [sp, #1384]
   88070:	str	d10, [sp, #1392]
   88074:	str	d11, [sp, #1400]
   88078:	str	d12, [sp, #1408]
   8807c:	str	d13, [sp, #1416]
   88080:	str	d14, [sp, #1424]
   88084:	str	d15, [sp, #1432]
   88088:	b.ne	87ea0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   8808c:	adrp	x3, f4000 <label_14+0x8>
   88090:	adrp	x2, f4000 <label_14+0x8>
   88094:	adrp	x0, f5000 <_fini+0x78c>
   88098:	add	x3, x3, #0xcc0
   8809c:	add	x2, x2, #0xa38
   880a0:	add	x0, x0, #0xb70
   880a4:	mov	w1, #0x2396                	// #9110
   880a8:	bl	20fc0 <ggml_abort@plt>
   880ac:	adrp	x0, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   880b0:	ldr	x0, [x0, #3280]
   880b4:	ldr	x2, [sp, #1272]
   880b8:	ldr	x1, [x0]
   880bc:	subs	x2, x2, x1
   880c0:	mov	x1, #0x0                   	// #0
   880c4:	str	d8, [sp, #1376]
   880c8:	str	d9, [sp, #1384]
   880cc:	str	d10, [sp, #1392]
   880d0:	str	d11, [sp, #1400]
   880d4:	str	d12, [sp, #1408]
   880d8:	str	d13, [sp, #1416]
   880dc:	str	d14, [sp, #1424]
   880e0:	str	d15, [sp, #1432]
   880e4:	b.ne	87ea0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   880e8:	adrp	x3, f5000 <_fini+0x78c>
   880ec:	adrp	x2, f4000 <label_14+0x8>
   880f0:	adrp	x0, f5000 <_fini+0x78c>
   880f4:	add	x3, x3, #0xf28
   880f8:	add	x2, x2, #0xa38
   880fc:	add	x0, x0, #0xb70
   88100:	mov	w1, #0x238f                	// #9103
   88104:	bl	20fc0 <ggml_abort@plt>
   88108:	adrp	x0, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   8810c:	ldr	x0, [x0, #3280]
   88110:	ldr	x2, [sp, #1272]
   88114:	ldr	x1, [x0]
   88118:	subs	x2, x2, x1
   8811c:	mov	x1, #0x0                   	// #0
   88120:	str	d8, [sp, #1376]
   88124:	str	d9, [sp, #1384]
   88128:	str	d10, [sp, #1392]
   8812c:	str	d11, [sp, #1400]
   88130:	str	d12, [sp, #1408]
   88134:	str	d13, [sp, #1416]
   88138:	str	d14, [sp, #1424]
   8813c:	str	d15, [sp, #1432]
   88140:	b.ne	87ea0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   88144:	adrp	x3, f5000 <_fini+0x78c>
   88148:	adrp	x2, f4000 <label_14+0x8>
   8814c:	adrp	x0, f5000 <_fini+0x78c>
   88150:	add	x3, x3, #0xf08
   88154:	add	x2, x2, #0xa38
   88158:	add	x0, x0, #0xb70
   8815c:	mov	w1, #0x238d                	// #9101
   88160:	bl	20fc0 <ggml_abort@plt>
   88164:	adrp	x0, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   88168:	ldr	x0, [x0, #3280]
   8816c:	ldr	x2, [sp, #1272]
   88170:	ldr	x1, [x0]
   88174:	subs	x2, x2, x1
   88178:	mov	x1, #0x0                   	// #0
   8817c:	str	d8, [sp, #1376]
   88180:	str	d9, [sp, #1384]
   88184:	str	d10, [sp, #1392]
   88188:	str	d11, [sp, #1400]
   8818c:	str	d12, [sp, #1408]
   88190:	str	d13, [sp, #1416]
   88194:	str	d14, [sp, #1424]
   88198:	str	d15, [sp, #1432]
   8819c:	b.ne	87ea0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   881a0:	adrp	x3, f5000 <_fini+0x78c>
   881a4:	adrp	x2, f4000 <label_14+0x8>
   881a8:	adrp	x0, f5000 <_fini+0x78c>
   881ac:	add	x3, x3, #0xee8
   881b0:	add	x2, x2, #0xa38
   881b4:	add	x0, x0, #0xb70
   881b8:	mov	w1, #0x238c                	// #9100
   881bc:	bl	20fc0 <ggml_abort@plt>
   881c0:	adrp	x0, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   881c4:	ldr	x0, [x0, #3280]
   881c8:	ldr	x2, [sp, #1272]
   881cc:	ldr	x1, [x0]
   881d0:	subs	x2, x2, x1
   881d4:	mov	x1, #0x0                   	// #0
   881d8:	str	d8, [sp, #1376]
   881dc:	str	d9, [sp, #1384]
   881e0:	str	d10, [sp, #1392]
   881e4:	str	d11, [sp, #1400]
   881e8:	str	d12, [sp, #1408]
   881ec:	str	d13, [sp, #1416]
   881f0:	str	d14, [sp, #1424]
   881f4:	str	d15, [sp, #1432]
   881f8:	b.ne	87ea0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   881fc:	adrp	x3, f5000 <_fini+0x78c>
   88200:	adrp	x2, f4000 <label_14+0x8>
   88204:	adrp	x0, f5000 <_fini+0x78c>
   88208:	add	x3, x3, #0xec8
   8820c:	add	x2, x2, #0xa38
   88210:	add	x0, x0, #0xb70
   88214:	mov	w1, #0x238b                	// #9099
   88218:	bl	20fc0 <ggml_abort@plt>
   8821c:	adrp	x0, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   88220:	ldr	x0, [x0, #3280]
   88224:	ldr	x2, [sp, #1272]
   88228:	ldr	x1, [x0]
   8822c:	subs	x2, x2, x1
   88230:	mov	x1, #0x0                   	// #0
   88234:	str	d8, [sp, #1376]
   88238:	str	d9, [sp, #1384]
   8823c:	str	d10, [sp, #1392]
   88240:	str	d11, [sp, #1400]
   88244:	str	d12, [sp, #1408]
   88248:	str	d13, [sp, #1416]
   8824c:	str	d14, [sp, #1424]
   88250:	str	d15, [sp, #1432]
   88254:	b.ne	87ea0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   88258:	adrp	x3, f5000 <_fini+0x78c>
   8825c:	adrp	x2, f4000 <label_14+0x8>
   88260:	adrp	x0, f5000 <_fini+0x78c>
   88264:	add	x3, x3, #0xeb8
   88268:	add	x2, x2, #0xa38
   8826c:	add	x0, x0, #0xb70
   88270:	mov	w1, #0x2388                	// #9096
   88274:	bl	20fc0 <ggml_abort@plt>
   88278:	adrp	x0, 13f000 <ggml_vec_dot_iq4_xs_q8_K@@Base+0x71820>
   8827c:	ldr	x0, [x0, #3280]
   88280:	ldr	x2, [sp, #1272]
   88284:	ldr	x1, [x0]
   88288:	subs	x2, x2, x1
   8828c:	mov	x1, #0x0                   	// #0
   88290:	str	d8, [sp, #1376]
   88294:	str	d9, [sp, #1384]
   88298:	str	d10, [sp, #1392]
   8829c:	str	d11, [sp, #1400]
   882a0:	str	d12, [sp, #1408]
   882a4:	str	d13, [sp, #1416]
   882a8:	str	d14, [sp, #1424]
   882ac:	str	d15, [sp, #1432]
   882b0:	b.ne	87ea0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   882b4:	adrp	x3, f5000 <_fini+0x78c>
   882b8:	adrp	x2, f4000 <label_14+0x8>
   882bc:	adrp	x0, f5000 <_fini+0x78c>
   882c0:	add	x3, x3, #0xea8
   882c4:	add	x2, x2, #0xa38
   882c8:	add	x0, x0, #0xb70
   882cc:	mov	w1, #0x2387                	// #9095
   882d0:	bl	20fc0 <ggml_abort@plt>
   882d4:	nop
   882d8:	nop
   882dc:	nop
