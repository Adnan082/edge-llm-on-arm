# ===== ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int) =====
   79200:	stp	x29, x30, [sp, #-160]!
   79204:	mov	x29, sp
   79208:	stp	x19, x20, [sp, #16]
   7920c:	stp	x21, x22, [sp, #32]
   79210:	stp	x23, x24, [sp, #48]
   79214:	stp	x25, x26, [sp, #64]
   79218:	stp	x27, x28, [sp, #80]
   7921c:	sub	sp, sp, #0x500
   79220:	str	xzr, [sp, #1024]
   79224:	adrp	x4, 10f000 <type_traits_cpu+0x10>
   79228:	ldr	x4, [x4, #3752]
   7922c:	mov	x5, x1
   79230:	str	x0, [sp, #424]
   79234:	ldr	x0, [x1, #160]
   79238:	stp	w2, w3, [sp, #248]
   7923c:	ldr	x9, [x1, #152]
   79240:	str	x0, [sp, #136]
   79244:	ldr	x0, [x4]
   79248:	str	x0, [sp, #1272]
   7924c:	mov	x0, #0x0                   	// #0
   79250:	ldr	x0, [x1, #168]
   79254:	str	x0, [sp, #80]
   79258:	ldr	x0, [x1, #176]
   7925c:	str	x0, [sp, #192]
   79260:	ldr	x0, [x1, #184]
   79264:	str	x0, [sp, #304]
   79268:	cbz	x9, 7a9c4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x17c4>
   7926c:	ldp	x1, x22, [x9, #32]
   79270:	ldp	x25, x0, [x9, #16]
   79274:	ldr	x2, [x9, #56]
   79278:	stp	x1, x2, [sp, #144]
   7927c:	ldr	x2, [x9, #64]
   79280:	ldr	x1, [x9, #48]
   79284:	str	x2, [sp, #320]
   79288:	ldr	x2, [x9, #72]
   7928c:	str	x2, [sp, #280]
   79290:	ldr	x2, [sp, #136]
   79294:	cbz	x2, 7a9e8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x17e8>
   79298:	ldr	x3, [x2, #16]
   7929c:	ldp	x26, x21, [x2, #32]
   792a0:	str	x3, [sp, #88]
   792a4:	ldr	x3, [x2, #24]
   792a8:	str	x3, [sp, #40]
   792ac:	ldr	x3, [x2, #48]
   792b0:	str	x3, [sp, #8]
   792b4:	ldr	x3, [x2, #56]
   792b8:	str	x3, [sp, #208]
   792bc:	ldp	x3, x2, [x2, #64]
   792c0:	str	x2, [sp, #288]
   792c4:	ldr	x2, [sp, #80]
   792c8:	str	x3, [sp, #328]
   792cc:	cbz	x2, 7aa10 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1810>
   792d0:	ldr	x3, [x2, #16]
   792d4:	ldp	x28, x20, [x2, #32]
   792d8:	str	x3, [sp, #32]
   792dc:	ldr	x3, [x2, #56]
   792e0:	ldr	x24, [x2, #48]
   792e4:	str	x3, [sp, #160]
   792e8:	ldp	x3, x2, [x2, #64]
   792ec:	str	x2, [sp, #296]
   792f0:	str	x3, [sp, #336]
   792f4:	ldp	x2, x3, [x5, #16]
   792f8:	ldp	x19, x23, [x5, #64]
   792fc:	str	x3, [sp, #312]
   79300:	ldr	x3, [x5, #32]
   79304:	ldr	x27, [x5, #48]
   79308:	str	x3, [sp, #200]
   7930c:	ldr	x3, [x5, #56]
   79310:	str	x3, [sp, #48]
   79314:	ldr	x3, [sp, #32]
   79318:	cmp	x2, x3
   7931c:	b.ne	7ae18 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1c18>  // b.any
   79320:	ldr	x2, [sp, #200]
   79324:	cmp	x0, x2
   79328:	b.ne	7adbc <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1bbc>  // b.any
   7932c:	ldr	w0, [x9]
   79330:	stp	x9, x1, [sp, #16]
   79334:	str	x5, [sp, #56]
   79338:	bl	13b70 <ggml_type_size@plt>
   7933c:	ldp	x9, x1, [sp, #16]
   79340:	ldr	x5, [sp, #56]
   79344:	cmp	x1, x0
   79348:	b.ne	7ad60 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1b60>  // b.any
   7934c:	ldr	x0, [sp, #136]
   79350:	stp	x9, x5, [sp, #16]
   79354:	ldr	w0, [x0]
   79358:	bl	13b70 <ggml_type_size@plt>
   7935c:	ldp	x1, x9, [sp, #8]
   79360:	ldr	x5, [sp, #24]
   79364:	cmp	x1, x0
   79368:	b.ne	7ad04 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1b04>  // b.any
   7936c:	ldr	x0, [sp, #80]
   79370:	stp	x9, x5, [sp, #8]
   79374:	ldr	w0, [x0]
   79378:	bl	13b70 <ggml_type_size@plt>
   7937c:	cmp	x24, x0
   79380:	ldp	x9, x5, [sp, #8]
   79384:	b.ne	7aca8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1aa8>  // b.any
   79388:	ldr	x0, [sp, #88]
   7938c:	cmp	x25, x0
   79390:	b.ne	7ac4c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1a4c>  // b.any
   79394:	cmp	x27, #0x4
   79398:	b.ne	7abf0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x19f0>  // b.any
   7939c:	ldr	x0, [sp, #48]
   793a0:	cmp	x0, #0x3
   793a4:	b.ls	7ab94 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1994>  // b.plast
   793a8:	cmp	x0, x19
   793ac:	b.hi	7aadc <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x18dc>  // b.pmore
   793b0:	cmp	x19, x23
   793b4:	b.hi	7aa80 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1880>  // b.pmore
   793b8:	ldr	x0, [sp, #136]
   793bc:	ldr	w1, [x0]
   793c0:	ldr	x0, [sp, #80]
   793c4:	str	w1, [sp, #344]
   793c8:	ldr	w0, [x0]
   793cc:	cmp	w1, w0
   793d0:	b.ne	7ab38 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1938>  // b.any
   793d4:	ldr	x0, [sp, #144]
   793d8:	str	d8, [sp, #1376]
   793dc:	str	d9, [sp, #1384]
   793e0:	str	d10, [sp, #1392]
   793e4:	str	d11, [sp, #1400]
   793e8:	sdiv	x1, x0, x26
   793ec:	str	d14, [sp, #1424]
   793f0:	str	d15, [sp, #1432]
   793f4:	ldr	s14, [x5, #92]
   793f8:	sdiv	x0, x0, x28
   793fc:	ldr	s10, [x5, #84]
   79400:	ldr	w19, [x5, #88]
   79404:	fcmp	s14, #0.0
   79408:	str	x1, [sp, #448]
   7940c:	sdiv	x1, x22, x21
   79410:	str	x0, [sp, #464]
   79414:	sdiv	x0, x22, x20
   79418:	str	x1, [sp, #456]
   7941c:	str	x0, [sp, #472]
   79420:	b.ne	7aa30 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1830>  // b.any
   79424:	ldr	x20, [sp, #144]
   79428:	stp	x9, x5, [sp, #8]
   7942c:	ucvtf	d0, w20
   79430:	bl	146d0 <log2@plt>
   79434:	fmov	d1, d0
   79438:	mov	w1, #0x1                   	// #1
   7943c:	fmov	s11, w19
   79440:	fmov	s0, #2.000000000000000000e+00
   79444:	fcvtmu	w0, d1
   79448:	fneg	s1, s11
   7944c:	lsl	w0, w1, w0
   79450:	fmov	s2, w0
   79454:	str	w0, [sp, #348]
   79458:	ucvtf	s8, s2
   7945c:	fdiv	s1, s1, s8
   79460:	bl	142c0 <powf@plt>
   79464:	fmov	s1, #5.000000000000000000e-01
   79468:	fmov	s15, s0
   7946c:	fmov	s0, #2.000000000000000000e+00
   79470:	fnmul	s1, s1, s11
   79474:	fdiv	s1, s1, s8
   79478:	bl	142c0 <powf@plt>
   7947c:	ldr	x0, [sp, #424]
   79480:	str	s0, [sp, #484]
   79484:	ldr	w1, [sp, #252]
   79488:	ldr	w6, [x0]
   7948c:	ldr	w0, [sp, #248]
   79490:	cmp	w0, w1
   79494:	b.ge	7a184 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xf84>  // b.tcont
   79498:	ldr	x7, [sp, #32]
   7949c:	mov	x2, #0x2010                	// #8208
   794a0:	sxtw	x6, w6
   794a4:	mvni	v9.2s, #0x80, lsl #16
   794a8:	str	d12, [sp, #1408]
   794ac:	mvni	v12.2s, #0x7f, msl #16
   794b0:	ldr	x5, [sp, #88]
   794b4:	str	d13, [sp, #1416]
   794b8:	ldr	x8, [sp, #200]
   794bc:	lsl	x26, x7, #2
   794c0:	mov	w22, w7
   794c4:	sbfiz	x28, x7, #2, #32
   794c8:	add	x0, x7, x5
   794cc:	add	x1, x5, x7, lsl #1
   794d0:	lsr	x4, x5, #2
   794d4:	add	x0, x2, x0, lsl #7
   794d8:	and	x2, x5, #0xfffffffffffffffc
   794dc:	sxtw	x18, w5
   794e0:	add	x9, x2, #0x1
   794e4:	mul	x3, x20, x8
   794e8:	mov	w12, w8
   794ec:	mul	w11, w20, w8
   794f0:	add	x10, x2, #0x2
   794f4:	mov	x19, x18
   794f8:	mul	x0, x0, x6
   794fc:	lsl	x6, x9, #2
   79500:	str	x9, [sp, #384]
   79504:	str	x3, [sp, #432]
   79508:	lsr	x3, x5, #3
   7950c:	str	x6, [sp, #544]
   79510:	lsl	x6, x9, #6
   79514:	ldr	x9, [sp, #312]
   79518:	str	x6, [sp, #376]
   7951c:	ldr	x6, [sp, #48]
   79520:	str	x10, [sp, #368]
   79524:	str	w12, [sp, #480]
   79528:	mul	x8, x8, x9
   7952c:	str	w11, [sp, #600]
   79530:	mul	x6, x6, x9
   79534:	str	x8, [sp, #592]
   79538:	lsl	x8, x2, #2
   7953c:	lsl	x2, x2, #6
   79540:	str	x2, [sp, #392]
   79544:	lsl	x2, x0, #2
   79548:	str	x8, [sp, #552]
   7954c:	add	x8, x0, x5, lsl #6
   79550:	add	x0, x0, x1, lsl #6
   79554:	lsl	x1, x3, #11
   79558:	str	x6, [sp, #416]
   7955c:	lsl	x6, x10, #2
   79560:	str	x2, [sp, #440]
   79564:	lsl	x2, x4, #4
   79568:	add	x0, x0, #0x2, lsl #12
   7956c:	str	x1, [sp, #240]
   79570:	lsl	x1, x5, #8
   79574:	lsl	x0, x0, #2
   79578:	str	x8, [sp, #224]
   7957c:	lsl	x8, x8, #2
   79580:	str	x6, [sp, #536]
   79584:	lsl	x6, x10, #6
   79588:	str	x0, [sp, #560]
   7958c:	lsl	x0, x7, #8
   79590:	str	x2, [sp, #232]
   79594:	str	x0, [sp, #272]
   79598:	lsl	x0, x5, #2
   7959c:	str	x6, [sp, #360]
   795a0:	stp	x1, x0, [sp, #176]
   795a4:	sxtw	x0, w7
   795a8:	add	x1, x8, #0x4, lsl #12
   795ac:	str	x0, [sp, #496]
   795b0:	ldr	x0, [sp, #160]
   795b4:	str	x1, [sp, #512]
   795b8:	lsl	x0, x0, #6
   795bc:	str	x0, [sp, #408]
   795c0:	ldr	x0, [sp, #208]
   795c4:	str	s15, [sp, #604]
   795c8:	fmov	s15, s10
   795cc:	ldr	x9, [sp, #8]
   795d0:	str	x8, [sp, #608]
   795d4:	lsl	x0, x0, #6
   795d8:	str	x0, [sp, #400]
   795dc:	sub	x0, x5, #0x1
   795e0:	mov	x27, x9
   795e4:	str	x0, [sp, #488]
   795e8:	and	x0, x5, #0xfffffffffffffff8
   795ec:	str	x0, [sp, #504]
   795f0:	sbfiz	x0, x5, #2, #32
   795f4:	ldr	x5, [sp, #16]
   795f8:	str	x0, [sp, #576]
   795fc:	str	x5, [sp, #616]
   79600:	ldp	w6, w1, [sp, #248]
   79604:	mov	w5, #0x40                  	// #64
   79608:	ldr	x0, [sp, #432]
   7960c:	ldr	w8, [sp, #600]
   79610:	sxtw	x2, w6
   79614:	sub	w1, w1, w6
   79618:	ldr	w7, [sp, #480]
   7961c:	sdiv	x0, x2, x0
   79620:	sub	w3, w7, w6
   79624:	sxtw	x4, w0
   79628:	mul	w0, w8, w0
   7962c:	ldr	x8, [sp, #144]
   79630:	str	x4, [sp, #64]
   79634:	sub	w6, w6, w0
   79638:	mul	x4, x4, x8
   7963c:	ldr	x8, [sp, #200]
   79640:	msub	x2, x4, x8, x2
   79644:	sdiv	x2, x2, x8
   79648:	str	x2, [sp, #120]
   7964c:	mul	w2, w7, w2
   79650:	add	w0, w0, w2
   79654:	sub	w2, w6, w2
   79658:	add	w0, w0, w3
   7965c:	cmp	w0, w1
   79660:	csel	w0, w0, w1, le
   79664:	str	w0, [sp, #8]
   79668:	cmp	w0, w5
   7966c:	csel	w1, w0, w5, le
   79670:	str	w1, [sp, #16]
   79674:	str	w2, [sp, #24]
   79678:	cmp	w0, #0x0
   7967c:	b.le	7aa44 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1844>
   79680:	fcmpe	s11, #0.0
   79684:	b.gt	7a7ec <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x15ec>
   79688:	fmov	s13, #1.000000000000000000e+00
   7968c:	movi	v0.4s, #0x0
   79690:	mvni	v1.4s, #0x7f, msl #16
   79694:	add	x23, sp, #0x3f8
   79698:	ldr	x4, [sp, #272]
   7969c:	mov	w1, #0x0                   	// #0
   796a0:	stp	q0, q0, [x23]
   796a4:	stp	q0, q0, [x23, #32]
   796a8:	stp	q0, q0, [x23, #64]
   796ac:	stp	q0, q0, [x23, #96]
   796b0:	stp	q0, q0, [x23, #128]
   796b4:	stp	q0, q0, [x23, #160]
   796b8:	stp	q0, q0, [x23, #192]
   796bc:	stp	q1, q1, [sp, #752]
   796c0:	stp	q1, q1, [sp, #784]
   796c4:	stp	q1, q1, [sp, #816]
   796c8:	stp	q1, q1, [sp, #848]
   796cc:	stp	q1, q1, [sp, #880]
   796d0:	stp	q1, q1, [sp, #912]
   796d4:	stp	q1, q1, [sp, #944]
   796d8:	stp	q1, q1, [sp, #976]
   796dc:	stp	q0, q0, [x23, #224]
   796e0:	ldr	x0, [sp, #424]
   796e4:	mov	x2, x4
   796e8:	ldr	x3, [sp, #440]
   796ec:	ldr	x0, [x0, #16]
   796f0:	add	x20, x0, x3
   796f4:	str	x0, [sp, #128]
   796f8:	ldr	x0, [sp, #176]
   796fc:	str	x20, [sp, #352]
   79700:	add	x21, x20, x0
   79704:	add	x3, x21, #0x8, lsl #12
   79708:	add	x24, x21, #0x4, lsl #12
   7970c:	add	x5, x3, x4
   79710:	mov	x0, x3
   79714:	str	x3, [sp, #216]
   79718:	add	x3, x3, x4, lsl #1
   7971c:	str	x24, [sp, #104]
   79720:	mov	x25, x3
   79724:	str	x5, [sp, #168]
   79728:	bl	13580 <memset@plt>
   7972c:	mov	x0, x24
   79730:	mov	x2, #0x4000                	// #16384
   79734:	mov	w1, #0x0                   	// #0
   79738:	bl	13580 <memset@plt>
   7973c:	ldr	x1, [sp, #64]
   79740:	mov	x5, x20
   79744:	mov	w4, #0x0                   	// #0
   79748:	ldp	x3, x2, [sp, #448]
   7974c:	str	x21, [sp, #112]
   79750:	ldrsw	x0, [sp, #120]
   79754:	sdiv	x2, x1, x2
   79758:	str	x19, [sp, #264]
   7975c:	mov	x19, x27
   79760:	mov	x27, x23
   79764:	ldr	x24, [sp, #184]
   79768:	sdiv	x3, x0, x3
   7976c:	str	x0, [sp, #72]
   79770:	str	x2, [sp, #56]
   79774:	ldrsw	x2, [sp, #24]
   79778:	str	x3, [sp, #24]
   7977c:	ldr	x3, [sp, #464]
   79780:	str	x2, [sp, #256]
   79784:	sdiv	x20, x0, x3
   79788:	ldr	x3, [sp, #472]
   7978c:	sdiv	x3, x1, x3
   79790:	mov	x23, x20
   79794:	mov	w20, w4
   79798:	str	x3, [sp, #96]
   7979c:	ldr	x3, [sp, #280]
   797a0:	mul	x3, x1, x3
   797a4:	ldr	x1, [sp, #320]
   797a8:	madd	x3, x0, x1, x3
   797ac:	ldr	x0, [sp, #152]
   797b0:	madd	x3, x0, x2, x3
   797b4:	mov	x21, x3
   797b8:	ldr	x1, [x19, #248]
   797bc:	mov	x0, x5
   797c0:	mov	x2, x24
   797c4:	add	w20, w20, #0x1
   797c8:	add	x1, x1, x21
   797cc:	bl	13010 <memcpy@plt>
   797d0:	add	x5, x0, x24
   797d4:	ldr	x0, [sp, #152]
   797d8:	add	x21, x21, x0
   797dc:	ldr	w0, [sp, #16]
   797e0:	cmp	w0, w20
   797e4:	b.gt	797b8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x5b8>
   797e8:	ldr	w0, [sp, #8]
   797ec:	mov	x20, x23
   797f0:	mov	x23, x27
   797f4:	mov	x27, x19
   797f8:	ldr	x21, [sp, #112]
   797fc:	ldr	x19, [sp, #264]
   79800:	cmp	w0, #0x3f
   79804:	b.gt	79850 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x650>
   79808:	ldr	w4, [sp, #16]
   7980c:	str	x19, [sp, #8]
   79810:	ldr	x0, [sp, #88]
   79814:	ldr	x24, [sp, #184]
   79818:	sxtw	x3, w4
   7981c:	mov	w19, w4
   79820:	mul	x3, x3, x0
   79824:	ldr	x0, [sp, #352]
   79828:	add	x3, x0, x3, lsl #2
   7982c:	mov	x0, x3
   79830:	mov	x2, x24
   79834:	mov	w1, #0x0                   	// #0
   79838:	add	w19, w19, #0x1
   7983c:	bl	13580 <memset@plt>
   79840:	add	x3, x0, x24
   79844:	cmp	w19, #0x40
   79848:	b.ne	7982c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x62c>  // b.any
   7984c:	ldr	x19, [sp, #8]
   79850:	mov	w1, #0x0                   	// #0
   79854:	mov	x0, x25
   79858:	ldr	x2, [sp, #176]
   7985c:	bl	13580 <memset@plt>
   79860:	ldr	x0, [sp, #168]
   79864:	mov	w1, #0x0                   	// #0
   79868:	ldr	x2, [sp, #272]
   7986c:	bl	13580 <memset@plt>
   79870:	ldr	x0, [sp, #40]
   79874:	cmp	x0, #0x0
   79878:	b.le	7a020 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xe20>
   7987c:	ldr	x4, [sp, #288]
   79880:	sxtw	x2, w20
   79884:	mov	x10, x25
   79888:	str	x27, [sp, #624]
   7988c:	mov	w27, w22
   79890:	ldrsw	x1, [sp, #56]
   79894:	ldr	x5, [sp, #560]
   79898:	ldrsw	x0, [sp, #96]
   7989c:	mul	x1, x1, x4
   798a0:	ldr	x4, [sp, #128]
   798a4:	ldrsw	x3, [sp, #24]
   798a8:	str	xzr, [sp, #24]
   798ac:	ldr	x18, [sp, #88]
   798b0:	add	x5, x4, x5
   798b4:	ldr	x9, [sp, #104]
   798b8:	str	x5, [sp, #568]
   798bc:	ldr	x5, [sp, #608]
   798c0:	ldr	x8, [sp, #496]
   798c4:	add	x5, x4, x5
   798c8:	str	x5, [sp, #528]
   798cc:	ldr	x5, [sp, #296]
   798d0:	mul	x0, x0, x5
   798d4:	ldr	x5, [sp, #512]
   798d8:	add	x4, x4, x5
   798dc:	str	x4, [sp, #520]
   798e0:	ldr	x4, [sp, #16]
   798e4:	ubfiz	x4, x4, #8, #26
   798e8:	str	x4, [sp, #584]
   798ec:	ldr	x4, [sp, #328]
   798f0:	madd	x1, x3, x4, x1
   798f4:	mov	x4, x21
   798f8:	str	x1, [sp, #96]
   798fc:	ldr	x1, [sp, #336]
   79900:	madd	x0, x2, x1, x0
   79904:	str	x0, [sp, #56]
   79908:	ldr	x0, [sp, #24]
   7990c:	ldr	x2, [sp, #40]
   79910:	ldr	x6, [sp, #192]
   79914:	sub	x20, x2, x0
   79918:	mov	x0, #0x40                  	// #64
   7991c:	cmp	x20, x0
   79920:	csel	x21, x20, x0, le
   79924:	mov	w3, w21
   79928:	cbz	x6, 79b4c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x94c>
   7992c:	ldr	x5, [sp, #224]
   79930:	sub	w0, w0, w21
   79934:	mov	w22, #0x3f                  	// #63
   79938:	mvni	v1.4s, #0x7f, msl #16
   7993c:	ldp	x11, x2, [x6, #32]
   79940:	and	w15, w0, #0xfffffff8
   79944:	lsr	w14, w0, #3
   79948:	and	w0, w0, #0x7
   7994c:	sub	w22, w22, w21
   79950:	add	w15, w15, w21
   79954:	cmp	w22, #0x7
   79958:	csel	w15, w21, w15, ls	// ls = plast
   7995c:	ldp	x24, x12, [x6, #56]
   79960:	add	w16, w15, #0x1
   79964:	add	w17, w15, #0x2
   79968:	add	x7, x21, x5
   7996c:	add	w25, w15, #0x3
   79970:	add	w30, w15, #0x4
   79974:	add	w13, w15, #0x5
   79978:	str	w0, [sp, #264]
   7997c:	ldr	x5, [sp, #128]
   79980:	str	x12, [sp, #8]
   79984:	add	x7, x5, x7, lsl #2
   79988:	ldr	x5, [x6, #72]
   7998c:	ldr	x6, [x6, #248]
   79990:	stp	x5, x6, [sp, #104]
   79994:	ldr	x5, [sp, #64]
   79998:	ldp	x6, x12, [sp, #64]
   7999c:	sdiv	x1, x5, x2
   799a0:	add	w5, w15, #0x6
   799a4:	sdiv	x0, x12, x11
   799a8:	mov	w12, #0x0                   	// #0
   799ac:	msub	x1, x1, x2, x6
   799b0:	ldr	x6, [sp, #104]
   799b4:	str	w27, [sp, #104]
   799b8:	add	w27, w15, #0x7
   799bc:	ldr	x2, [sp, #72]
   799c0:	mul	x1, x1, x6
   799c4:	ldr	x6, [sp, #8]
   799c8:	str	x26, [sp, #8]
   799cc:	msub	x0, x0, x11, x2
   799d0:	ldr	x2, [sp, #256]
   799d4:	ldr	w26, [sp, #264]
   799d8:	madd	x0, x0, x6, x1
   799dc:	ldr	x1, [sp, #24]
   799e0:	mul	x2, x24, x2
   799e4:	ldr	x6, [sp, #112]
   799e8:	str	x18, [sp, #112]
   799ec:	ldr	w18, [sp, #16]
   799f0:	add	x2, x2, x1, lsl #1
   799f4:	mov	w1, #0x1                   	// #1
   799f8:	add	x0, x0, x2
   799fc:	add	x2, x6, x0
   79a00:	mov	x6, x9
   79a04:	lsl	w11, w12, #6
   79a08:	mov	x0, #0x0                   	// #0
   79a0c:	ldr	h0, [x2, x0, lsl #1]
   79a10:	fcvt	s0, h0
   79a14:	fmul	s0, s0, s13
   79a18:	fcmp	s0, s9
   79a1c:	str	s0, [x6, x0, lsl #2]
   79a20:	add	x0, x0, #0x1
   79a24:	csel	w1, wzr, w1, pl	// pl = nfrst
   79a28:	cmp	w3, w0
   79a2c:	b.gt	79a0c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x80c>
   79a30:	cmp	x20, #0x3f
   79a34:	b.gt	79b24 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>
   79a38:	cmp	w22, #0x7
   79a3c:	b.ls	79aac <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8ac>  // b.plast
   79a40:	str	q1, [x7, #16384]
   79a44:	str	q1, [x7, #16400]
   79a48:	cmp	w14, #0x1
   79a4c:	b.ls	79aa8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8a8>  // b.plast
   79a50:	str	q1, [x7, #16416]
   79a54:	str	q1, [x7, #16432]
   79a58:	cmp	w14, #0x2
   79a5c:	b.eq	79aa8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8a8>  // b.none
   79a60:	str	q1, [x7, #16448]
   79a64:	str	q1, [x7, #16464]
   79a68:	cmp	w14, #0x3
   79a6c:	b.eq	79aa8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8a8>  // b.none
   79a70:	str	q1, [x7, #16480]
   79a74:	str	q1, [x7, #16496]
   79a78:	cmp	w14, #0x4
   79a7c:	b.eq	79aa8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8a8>  // b.none
   79a80:	str	q1, [x7, #16512]
   79a84:	str	q1, [x7, #16528]
   79a88:	cmp	w14, #0x5
   79a8c:	b.eq	79aa8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8a8>  // b.none
   79a90:	str	q1, [x7, #16544]
   79a94:	str	q1, [x7, #16560]
   79a98:	cmp	w14, #0x7
   79a9c:	b.ne	79aa8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x8a8>  // b.any
   79aa0:	str	q1, [x7, #16576]
   79aa4:	str	q1, [x7, #16592]
   79aa8:	cbz	w26, 79b24 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>
   79aac:	add	w0, w11, w15
   79ab0:	str	s12, [x9, w0, sxtw #2]
   79ab4:	cmp	w16, #0x40
   79ab8:	b.eq	79b24 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   79abc:	add	w0, w11, w16
   79ac0:	str	s12, [x9, w0, sxtw #2]
   79ac4:	cmp	w17, #0x40
   79ac8:	b.eq	79b24 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   79acc:	add	w0, w11, w17
   79ad0:	str	s12, [x9, w0, sxtw #2]
   79ad4:	cmp	w25, #0x40
   79ad8:	b.eq	79b24 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   79adc:	add	w0, w11, w25
   79ae0:	str	s12, [x9, w0, sxtw #2]
   79ae4:	cmp	w30, #0x40
   79ae8:	b.eq	79b24 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   79aec:	add	w0, w11, w30
   79af0:	str	s12, [x9, w0, sxtw #2]
   79af4:	cmp	w13, #0x40
   79af8:	b.eq	79b24 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   79afc:	add	w0, w11, w13
   79b00:	str	s12, [x9, w0, sxtw #2]
   79b04:	cmp	w5, #0x40
   79b08:	b.eq	79b24 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   79b0c:	add	w0, w11, w5
   79b10:	str	s12, [x9, w0, sxtw #2]
   79b14:	cmp	w27, #0x40
   79b18:	b.eq	79b24 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x924>  // b.none
   79b1c:	add	w11, w11, w27
   79b20:	str	s12, [x9, w11, sxtw #2]
   79b24:	add	w12, w12, #0x1
   79b28:	add	x7, x7, #0x100
   79b2c:	add	x2, x2, x24
   79b30:	add	x6, x6, #0x100
   79b34:	cmp	w18, w12
   79b38:	b.gt	79a04 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x804>
   79b3c:	ldr	x26, [sp, #8]
   79b40:	ldr	x18, [sp, #112]
   79b44:	ldr	w27, [sp, #104]
   79b48:	tbnz	w1, #0, 79fe0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xde0>
   79b4c:	str	x4, [sp, #264]
   79b50:	mov	x2, x10
   79b54:	mov	x7, #0x0                   	// #0
   79b58:	ldr	x0, [sp, #136]
   79b5c:	and	x17, x18, #0x3
   79b60:	mov	x22, x20
   79b64:	str	x8, [sp, #632]
   79b68:	ldr	x15, [sp, #184]
   79b6c:	ldr	x13, [sp, #208]
   79b70:	ldr	x1, [x0, #248]
   79b74:	ldr	x0, [sp, #176]
   79b78:	ldr	x14, [sp, #488]
   79b7c:	ldr	x24, [sp, #504]
   79b80:	sub	x16, x0, #0xfc
   79b84:	ldr	x0, [sp, #96]
   79b88:	ldr	x4, [sp, #536]
   79b8c:	ldr	x8, [sp, #544]
   79b90:	add	x1, x1, x0
   79b94:	ldr	x25, [sp, #552]
   79b98:	ldr	x6, [sp, #568]
   79b9c:	ldr	w12, [sp, #344]
   79ba0:	cmp	w12, #0x1
   79ba4:	b.eq	7a2b4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x10b4>  // b.none
   79ba8:	cmp	x18, #0x0
   79bac:	b.le	79be8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   79bb0:	cmp	x14, #0x2
   79bb4:	b.ls	7a4c0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x12c0>  // b.plast
   79bb8:	add	x0, x16, x6
   79bbc:	add	x5, x15, x1
   79bc0:	cmp	x1, x0
   79bc4:	mov	x0, #0x0                   	// #0
   79bc8:	ccmp	x6, x5, #0x2, cc	// cc = lo, ul, last
   79bcc:	b.cs	7a420 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1220>  // b.hs, b.nlast
   79bd0:	ldr	s0, [x1, x0, lsl #2]
   79bd4:	lsl	x5, x0, #8
   79bd8:	add	x0, x0, #0x1
   79bdc:	str	s0, [x2, x5]
   79be0:	cmp	x18, x0
   79be4:	b.ne	79bd0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9d0>  // b.any
   79be8:	add	x7, x7, #0x1
   79bec:	add	x1, x1, x13
   79bf0:	add	x2, x2, #0x4
   79bf4:	add	x6, x6, #0x4
   79bf8:	cmp	w3, w7
   79bfc:	b.gt	79ba0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9a0>
   79c00:	ldr	x4, [sp, #264]
   79c04:	mov	x2, #0x4000                	// #16384
   79c08:	mov	w1, #0x0                   	// #0
   79c0c:	str	w3, [sp, #8]
   79c10:	mov	x20, x22
   79c14:	ldr	x8, [sp, #632]
   79c18:	stp	x18, x10, [sp, #104]
   79c1c:	mov	x0, x4
   79c20:	str	x9, [sp, #632]
   79c24:	str	x8, [sp, #264]
   79c28:	bl	13580 <memset@plt>
   79c2c:	ldp	x18, x10, [sp, #104]
   79c30:	mov	x4, x0
   79c34:	mov	x2, x0
   79c38:	mov	x12, x0
   79c3c:	ldr	x8, [sp, #264]
   79c40:	ldr	x7, [sp, #352]
   79c44:	ldr	x1, [sp, #576]
   79c48:	ldr	x9, [sp, #632]
   79c4c:	ldr	w3, [sp, #8]
   79c50:	mov	x5, x10
   79c54:	mov	x6, #0x0                   	// #0
   79c58:	nop
   79c5c:	nop
   79c60:	ldr	s0, [x12, x6, lsl #2]
   79c64:	cmp	x19, #0x0
   79c68:	b.le	79c8c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xa8c>
   79c6c:	mov	x0, #0x0                   	// #0
   79c70:	lsl	x11, x0, #8
   79c74:	ldr	s2, [x7, x0, lsl #2]
   79c78:	add	x0, x0, #0x1
   79c7c:	ldr	s1, [x5, x11]
   79c80:	fmadd	s0, s2, s1, s0
   79c84:	cmp	x0, x19
   79c88:	b.ne	79c70 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xa70>  // b.any
   79c8c:	str	s0, [x12, x6, lsl #2]
   79c90:	add	x6, x6, #0x1
   79c94:	add	x5, x5, #0x4
   79c98:	cmp	x6, #0x40
   79c9c:	b.ne	79c60 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xa60>  // b.any
   79ca0:	add	x12, x12, #0x100
   79ca4:	add	x7, x7, x1
   79ca8:	cmp	x9, x12
   79cac:	b.ne	79c50 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xa50>  // b.any
   79cb0:	str	x9, [sp, #8]
   79cb4:	stp	x2, x8, [sp, #104]
   79cb8:	str	w3, [sp, #264]
   79cbc:	str	x10, [sp, #632]
   79cc0:	str	x4, [sp, #640]
   79cc4:	str	x18, [sp, #648]
   79cc8:	bl	14780 <ggml_cpu_get_sve_cnt@plt>
   79ccc:	mov	z1.s, s15
   79cd0:	lsl	w0, w0, #3
   79cd4:	ldr	x9, [sp, #8]
   79cd8:	add	w6, w0, #0x1f
   79cdc:	cmp	w0, #0x0
   79ce0:	csel	w0, w6, w0, lt	// lt = tstop
   79ce4:	ldp	x2, x8, [sp, #104]
   79ce8:	asr	w6, w0, #5
   79cec:	neg	w0, w6, lsl #1
   79cf0:	lsl	w7, w6, #1
   79cf4:	ldr	x10, [sp, #632]
   79cf8:	and	w1, w0, #0x1000
   79cfc:	ldr	x4, [sp, #640]
   79d00:	ldr	x18, [sp, #648]
   79d04:	ldr	w3, [sp, #264]
   79d08:	tbz	w0, #12, 7a814 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1614>
   79d0c:	add	x0, x4, w6, sxtw #2
   79d10:	sbfiz	x11, x7, #2, #32
   79d14:	mov	x1, x4
   79d18:	ptrue	p0.b
   79d1c:	mov	w6, #0x0                   	// #0
   79d20:	ld1w	{z0.s}, p0/z, [x1]
   79d24:	fmul	z0.s, p0/m, z0.s, z1.s
   79d28:	st1w	{z0.s}, p0, [x1]
   79d2c:	add	w6, w6, w7
   79d30:	add	x1, x1, x11
   79d34:	ld1w	{z0.s}, p0/z, [x0]
   79d38:	fmul	z0.s, p0/m, z0.s, z1.s
   79d3c:	st1w	{z0.s}, p0, [x0]
   79d40:	add	x0, x0, x11
   79d44:	cmp	w6, #0xfff
   79d48:	b.le	79d20 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb20>
   79d4c:	fcmp	s14, #0.0
   79d50:	b.ne	7a4c8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x12c8>  // b.any
   79d54:	cmp	x20, #0x3f
   79d58:	b.le	7a5b8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x13b8>
   79d5c:	ldr	x0, [sp, #192]
   79d60:	cbnz	x0, 7a708 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1508>
   79d64:	ldr	x22, [sp, #216]
   79d68:	add	x24, x4, #0x100
   79d6c:	movi	v0.4s, #0x0
   79d70:	add	x5, sp, #0x2b0
   79d74:	str	x10, [sp, #264]
   79d78:	add	x10, sp, #0x280
   79d7c:	mov	x20, x24
   79d80:	mov	x21, #0x1                   	// #1
   79d84:	add	x25, sp, #0x2f0
   79d88:	stp	x18, x4, [sp, #104]
   79d8c:	stp	x8, x19, [x10]
   79d90:	mov	x19, x5
   79d94:	stp	x24, x2, [x10, #16]
   79d98:	mov	x24, x21
   79d9c:	mov	x21, x22
   79da0:	str	x22, [sp, #672]
   79da4:	mov	x22, x20
   79da8:	mov	w20, w27
   79dac:	stp	q0, q0, [x5]
   79db0:	stp	q0, q0, [x5, #32]
   79db4:	str	w3, [sp, #632]
   79db8:	str	x9, [sp, #680]
   79dbc:	nop
   79dc0:	mvni	v1.2s, #0x7f, msl #16
   79dc4:	sub	x2, x22, #0x100
   79dc8:	mov	x0, x2
   79dcc:	ldr	s0, [x0], #4
   79dd0:	fcmpe	s0, s1
   79dd4:	fcsel	s1, s1, s0, mi	// mi = first
   79dd8:	cmp	x22, x0
   79ddc:	b.ne	79dcc <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xbcc>  // b.any
   79de0:	fcmp	s1, s12
   79de4:	b.eq	7a1d8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xfd8>  // b.none
   79de8:	add	x0, x25, x24, lsl #2
   79dec:	lsl	x27, x24, #2
   79df0:	ldur	s0, [x0, #-4]
   79df4:	fmaxnm	s8, s0, s1
   79df8:	fcmpe	s0, s8
   79dfc:	b.mi	7a1e8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xfe8>  // b.first
   79e00:	add	x4, x25, x27
   79e04:	fmov	s0, s8
   79e08:	mov	x1, x2
   79e0c:	mov	w0, #0x40                  	// #64
   79e10:	stur	s8, [x4, #-4]
   79e14:	bl	13380 <ggml_vec_soft_max_f32@plt>
   79e18:	add	x7, x27, x23
   79e1c:	ldur	s1, [x7, #-4]
   79e20:	fcvt	d1, s1
   79e24:	fadd	d1, d1, d0
   79e28:	fcvt	s1, d1
   79e2c:	stur	s1, [x7, #-4]
   79e30:	add	x24, x24, #0x1
   79e34:	add	x22, x22, #0x100
   79e38:	add	x21, x21, x26
   79e3c:	cmp	x24, #0x41
   79e40:	b.ne	79dc0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xbc0>  // b.any
   79e44:	ldr	w0, [sp, #344]
   79e48:	add	x9, sp, #0x280
   79e4c:	mov	x5, x19
   79e50:	ldp	x8, x19, [x9]
   79e54:	mov	w27, w20
   79e58:	ldp	x24, x2, [x9, #16]
   79e5c:	ldp	x18, x4, [sp, #104]
   79e60:	ldr	x10, [sp, #264]
   79e64:	ldr	x11, [sp, #672]
   79e68:	ldr	x9, [sp, #680]
   79e6c:	ldr	w3, [sp, #632]
   79e70:	cmp	w0, #0x1
   79e74:	b.eq	7a738 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1538>  // b.none
   79e78:	add	x7, sp, #0x278
   79e7c:	ldp	x22, x6, [sp, #160]
   79e80:	mov	w20, #0x0                   	// #0
   79e84:	stp	x19, x24, [x7]
   79e88:	mov	w19, w3
   79e8c:	ldr	x21, [sp, #56]
   79e90:	str	x23, [sp, #672]
   79e94:	mov	w23, w20
   79e98:	mov	x20, x26
   79e9c:	mov	x26, x9
   79ea0:	str	x18, [sp, #8]
   79ea4:	stp	x2, x11, [x7, #16]
   79ea8:	mov	x24, x21
   79eac:	ldr	x21, [sp, #80]
   79eb0:	stp	x4, x10, [sp, #104]
   79eb4:	str	x8, [sp, #264]
   79eb8:	str	x5, [sp, #664]
   79ebc:	ldr	x1, [x21, #248]
   79ec0:	mov	x0, x6
   79ec4:	mov	x2, x20
   79ec8:	add	w23, w23, #0x1
   79ecc:	add	x1, x1, x24
   79ed0:	add	x24, x24, x22
   79ed4:	bl	13010 <memcpy@plt>
   79ed8:	add	x6, x0, x20
   79edc:	cmp	w19, w23
   79ee0:	b.gt	79ebc <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xcbc>
   79ee4:	add	x5, sp, #0x278
   79ee8:	ldr	x18, [sp, #8]
   79eec:	mov	x9, x26
   79ef0:	ldp	x19, x24, [x5]
   79ef4:	mov	x26, x20
   79ef8:	ldp	x2, x11, [x5, #16]
   79efc:	ldp	x4, x10, [sp, #104]
   79f00:	ldr	x8, [sp, #264]
   79f04:	ldr	x5, [sp, #664]
   79f08:	ldr	x23, [sp, #672]
   79f0c:	movi	v0.4s, #0x0
   79f10:	mov	x22, x5
   79f14:	mov	x0, x4
   79f18:	b	79f2c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd2c>
   79f1c:	add	x22, x22, #0x1
   79f20:	add	x0, x0, #0x100
   79f24:	cmp	x25, x22
   79f28:	b.eq	79f64 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd64>  // b.none
   79f2c:	ldrb	w1, [x22]
   79f30:	tbz	w1, #0, 79f1c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd1c>
   79f34:	add	x22, x22, #0x1
   79f38:	stp	q0, q0, [x0]
   79f3c:	stp	q0, q0, [x0, #32]
   79f40:	stp	q0, q0, [x0, #64]
   79f44:	stp	q0, q0, [x0, #96]
   79f48:	stp	q0, q0, [x0, #128]
   79f4c:	stp	q0, q0, [x0, #160]
   79f50:	stp	q0, q0, [x0, #192]
   79f54:	stp	q0, q0, [x0, #224]
   79f58:	add	x0, x0, #0x100
   79f5c:	cmp	x25, x22
   79f60:	b.ne	79f2c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd2c>  // b.any
   79f64:	cmp	x8, #0x0
   79f68:	b.le	79fe0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xde0>
   79f6c:	ldr	x3, [sp, #168]
   79f70:	mov	x0, #0x4100                	// #16640
   79f74:	add	x1, x4, x0
   79f78:	nop
   79f7c:	nop
   79f80:	mov	x6, x3
   79f84:	mov	x5, #0x0                   	// #0
   79f88:	ldr	s0, [x11, x5, lsl #2]
   79f8c:	mov	x7, x6
   79f90:	mov	x0, x2
   79f94:	nop
   79f98:	nop
   79f9c:	nop
   79fa0:	ldr	s1, [x7]
   79fa4:	add	x7, x7, x28
   79fa8:	ldr	s2, [x0], #4
   79fac:	fmadd	s0, s2, s1, s0
   79fb0:	cmp	x24, x0
   79fb4:	b.ne	79fa0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xda0>  // b.any
   79fb8:	str	s0, [x11, x5, lsl #2]
   79fbc:	add	x5, x5, #0x1
   79fc0:	add	x6, x6, #0x4
   79fc4:	cmp	x5, x8
   79fc8:	b.ne	79f88 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd88>  // b.any
   79fcc:	add	x24, x24, #0x100
   79fd0:	add	x11, x11, x28
   79fd4:	add	x2, x2, #0x100
   79fd8:	cmp	x1, x24
   79fdc:	b.ne	79f80 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd80>  // b.any
   79fe0:	ldr	x1, [sp, #56]
   79fe4:	ldr	x2, [sp, #408]
   79fe8:	ldr	x0, [sp, #24]
   79fec:	add	x1, x1, x2
   79ff0:	ldr	x2, [sp, #400]
   79ff4:	str	x1, [sp, #56]
   79ff8:	add	x0, x0, #0x40
   79ffc:	ldr	x1, [sp, #96]
   7a000:	str	x0, [sp, #24]
   7a004:	add	x1, x1, x2
   7a008:	str	x1, [sp, #96]
   7a00c:	ldr	x1, [sp, #40]
   7a010:	cmp	x1, x0
   7a014:	b.gt	79908 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x708>
   7a018:	mov	w22, w27
   7a01c:	ldr	x27, [sp, #624]
   7a020:	ldr	x0, [sp, #304]
   7a024:	cbnz	x0, 7a844 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1644>
   7a028:	ldp	x1, x2, [sp, #64]
   7a02c:	mov	x21, x23
   7a030:	fmov	s13, #1.000000000000000000e+00
   7a034:	mov	w23, #0x0                   	// #0
   7a038:	mov	w20, w23
   7a03c:	mov	x23, x19
   7a040:	ldr	x0, [sp, #592]
   7a044:	ldr	x3, [sp, #312]
   7a048:	madd	x0, x0, x1, x2
   7a04c:	ldr	x2, [sp, #256]
   7a050:	ldr	x1, [sp, #216]
   7a054:	madd	x0, x2, x3, x0
   7a058:	ldr	x2, [sp, #48]
   7a05c:	mov	x19, x1
   7a060:	mul	x25, x0, x2
   7a064:	mov	x24, x25
   7a068:	mov	w25, w22
   7a06c:	mov	x22, x21
   7a070:	ldr	x21, [sp, #616]
   7a074:	movi	v8.2s, #0x0
   7a078:	ldr	s0, [x22]
   7a07c:	fcmp	s0, s8
   7a080:	b.eq	7a088 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xe88>  // b.none
   7a084:	fdiv	s8, s13, s0
   7a088:	bl	14780 <ggml_cpu_get_sve_cnt@plt>
   7a08c:	mov	z8.s, s8
   7a090:	lsl	w0, w0, #3
   7a094:	cmp	w0, #0x0
   7a098:	add	w6, w0, #0x1f
   7a09c:	csel	w6, w6, w0, lt	// lt = tstop
   7a0a0:	asr	w6, w6, #5
   7a0a4:	neg	w0, w6, lsl #1
   7a0a8:	lsl	w7, w6, #1
   7a0ac:	ands	w0, w0, w25
   7a0b0:	b.le	7a0f4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xef4>
   7a0b4:	sbfiz	x5, x7, #2, #32
   7a0b8:	mov	x3, x19
   7a0bc:	ptrue	p0.b
   7a0c0:	add	x2, x19, w6, sxtw #2
   7a0c4:	mov	w4, #0x0                   	// #0
   7a0c8:	ld1w	{z0.s}, p0/z, [x3]
   7a0cc:	fmul	z0.s, p0/m, z0.s, z8.s
   7a0d0:	st1w	{z0.s}, p0, [x3]
   7a0d4:	add	w4, w4, w7
   7a0d8:	add	x3, x3, x5
   7a0dc:	ld1w	{z0.s}, p0/z, [x2]
   7a0e0:	fmul	z0.s, p0/m, z0.s, z8.s
   7a0e4:	st1w	{z0.s}, p0, [x2]
   7a0e8:	add	x2, x2, x5
   7a0ec:	cmp	w0, w4
   7a0f0:	b.gt	7a0c8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xec8>
   7a0f4:	sbfiz	x3, x6, #2, #32
   7a0f8:	add	x2, x19, w0, sxtw #2
   7a0fc:	cmp	w25, w0
   7a100:	b.le	7a124 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xf24>
   7a104:	whilelt	p0.s, w0, w25
   7a108:	add	w0, w0, w6
   7a10c:	ld1w	{z0.s}, p0/z, [x2]
   7a110:	fmul	z0.s, p0/m, z0.s, z8.s
   7a114:	st1w	{z0.s}, p0, [x2]
   7a118:	add	x2, x2, x3
   7a11c:	cmp	w25, w0
   7a120:	b.gt	7a104 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xf04>
   7a124:	ldr	x0, [x21, #248]
   7a128:	mov	x1, x19
   7a12c:	add	w20, w20, #0x1
   7a130:	add	x22, x22, #0x4
   7a134:	add	x19, x19, x26
   7a138:	ldr	x2, [sp, #48]
   7a13c:	add	x0, x0, x24
   7a140:	bl	13010 <memcpy@plt>
   7a144:	ldr	x0, [sp, #416]
   7a148:	add	x24, x24, x0
   7a14c:	ldr	w0, [sp, #16]
   7a150:	cmp	w0, w20
   7a154:	b.gt	7a074 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xe74>
   7a158:	ldr	w1, [sp, #16]
   7a15c:	mov	w22, w25
   7a160:	mov	x19, x23
   7a164:	ldr	w0, [sp, #248]
   7a168:	add	w0, w0, w1
   7a16c:	ldr	w1, [sp, #252]
   7a170:	str	w0, [sp, #248]
   7a174:	cmp	w1, w0
   7a178:	b.gt	79600 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x400>
   7a17c:	ldr	d12, [sp, #1408]
   7a180:	ldr	d13, [sp, #1416]
   7a184:	adrp	x0, 10f000 <type_traits_cpu+0x10>
   7a188:	ldr	x0, [x0, #3752]
   7a18c:	ldr	x2, [sp, #1272]
   7a190:	ldr	x1, [x0]
   7a194:	subs	x2, x2, x1
   7a198:	mov	x1, #0x0                   	// #0
   7a19c:	b.ne	7aa38 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1838>  // b.any
   7a1a0:	ldr	d8, [sp, #1376]
   7a1a4:	ldr	d9, [sp, #1384]
   7a1a8:	ldr	d10, [sp, #1392]
   7a1ac:	ldr	d11, [sp, #1400]
   7a1b0:	ldr	d14, [sp, #1424]
   7a1b4:	ldr	d15, [sp, #1432]
   7a1b8:	add	sp, sp, #0x500
   7a1bc:	ldp	x19, x20, [sp, #16]
   7a1c0:	ldp	x21, x22, [sp, #32]
   7a1c4:	ldp	x23, x24, [sp, #48]
   7a1c8:	ldp	x25, x26, [sp, #64]
   7a1cc:	ldp	x27, x28, [sp, #80]
   7a1d0:	ldp	x29, x30, [sp], #160
   7a1d4:	ret
   7a1d8:	add	x0, x24, x19
   7a1dc:	mov	w1, #0x1                   	// #1
   7a1e0:	sturb	w1, [x0, #-1]
   7a1e4:	b	79e30 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xc30>
   7a1e8:	fsub	s0, s0, s8
   7a1ec:	str	x2, [sp, #8]
   7a1f0:	bl	144b0 <expf@plt>
   7a1f4:	fmov	s10, s0
   7a1f8:	bl	14780 <ggml_cpu_get_sve_cnt@plt>
   7a1fc:	mov	z2.s, s10
   7a200:	lsl	w0, w0, #3
   7a204:	ldr	x2, [sp, #8]
   7a208:	cmp	w0, #0x0
   7a20c:	add	w12, w0, #0x1f
   7a210:	csel	w12, w12, w0, lt	// lt = tstop
   7a214:	asr	w12, w12, #5
   7a218:	neg	w0, w12, lsl #1
   7a21c:	lsl	w13, w12, #1
   7a220:	ands	w0, w0, w20
   7a224:	b.le	7a26c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x106c>
   7a228:	sbfiz	x11, x13, #2, #32
   7a22c:	mov	x4, x21
   7a230:	ptrue	p0.b
   7a234:	add	x1, x21, w12, sxtw #2
   7a238:	mov	w5, #0x0                   	// #0
   7a23c:	nop
   7a240:	ld1w	{z1.s}, p0/z, [x4]
   7a244:	fmul	z1.s, p0/m, z1.s, z2.s
   7a248:	st1w	{z1.s}, p0, [x4]
   7a24c:	add	w5, w5, w13
   7a250:	add	x4, x4, x11
   7a254:	ld1w	{z1.s}, p0/z, [x1]
   7a258:	fmul	z1.s, p0/m, z1.s, z2.s
   7a25c:	st1w	{z1.s}, p0, [x1]
   7a260:	add	x1, x1, x11
   7a264:	cmp	w0, w5
   7a268:	b.gt	7a240 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1040>
   7a26c:	sbfiz	x4, x12, #2, #32
   7a270:	add	x1, x21, w0, sxtw #2
   7a274:	cmp	w20, w0
   7a278:	b.le	7a2a0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x10a0>
   7a27c:	nop
   7a280:	whilelt	p0.s, w0, w20
   7a284:	add	w0, w0, w12
   7a288:	ld1w	{z1.s}, p0/z, [x1]
   7a28c:	fmul	z1.s, p0/m, z1.s, z2.s
   7a290:	st1w	{z1.s}, p0, [x1]
   7a294:	add	x1, x1, x4
   7a298:	cmp	w20, w0
   7a29c:	b.gt	7a280 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1080>
   7a2a0:	add	x0, x27, x23
   7a2a4:	ldur	s0, [x0, #-4]
   7a2a8:	fmul	s0, s0, s10
   7a2ac:	stur	s0, [x0, #-4]
   7a2b0:	b	79e00 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xc00>
   7a2b4:	cmp	x18, #0x0
   7a2b8:	b.le	79be8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   7a2bc:	cmp	x14, #0x6
   7a2c0:	b.ls	7a7e4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x15e4>  // b.plast
   7a2c4:	ldr	x0, [sp, #240]
   7a2c8:	mov	x5, x1
   7a2cc:	str	w12, [sp, #8]
   7a2d0:	stp	x15, x22, [sp, #104]
   7a2d4:	add	x20, x6, x0
   7a2d8:	mov	x0, x6
   7a2dc:	nop
   7a2e0:	ldr	q0, [x5], #16
   7a2e4:	add	x30, x0, #0x100
   7a2e8:	add	x22, x0, #0x200
   7a2ec:	add	x15, x0, #0x300
   7a2f0:	add	x12, x0, #0x500
   7a2f4:	add	x11, x0, #0x600
   7a2f8:	fcvtl	v1.4s, v0.4h
   7a2fc:	fcvtl2	v0.4s, v0.8h
   7a300:	str	s1, [x0]
   7a304:	st1	{v1.s}[1], [x30]
   7a308:	st1	{v1.s}[2], [x22]
   7a30c:	st1	{v1.s}[3], [x15]
   7a310:	str	s0, [x0, #1024]
   7a314:	st1	{v0.s}[1], [x12]
   7a318:	add	x12, x0, #0x700
   7a31c:	add	x0, x0, #0x800
   7a320:	st1	{v0.s}[2], [x11]
   7a324:	st1	{v0.s}[3], [x12]
   7a328:	cmp	x20, x0
   7a32c:	b.ne	7a2e0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x10e0>  // b.any
   7a330:	ldp	x15, x22, [sp, #104]
   7a334:	ldr	w12, [sp, #8]
   7a338:	cmp	x18, x24
   7a33c:	b.eq	79be8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>  // b.none
   7a340:	mov	x0, x24
   7a344:	lsl	x5, x0, #1
   7a348:	add	x11, x7, x0, lsl #6
   7a34c:	add	x20, x0, #0x1
   7a350:	ldr	h0, [x1, x5]
   7a354:	fcvt	s0, h0
   7a358:	str	s0, [x10, x11, lsl #2]
   7a35c:	cmp	x18, x20
   7a360:	b.le	79be8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   7a364:	add	x5, x1, x5
   7a368:	add	x30, x11, #0x40
   7a36c:	add	x20, x0, #0x2
   7a370:	ldr	h0, [x5, #2]
   7a374:	fcvt	s0, h0
   7a378:	str	s0, [x10, x30, lsl #2]
   7a37c:	cmp	x18, x20
   7a380:	b.le	79be8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   7a384:	ldr	h0, [x5, #4]
   7a388:	add	x30, x11, #0x80
   7a38c:	add	x20, x0, #0x3
   7a390:	fcvt	s0, h0
   7a394:	str	s0, [x10, x30, lsl #2]
   7a398:	cmp	x18, x20
   7a39c:	b.le	79be8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   7a3a0:	ldr	h0, [x5, #6]
   7a3a4:	add	x30, x11, #0xc0
   7a3a8:	add	x20, x0, #0x4
   7a3ac:	fcvt	s0, h0
   7a3b0:	str	s0, [x10, x30, lsl #2]
   7a3b4:	cmp	x18, x20
   7a3b8:	b.le	79be8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   7a3bc:	ldr	h0, [x5, #8]
   7a3c0:	add	x30, x11, #0x100
   7a3c4:	add	x20, x0, #0x5
   7a3c8:	fcvt	s0, h0
   7a3cc:	str	s0, [x10, x30, lsl #2]
   7a3d0:	cmp	x18, x20
   7a3d4:	b.le	79be8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   7a3d8:	ldr	h0, [x5, #10]
   7a3dc:	add	x20, x11, #0x140
   7a3e0:	add	x0, x0, #0x6
   7a3e4:	fcvt	s0, h0
   7a3e8:	str	s0, [x10, x20, lsl #2]
   7a3ec:	cmp	x18, x0
   7a3f0:	b.le	79be8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   7a3f4:	ldr	h0, [x5, #12]
   7a3f8:	add	x11, x11, #0x180
   7a3fc:	add	x7, x7, #0x1
   7a400:	add	x1, x1, x13
   7a404:	add	x2, x2, #0x4
   7a408:	add	x6, x6, #0x4
   7a40c:	fcvt	s0, h0
   7a410:	str	s0, [x10, x11, lsl #2]
   7a414:	cmp	w3, w7
   7a418:	b.gt	79ba0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9a0>
   7a41c:	b	79c00 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xa00>
   7a420:	ldr	x0, [sp, #232]
   7a424:	mov	x5, x6
   7a428:	add	x11, x1, x0
   7a42c:	mov	x0, x1
   7a430:	ldp	s3, s2, [x0, #4]
   7a434:	ldr	s1, [x0, #12]
   7a438:	ldr	s0, [x0], #16
   7a43c:	str	s3, [x5, #256]
   7a440:	str	s2, [x5, #512]
   7a444:	str	s1, [x5, #768]
   7a448:	str	s0, [x5]
   7a44c:	add	x5, x5, #0x400
   7a450:	cmp	x11, x0
   7a454:	b.ne	7a430 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1230>  // b.any
   7a458:	cbz	x17, 79be8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   7a45c:	ldr	x0, [sp, #392]
   7a460:	ldr	s0, [x1, x25]
   7a464:	add	x0, x7, x0
   7a468:	str	s0, [x10, x0, lsl #2]
   7a46c:	ldr	x0, [sp, #384]
   7a470:	cmp	x18, x0
   7a474:	b.le	79be8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   7a478:	ldr	x0, [sp, #376]
   7a47c:	ldr	s0, [x1, x8]
   7a480:	add	x0, x7, x0
   7a484:	str	s0, [x10, x0, lsl #2]
   7a488:	ldr	x0, [sp, #368]
   7a48c:	cmp	x18, x0
   7a490:	b.le	79be8 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9e8>
   7a494:	ldr	x0, [sp, #360]
   7a498:	add	x2, x2, #0x4
   7a49c:	add	x6, x6, #0x4
   7a4a0:	ldr	s0, [x1, x4]
   7a4a4:	add	x1, x1, x13
   7a4a8:	add	x0, x7, x0
   7a4ac:	add	x7, x7, #0x1
   7a4b0:	str	s0, [x10, x0, lsl #2]
   7a4b4:	cmp	w3, w7
   7a4b8:	b.gt	79ba0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9a0>
   7a4bc:	b	79c00 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xa00>
   7a4c0:	mov	x0, #0x0                   	// #0
   7a4c4:	b	79bd0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x9d0>
   7a4c8:	mov	w24, w3
   7a4cc:	mov	x25, x8
   7a4d0:	str	x20, [sp, #8]
   7a4d4:	mov	x22, x2
   7a4d8:	mov	x20, x9
   7a4dc:	str	x19, [sp, #632]
   7a4e0:	mov	x19, x4
   7a4e4:	stp	x18, x4, [sp, #104]
   7a4e8:	str	x10, [sp, #264]
   7a4ec:	ldr	s0, [x19]
   7a4f0:	bl	13030 <tanhf@plt>
   7a4f4:	str	s0, [x19], #4
   7a4f8:	cmp	x20, x19
   7a4fc:	b.ne	7a4ec <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x12ec>  // b.any
   7a500:	ldp	x18, x4, [sp, #104]
   7a504:	mov	x9, x20
   7a508:	stp	x9, x22, [sp, #104]
   7a50c:	ldr	x10, [sp, #264]
   7a510:	str	x25, [sp, #264]
   7a514:	ldr	x20, [sp, #8]
   7a518:	str	w24, [sp, #640]
   7a51c:	ldr	x19, [sp, #632]
   7a520:	str	x10, [sp, #648]
   7a524:	str	x4, [sp, #656]
   7a528:	str	x18, [sp, #664]
   7a52c:	bl	14780 <ggml_cpu_get_sve_cnt@plt>
   7a530:	mov	z1.s, s14
   7a534:	lsl	w0, w0, #3
   7a538:	ldp	x9, x2, [sp, #104]
   7a53c:	add	w6, w0, #0x1f
   7a540:	cmp	w0, #0x0
   7a544:	csel	w0, w6, w0, lt	// lt = tstop
   7a548:	asr	w6, w0, #5
   7a54c:	neg	w0, w6, lsl #1
   7a550:	lsl	w7, w6, #1
   7a554:	ldr	x8, [sp, #264]
   7a558:	and	w1, w0, #0x1000
   7a55c:	ldr	x10, [sp, #648]
   7a560:	ldr	x4, [sp, #656]
   7a564:	ldr	x18, [sp, #664]
   7a568:	ldr	w3, [sp, #640]
   7a56c:	tbz	w0, #12, 7a994 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1794>
   7a570:	add	x0, x4, w6, sxtw #2
   7a574:	sbfiz	x11, x7, #2, #32
   7a578:	mov	x1, x4
   7a57c:	ptrue	p0.b
   7a580:	mov	w6, #0x0                   	// #0
   7a584:	ld1w	{z0.s}, p0/z, [x1]
   7a588:	fmul	z0.s, p0/m, z0.s, z1.s
   7a58c:	st1w	{z0.s}, p0, [x1]
   7a590:	add	w6, w6, w7
   7a594:	add	x1, x1, x11
   7a598:	ld1w	{z0.s}, p0/z, [x0]
   7a59c:	fmul	z0.s, p0/m, z0.s, z1.s
   7a5a0:	st1w	{z0.s}, p0, [x0]
   7a5a4:	add	x0, x0, x11
   7a5a8:	cmp	w6, #0xfff
   7a5ac:	b.le	7a584 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1384>
   7a5b0:	cmp	x20, #0x3f
   7a5b4:	b.gt	79d5c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb5c>
   7a5b8:	mov	w0, #0x40                  	// #64
   7a5bc:	ldr	x5, [sp, #128]
   7a5c0:	mov	w20, #0x3f                  	// #63
   7a5c4:	mvni	v0.4s, #0x7f, msl #16
   7a5c8:	sub	w1, w0, w21
   7a5cc:	sub	w20, w20, w21
   7a5d0:	ldr	x0, [sp, #224]
   7a5d4:	and	w15, w1, #0xfffffff8
   7a5d8:	cmp	w20, #0x7
   7a5dc:	add	w15, w15, w21
   7a5e0:	lsr	w6, w1, #3
   7a5e4:	csel	w15, w21, w15, ls	// ls = plast
   7a5e8:	add	w11, w15, #0x1
   7a5ec:	add	w12, w15, #0x2
   7a5f0:	add	w14, w15, #0x3
   7a5f4:	add	w16, w15, #0x4
   7a5f8:	add	w17, w15, #0x5
   7a5fc:	add	w22, w15, #0x6
   7a600:	add	x0, x21, x0
   7a604:	add	w24, w15, #0x7
   7a608:	add	x0, x5, x0, lsl #2
   7a60c:	and	w21, w1, #0x7
   7a610:	mov	w1, #0x0                   	// #0
   7a614:	nop
   7a618:	nop
   7a61c:	nop
   7a620:	cmp	w20, #0x7
   7a624:	b.ls	7a678 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1478>  // b.plast
   7a628:	stp	q0, q0, [x0]
   7a62c:	cmp	w6, #0x1
   7a630:	b.eq	7a674 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1474>  // b.none
   7a634:	stp	q0, q0, [x0, #32]
   7a638:	cmp	w6, #0x2
   7a63c:	b.eq	7a674 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1474>  // b.none
   7a640:	stp	q0, q0, [x0, #64]
   7a644:	cmp	w6, #0x3
   7a648:	b.eq	7a674 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1474>  // b.none
   7a64c:	stp	q0, q0, [x0, #96]
   7a650:	cmp	w6, #0x4
   7a654:	b.eq	7a674 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1474>  // b.none
   7a658:	stp	q0, q0, [x0, #128]
   7a65c:	cmp	w6, #0x5
   7a660:	b.eq	7a674 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1474>  // b.none
   7a664:	stp	q0, q0, [x0, #160]
   7a668:	cmp	w6, #0x7
   7a66c:	b.ne	7a674 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1474>  // b.any
   7a670:	stp	q0, q0, [x0, #192]
   7a674:	cbz	w21, 7a7d0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x15d0>
   7a678:	add	w5, w1, w15
   7a67c:	str	s12, [x4, w5, sxtw #2]
   7a680:	cmp	w11, #0x40
   7a684:	b.eq	7a6f0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   7a688:	add	w5, w1, w11
   7a68c:	str	s12, [x4, w5, sxtw #2]
   7a690:	cmp	w12, #0x40
   7a694:	b.eq	7a6f0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   7a698:	add	w5, w1, w12
   7a69c:	str	s12, [x4, w5, sxtw #2]
   7a6a0:	cmp	w14, #0x40
   7a6a4:	b.eq	7a6f0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   7a6a8:	add	w5, w1, w14
   7a6ac:	str	s12, [x4, w5, sxtw #2]
   7a6b0:	cmp	w16, #0x40
   7a6b4:	b.eq	7a6f0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   7a6b8:	add	w5, w1, w16
   7a6bc:	str	s12, [x4, w5, sxtw #2]
   7a6c0:	cmp	w17, #0x40
   7a6c4:	b.eq	7a6f0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   7a6c8:	add	w5, w1, w17
   7a6cc:	str	s12, [x4, w5, sxtw #2]
   7a6d0:	cmp	w22, #0x40
   7a6d4:	b.eq	7a6f0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   7a6d8:	add	w5, w1, w22
   7a6dc:	str	s12, [x4, w5, sxtw #2]
   7a6e0:	cmp	w24, #0x40
   7a6e4:	b.eq	7a6f0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x14f0>  // b.none
   7a6e8:	add	w5, w1, w24
   7a6ec:	str	s12, [x4, w5, sxtw #2]
   7a6f0:	add	w1, w1, #0x40
   7a6f4:	add	x0, x0, #0x100
   7a6f8:	cmp	w1, #0x1, lsl #12
   7a6fc:	b.ne	7a620 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1420>  // b.any
   7a700:	ldr	x0, [sp, #192]
   7a704:	cbz	x0, 79d64 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb64>
   7a708:	ldr	x5, [sp, #520]
   7a70c:	mov	x0, #0x0                   	// #0
   7a710:	ldr	x1, [sp, #528]
   7a714:	ldr	x6, [sp, #584]
   7a718:	ldr	q0, [x5, x0]
   7a71c:	ldr	q1, [x1, x0]
   7a720:	fadd	v0.4s, v0.4s, v1.4s
   7a724:	str	q0, [x1, x0]
   7a728:	add	x0, x0, #0x10
   7a72c:	cmp	x6, x0
   7a730:	b.ne	7a718 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1518>  // b.any
   7a734:	b	79d64 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb64>
   7a738:	ldr	x22, [sp, #168]
   7a73c:	mov	w20, #0x0                   	// #0
   7a740:	stp	x4, x10, [sp, #104]
   7a744:	add	x4, sp, #0x278
   7a748:	ldr	x21, [sp, #56]
   7a74c:	stp	x19, x24, [x4]
   7a750:	ldr	x19, [sp, #160]
   7a754:	str	x23, [sp, #672]
   7a758:	mov	x23, x22
   7a75c:	mov	w22, w20
   7a760:	ldr	x20, [sp, #80]
   7a764:	mov	x24, x21
   7a768:	mov	w21, w3
   7a76c:	str	x18, [sp, #8]
   7a770:	stp	x2, x11, [x4, #16]
   7a774:	str	x8, [sp, #264]
   7a778:	str	x5, [sp, #664]
   7a77c:	str	x9, [sp, #680]
   7a780:	ldr	x0, [x20, #248]
   7a784:	mov	x1, x23
   7a788:	add	w22, w22, #0x1
   7a78c:	add	x23, x23, x26
   7a790:	ldr	x2, [sp, #32]
   7a794:	add	x0, x0, x24
   7a798:	add	x24, x24, x19
   7a79c:	bl	140d0 <ggml_cpu_fp16_to_fp32@plt>
   7a7a0:	cmp	w21, w22
   7a7a4:	b.gt	7a780 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1580>
   7a7a8:	add	x1, sp, #0x278
   7a7ac:	ldr	x18, [sp, #8]
   7a7b0:	ldp	x19, x24, [x1]
   7a7b4:	ldp	x2, x11, [x1, #16]
   7a7b8:	ldp	x4, x10, [sp, #104]
   7a7bc:	ldr	x8, [sp, #264]
   7a7c0:	ldr	x5, [sp, #664]
   7a7c4:	ldr	x23, [sp, #672]
   7a7c8:	ldr	x9, [sp, #680]
   7a7cc:	b	79f0c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd0c>
   7a7d0:	add	w1, w1, #0x40
   7a7d4:	add	x0, x0, #0x100
   7a7d8:	cmp	w1, #0x1, lsl #12
   7a7dc:	b.ne	7a628 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1428>  // b.any
   7a7e0:	b	79d5c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb5c>
   7a7e4:	mov	x0, #0x0                   	// #0
   7a7e8:	b	7a344 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1144>
   7a7ec:	ldr	x0, [sp, #120]
   7a7f0:	ldr	w2, [sp, #348]
   7a7f4:	cmp	w0, w2
   7a7f8:	b.cs	7a96c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x176c>  // b.hs, b.nlast
   7a7fc:	add	w0, w0, #0x1
   7a800:	ldr	s0, [sp, #604]
   7a804:	ucvtf	s1, w0
   7a808:	bl	142c0 <powf@plt>
   7a80c:	fmov	s13, s0
   7a810:	b	7968c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x48c>
   7a814:	sbfiz	x11, x6, #2, #32
   7a818:	mov	x0, x4
   7a81c:	mov	w7, #0x1000                	// #4096
   7a820:	whilelt	p0.s, w1, w7
   7a824:	add	w1, w1, w6
   7a828:	ld1w	{z0.s}, p0/z, [x0]
   7a82c:	fmul	z0.s, p0/m, z0.s, z1.s
   7a830:	st1w	{z0.s}, p0, [x0]
   7a834:	add	x0, x0, x11
   7a838:	cmp	w1, #0xfff
   7a83c:	b.le	7a820 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1620>
   7a840:	b	79d4c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb4c>
   7a844:	ldr	x1, [sp, #120]
   7a848:	mov	x25, #0x1                   	// #1
   7a84c:	add	x24, sp, #0x2f0
   7a850:	ldr	x0, [x0, #248]
   7a854:	ldr	x21, [sp, #216]
   7a858:	ldr	s13, [x0, w1, uxtw #2]
   7a85c:	mov	x0, x25
   7a860:	mov	x25, x21
   7a864:	mov	x21, x19
   7a868:	mov	x19, x0
   7a86c:	add	x0, x24, x19, lsl #2
   7a870:	lsl	x20, x19, #2
   7a874:	ldur	s0, [x0, #-4]
   7a878:	fcmpe	s0, s13
   7a87c:	b.mi	7a8bc <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x16bc>  // b.first
   7a880:	fsub	s0, s13, s0
   7a884:	bl	144b0 <expf@plt>
   7a888:	fmov	s8, #1.000000000000000000e+00
   7a88c:	add	x20, x20, x23
   7a890:	ldr	w1, [sp, #16]
   7a894:	add	x19, x19, #0x1
   7a898:	sub	w0, w19, #0x1
   7a89c:	add	x25, x25, x26
   7a8a0:	ldur	s1, [x20, #-4]
   7a8a4:	fmadd	s0, s1, s8, s0
   7a8a8:	stur	s0, [x20, #-4]
   7a8ac:	cmp	w1, w0
   7a8b0:	b.gt	7a86c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x166c>
   7a8b4:	mov	x19, x21
   7a8b8:	b	7a028 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xe28>
   7a8bc:	fsub	s0, s0, s13
   7a8c0:	bl	144b0 <expf@plt>
   7a8c4:	fmov	s8, s0
   7a8c8:	bl	14780 <ggml_cpu_get_sve_cnt@plt>
   7a8cc:	mov	z1.s, s8
   7a8d0:	lsl	w0, w0, #3
   7a8d4:	cmp	w0, #0x0
   7a8d8:	add	w4, w0, #0x1f
   7a8dc:	csel	w4, w4, w0, lt	// lt = tstop
   7a8e0:	asr	w4, w4, #5
   7a8e4:	neg	w0, w4, lsl #1
   7a8e8:	lsl	w6, w4, #1
   7a8ec:	ands	w0, w0, w22
   7a8f0:	b.le	7a934 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1734>
   7a8f4:	sbfiz	x5, x6, #2, #32
   7a8f8:	mov	x2, x25
   7a8fc:	ptrue	p0.b
   7a900:	add	x1, x25, w4, sxtw #2
   7a904:	mov	w3, #0x0                   	// #0
   7a908:	ld1w	{z0.s}, p0/z, [x2]
   7a90c:	fmul	z0.s, p0/m, z0.s, z1.s
   7a910:	st1w	{z0.s}, p0, [x2]
   7a914:	add	w3, w3, w6
   7a918:	add	x2, x2, x5
   7a91c:	ld1w	{z0.s}, p0/z, [x1]
   7a920:	fmul	z0.s, p0/m, z0.s, z1.s
   7a924:	st1w	{z0.s}, p0, [x1]
   7a928:	add	x1, x1, x5
   7a92c:	cmp	w0, w3
   7a930:	b.gt	7a908 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1708>
   7a934:	sbfiz	x2, x4, #2, #32
   7a938:	add	x1, x25, w0, sxtw #2
   7a93c:	cmp	w22, w0
   7a940:	b.le	7a964 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1764>
   7a944:	whilelt	p0.s, w0, w22
   7a948:	add	w0, w0, w4
   7a94c:	ld1w	{z0.s}, p0/z, [x1]
   7a950:	fmul	z0.s, p0/m, z0.s, z1.s
   7a954:	st1w	{z0.s}, p0, [x1]
   7a958:	add	x1, x1, x2
   7a95c:	cmp	w22, w0
   7a960:	b.gt	7a944 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1744>
   7a964:	fmov	s0, #1.000000000000000000e+00
   7a968:	b	7a88c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x168c>
   7a96c:	ldr	w0, [sp, #120]
   7a970:	ldr	w1, [sp, #348]
   7a974:	ldr	s0, [sp, #484]
   7a978:	sub	w0, w0, w1
   7a97c:	lsl	w0, w0, #1
   7a980:	add	w0, w0, #0x1
   7a984:	ucvtf	s1, w0
   7a988:	bl	142c0 <powf@plt>
   7a98c:	fmov	s13, s0
   7a990:	b	7968c <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x48c>
   7a994:	sbfiz	x11, x6, #2, #32
   7a998:	mov	x0, x4
   7a99c:	mov	w7, #0x1000                	// #4096
   7a9a0:	whilelt	p0.s, w1, w7
   7a9a4:	add	w1, w1, w6
   7a9a8:	ld1w	{z0.s}, p0/z, [x0]
   7a9ac:	fmul	z0.s, p0/m, z0.s, z1.s
   7a9b0:	st1w	{z0.s}, p0, [x0]
   7a9b4:	add	x0, x0, x11
   7a9b8:	cmp	w1, #0xfff
   7a9bc:	b.le	7a9a0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x17a0>
   7a9c0:	b	79d54 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xb54>
   7a9c4:	ldr	x2, [sp, #136]
   7a9c8:	mov	x1, #0x0                   	// #0
   7a9cc:	mov	x22, #0x0                   	// #0
   7a9d0:	stp	xzr, xzr, [sp, #144]
   7a9d4:	mov	x0, #0x0                   	// #0
   7a9d8:	mov	x25, #0x0                   	// #0
   7a9dc:	str	xzr, [sp, #280]
   7a9e0:	str	xzr, [sp, #320]
   7a9e4:	cbnz	x2, 79298 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x98>
   7a9e8:	ldr	x2, [sp, #80]
   7a9ec:	mov	x21, #0x0                   	// #0
   7a9f0:	mov	x26, #0x0                   	// #0
   7a9f4:	str	xzr, [sp, #8]
   7a9f8:	str	xzr, [sp, #40]
   7a9fc:	str	xzr, [sp, #88]
   7aa00:	str	xzr, [sp, #208]
   7aa04:	str	xzr, [sp, #288]
   7aa08:	str	xzr, [sp, #328]
   7aa0c:	cbnz	x2, 792d0 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xd0>
   7aa10:	mov	x24, #0x0                   	// #0
   7aa14:	mov	x20, #0x0                   	// #0
   7aa18:	str	xzr, [sp, #32]
   7aa1c:	mov	x28, #0x0                   	// #0
   7aa20:	str	xzr, [sp, #160]
   7aa24:	str	xzr, [sp, #296]
   7aa28:	str	xzr, [sp, #336]
   7aa2c:	b	792f4 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0xf4>
   7aa30:	fdiv	s10, s10, s14
   7aa34:	b	79424 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x224>
   7aa38:	str	d12, [sp, #1408]
   7aa3c:	str	d13, [sp, #1416]
   7aa40:	bl	132b0 <__stack_chk_fail@plt>
   7aa44:	adrp	x0, 10f000 <type_traits_cpu+0x10>
   7aa48:	ldr	x0, [x0, #3752]
   7aa4c:	ldr	x2, [sp, #1272]
   7aa50:	ldr	x1, [x0]
   7aa54:	subs	x2, x2, x1
   7aa58:	mov	x1, #0x0                   	// #0
   7aa5c:	b.ne	7aa40 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   7aa60:	adrp	x3, cd000 <_fini+0xd94>
   7aa64:	adrp	x2, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7aa68:	adrp	x0, cd000 <_fini+0xd94>
   7aa6c:	add	x3, x3, #0x930
   7aa70:	add	x2, x2, #0x428
   7aa74:	add	x0, x0, #0x550
   7aa78:	mov	w1, #0x23c9                	// #9161
   7aa7c:	bl	14570 <ggml_abort@plt>
   7aa80:	adrp	x0, 10f000 <type_traits_cpu+0x10>
   7aa84:	ldr	x0, [x0, #3752]
   7aa88:	ldr	x2, [sp, #1272]
   7aa8c:	ldr	x1, [x0]
   7aa90:	subs	x2, x2, x1
   7aa94:	mov	x1, #0x0                   	// #0
   7aa98:	str	d8, [sp, #1376]
   7aa9c:	str	d9, [sp, #1384]
   7aaa0:	str	d10, [sp, #1392]
   7aaa4:	str	d11, [sp, #1400]
   7aaa8:	str	d12, [sp, #1408]
   7aaac:	str	d13, [sp, #1416]
   7aab0:	str	d14, [sp, #1424]
   7aab4:	str	d15, [sp, #1432]
   7aab8:	b.ne	7aa40 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   7aabc:	adrp	x3, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7aac0:	adrp	x2, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7aac4:	adrp	x0, cd000 <_fini+0xd94>
   7aac8:	add	x3, x3, #0x6e8
   7aacc:	add	x2, x2, #0x428
   7aad0:	add	x0, x0, #0x550
   7aad4:	mov	w1, #0x2399                	// #9113
   7aad8:	bl	14570 <ggml_abort@plt>
   7aadc:	adrp	x0, 10f000 <type_traits_cpu+0x10>
   7aae0:	ldr	x0, [x0, #3752]
   7aae4:	ldr	x2, [sp, #1272]
   7aae8:	ldr	x1, [x0]
   7aaec:	subs	x2, x2, x1
   7aaf0:	mov	x1, #0x0                   	// #0
   7aaf4:	str	d8, [sp, #1376]
   7aaf8:	str	d9, [sp, #1384]
   7aafc:	str	d10, [sp, #1392]
   7ab00:	str	d11, [sp, #1400]
   7ab04:	str	d12, [sp, #1408]
   7ab08:	str	d13, [sp, #1416]
   7ab0c:	str	d14, [sp, #1424]
   7ab10:	str	d15, [sp, #1432]
   7ab14:	b.ne	7aa40 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   7ab18:	adrp	x3, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7ab1c:	adrp	x2, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7ab20:	adrp	x0, cd000 <_fini+0xd94>
   7ab24:	add	x3, x3, #0x6d8
   7ab28:	add	x2, x2, #0x428
   7ab2c:	add	x0, x0, #0x550
   7ab30:	mov	w1, #0x2398                	// #9112
   7ab34:	bl	14570 <ggml_abort@plt>
   7ab38:	adrp	x0, 10f000 <type_traits_cpu+0x10>
   7ab3c:	ldr	x0, [x0, #3752]
   7ab40:	ldr	x2, [sp, #1272]
   7ab44:	ldr	x1, [x0]
   7ab48:	subs	x2, x2, x1
   7ab4c:	mov	x1, #0x0                   	// #0
   7ab50:	str	d8, [sp, #1376]
   7ab54:	str	d9, [sp, #1384]
   7ab58:	str	d10, [sp, #1392]
   7ab5c:	str	d11, [sp, #1400]
   7ab60:	str	d12, [sp, #1408]
   7ab64:	str	d13, [sp, #1416]
   7ab68:	str	d14, [sp, #1424]
   7ab6c:	str	d15, [sp, #1432]
   7ab70:	b.ne	7aa40 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   7ab74:	adrp	x3, cd000 <_fini+0xd94>
   7ab78:	adrp	x2, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7ab7c:	adrp	x0, cd000 <_fini+0xd94>
   7ab80:	add	x3, x3, #0x918
   7ab84:	add	x2, x2, #0x428
   7ab88:	add	x0, x0, #0x550
   7ab8c:	mov	w1, #0x239b                	// #9115
   7ab90:	bl	14570 <ggml_abort@plt>
   7ab94:	adrp	x0, 10f000 <type_traits_cpu+0x10>
   7ab98:	ldr	x0, [x0, #3752]
   7ab9c:	ldr	x2, [sp, #1272]
   7aba0:	ldr	x1, [x0]
   7aba4:	subs	x2, x2, x1
   7aba8:	mov	x1, #0x0                   	// #0
   7abac:	str	d8, [sp, #1376]
   7abb0:	str	d9, [sp, #1384]
   7abb4:	str	d10, [sp, #1392]
   7abb8:	str	d11, [sp, #1400]
   7abbc:	str	d12, [sp, #1408]
   7abc0:	str	d13, [sp, #1416]
   7abc4:	str	d14, [sp, #1424]
   7abc8:	str	d15, [sp, #1432]
   7abcc:	b.ne	7aa40 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   7abd0:	adrp	x3, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7abd4:	adrp	x2, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7abd8:	adrp	x0, cd000 <_fini+0xd94>
   7abdc:	add	x3, x3, #0x6c8
   7abe0:	add	x2, x2, #0x428
   7abe4:	add	x0, x0, #0x550
   7abe8:	mov	w1, #0x2397                	// #9111
   7abec:	bl	14570 <ggml_abort@plt>
   7abf0:	adrp	x0, 10f000 <type_traits_cpu+0x10>
   7abf4:	ldr	x0, [x0, #3752]
   7abf8:	ldr	x2, [sp, #1272]
   7abfc:	ldr	x1, [x0]
   7ac00:	subs	x2, x2, x1
   7ac04:	mov	x1, #0x0                   	// #0
   7ac08:	str	d8, [sp, #1376]
   7ac0c:	str	d9, [sp, #1384]
   7ac10:	str	d10, [sp, #1392]
   7ac14:	str	d11, [sp, #1400]
   7ac18:	str	d12, [sp, #1408]
   7ac1c:	str	d13, [sp, #1416]
   7ac20:	str	d14, [sp, #1424]
   7ac24:	str	d15, [sp, #1432]
   7ac28:	b.ne	7aa40 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   7ac2c:	adrp	x3, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7ac30:	adrp	x2, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7ac34:	adrp	x0, cd000 <_fini+0xd94>
   7ac38:	add	x3, x3, #0x6b0
   7ac3c:	add	x2, x2, #0x428
   7ac40:	add	x0, x0, #0x550
   7ac44:	mov	w1, #0x2396                	// #9110
   7ac48:	bl	14570 <ggml_abort@plt>
   7ac4c:	adrp	x0, 10f000 <type_traits_cpu+0x10>
   7ac50:	ldr	x0, [x0, #3752]
   7ac54:	ldr	x2, [sp, #1272]
   7ac58:	ldr	x1, [x0]
   7ac5c:	subs	x2, x2, x1
   7ac60:	mov	x1, #0x0                   	// #0
   7ac64:	str	d8, [sp, #1376]
   7ac68:	str	d9, [sp, #1384]
   7ac6c:	str	d10, [sp, #1392]
   7ac70:	str	d11, [sp, #1400]
   7ac74:	str	d12, [sp, #1408]
   7ac78:	str	d13, [sp, #1416]
   7ac7c:	str	d14, [sp, #1424]
   7ac80:	str	d15, [sp, #1432]
   7ac84:	b.ne	7aa40 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   7ac88:	adrp	x3, cd000 <_fini+0xd94>
   7ac8c:	adrp	x2, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7ac90:	adrp	x0, cd000 <_fini+0xd94>
   7ac94:	add	x3, x3, #0x908
   7ac98:	add	x2, x2, #0x428
   7ac9c:	add	x0, x0, #0x550
   7aca0:	mov	w1, #0x238f                	// #9103
   7aca4:	bl	14570 <ggml_abort@plt>
   7aca8:	adrp	x0, 10f000 <type_traits_cpu+0x10>
   7acac:	ldr	x0, [x0, #3752]
   7acb0:	ldr	x2, [sp, #1272]
   7acb4:	ldr	x1, [x0]
   7acb8:	subs	x2, x2, x1
   7acbc:	mov	x1, #0x0                   	// #0
   7acc0:	str	d8, [sp, #1376]
   7acc4:	str	d9, [sp, #1384]
   7acc8:	str	d10, [sp, #1392]
   7accc:	str	d11, [sp, #1400]
   7acd0:	str	d12, [sp, #1408]
   7acd4:	str	d13, [sp, #1416]
   7acd8:	str	d14, [sp, #1424]
   7acdc:	str	d15, [sp, #1432]
   7ace0:	b.ne	7aa40 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   7ace4:	adrp	x3, cd000 <_fini+0xd94>
   7ace8:	adrp	x2, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7acec:	adrp	x0, cd000 <_fini+0xd94>
   7acf0:	add	x3, x3, #0x8e8
   7acf4:	add	x2, x2, #0x428
   7acf8:	add	x0, x0, #0x550
   7acfc:	mov	w1, #0x238d                	// #9101
   7ad00:	bl	14570 <ggml_abort@plt>
   7ad04:	adrp	x0, 10f000 <type_traits_cpu+0x10>
   7ad08:	ldr	x0, [x0, #3752]
   7ad0c:	ldr	x2, [sp, #1272]
   7ad10:	ldr	x1, [x0]
   7ad14:	subs	x2, x2, x1
   7ad18:	mov	x1, #0x0                   	// #0
   7ad1c:	str	d8, [sp, #1376]
   7ad20:	str	d9, [sp, #1384]
   7ad24:	str	d10, [sp, #1392]
   7ad28:	str	d11, [sp, #1400]
   7ad2c:	str	d12, [sp, #1408]
   7ad30:	str	d13, [sp, #1416]
   7ad34:	str	d14, [sp, #1424]
   7ad38:	str	d15, [sp, #1432]
   7ad3c:	b.ne	7aa40 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   7ad40:	adrp	x3, cd000 <_fini+0xd94>
   7ad44:	adrp	x2, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7ad48:	adrp	x0, cd000 <_fini+0xd94>
   7ad4c:	add	x3, x3, #0x8c8
   7ad50:	add	x2, x2, #0x428
   7ad54:	add	x0, x0, #0x550
   7ad58:	mov	w1, #0x238c                	// #9100
   7ad5c:	bl	14570 <ggml_abort@plt>
   7ad60:	adrp	x0, 10f000 <type_traits_cpu+0x10>
   7ad64:	ldr	x0, [x0, #3752]
   7ad68:	ldr	x2, [sp, #1272]
   7ad6c:	ldr	x1, [x0]
   7ad70:	subs	x2, x2, x1
   7ad74:	mov	x1, #0x0                   	// #0
   7ad78:	str	d8, [sp, #1376]
   7ad7c:	str	d9, [sp, #1384]
   7ad80:	str	d10, [sp, #1392]
   7ad84:	str	d11, [sp, #1400]
   7ad88:	str	d12, [sp, #1408]
   7ad8c:	str	d13, [sp, #1416]
   7ad90:	str	d14, [sp, #1424]
   7ad94:	str	d15, [sp, #1432]
   7ad98:	b.ne	7aa40 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   7ad9c:	adrp	x3, cd000 <_fini+0xd94>
   7ada0:	adrp	x2, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7ada4:	adrp	x0, cd000 <_fini+0xd94>
   7ada8:	add	x3, x3, #0x8a8
   7adac:	add	x2, x2, #0x428
   7adb0:	add	x0, x0, #0x550
   7adb4:	mov	w1, #0x238b                	// #9099
   7adb8:	bl	14570 <ggml_abort@plt>
   7adbc:	adrp	x0, 10f000 <type_traits_cpu+0x10>
   7adc0:	ldr	x0, [x0, #3752]
   7adc4:	ldr	x2, [sp, #1272]
   7adc8:	ldr	x1, [x0]
   7adcc:	subs	x2, x2, x1
   7add0:	mov	x1, #0x0                   	// #0
   7add4:	str	d8, [sp, #1376]
   7add8:	str	d9, [sp, #1384]
   7addc:	str	d10, [sp, #1392]
   7ade0:	str	d11, [sp, #1400]
   7ade4:	str	d12, [sp, #1408]
   7ade8:	str	d13, [sp, #1416]
   7adec:	str	d14, [sp, #1424]
   7adf0:	str	d15, [sp, #1432]
   7adf4:	b.ne	7aa40 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   7adf8:	adrp	x3, cd000 <_fini+0xd94>
   7adfc:	adrp	x2, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7ae00:	adrp	x0, cd000 <_fini+0xd94>
   7ae04:	add	x3, x3, #0x898
   7ae08:	add	x2, x2, #0x428
   7ae0c:	add	x0, x0, #0x550
   7ae10:	mov	w1, #0x2388                	// #9096
   7ae14:	bl	14570 <ggml_abort@plt>
   7ae18:	adrp	x0, 10f000 <type_traits_cpu+0x10>
   7ae1c:	ldr	x0, [x0, #3752]
   7ae20:	ldr	x2, [sp, #1272]
   7ae24:	ldr	x1, [x0]
   7ae28:	subs	x2, x2, x1
   7ae2c:	mov	x1, #0x0                   	// #0
   7ae30:	str	d8, [sp, #1376]
   7ae34:	str	d9, [sp, #1384]
   7ae38:	str	d10, [sp, #1392]
   7ae3c:	str	d11, [sp, #1400]
   7ae40:	str	d12, [sp, #1408]
   7ae44:	str	d13, [sp, #1416]
   7ae48:	str	d14, [sp, #1424]
   7ae4c:	str	d15, [sp, #1432]
   7ae50:	b.ne	7aa40 <ggml_compute_forward_flash_attn_ext_tiled(ggml_compute_params const*, ggml_tensor*, int, int)+0x1840>  // b.any
   7ae54:	adrp	x3, cd000 <_fini+0xd94>
   7ae58:	adrp	x2, cc000 <ggml_gemm_q1_0_4x8_q8_0+0x120>
   7ae5c:	adrp	x0, cd000 <_fini+0xd94>
   7ae60:	add	x3, x3, #0x888
   7ae64:	add	x2, x2, #0x428
   7ae68:	add	x0, x0, #0x550
   7ae6c:	mov	w1, #0x2387                	// #9095
   7ae70:	bl	14570 <ggml_abort@plt>
   7ae74:	nop
   7ae78:	nop
   7ae7c:	nop
