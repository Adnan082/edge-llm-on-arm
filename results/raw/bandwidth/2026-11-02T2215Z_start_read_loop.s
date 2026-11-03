# ===== read_slice_acc8_k1 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000030a0 <read_slice_acc8_k1>:
    30a0:	adrp	x3, 1f000 <__FRAME_END__+0x17970>
    30a4:	ldr	x3, [x3, #4040]
    30a8:	sub	sp, sp, #0xa0
    30ac:	movi	v0.4s, #0x0
    30b0:	mov	x2, sp
    30b4:	stp	x29, x30, [sp, #144]
    30b8:	add	x29, sp, #0x90
    30bc:	ldr	x4, [x3]
    30c0:	str	x4, [sp, #136]
    30c4:	mov	x4, #0x0                   	// #0
    30c8:	stp	q0, q0, [x2]
    30cc:	stp	q0, q0, [x2, #32]
    30d0:	stp	q0, q0, [x2, #64]
    30d4:	stp	q0, q0, [x2, #96]
    30d8:	cbz	x1, 31c0 <read_slice_acc8_k1+0x120>
    30dc:	movi	v0.4s, #0x0
    30e0:	sub	x1, x1, #0x1
    30e4:	add	x2, x0, #0x80
    30e8:	lsr	x1, x1, #4
    30ec:	add	x1, x2, x1, lsl #7
    30f0:	mov	v2.16b, v0.16b
    30f4:	mov	v3.16b, v0.16b
    30f8:	mov	v4.16b, v0.16b
    30fc:	mov	v5.16b, v0.16b
    3100:	mov	v6.16b, v0.16b
    3104:	mov	v7.16b, v0.16b
    3108:	mov	v1.16b, v0.16b
    310c:	ldp	q19, q18, [x0]
    3110:	ldp	q17, q16, [x0, #32]
    3114:	add	v1.2d, v1.2d, v19.2d
    3118:	add	v7.2d, v7.2d, v18.2d
    311c:	ldp	q19, q18, [x0, #64]
    3120:	add	v6.2d, v6.2d, v17.2d
    3124:	add	v5.2d, v5.2d, v16.2d
    3128:	ldp	q17, q16, [x0, #96]
    312c:	add	x0, x0, #0x80
    3130:	add	v4.2d, v4.2d, v19.2d
    3134:	add	v3.2d, v3.2d, v18.2d
    3138:	add	v2.2d, v2.2d, v17.2d
    313c:	add	v0.2d, v0.2d, v16.2d
    3140:	cmp	x0, x1
    3144:	b.ne	310c <read_slice_acc8_k1+0x6c>  // b.any
    3148:	stp	q5, q4, [sp, #48]
    314c:	mov	v4.16b, v5.16b
    3150:	str	q0, [sp, #112]
    3154:	mov	v0.16b, v7.16b
    3158:	stp	q3, q2, [sp, #80]
    315c:	mov	v2.16b, v6.16b
    3160:	stp	q7, q6, [sp, #16]
    3164:	ldp	q3, q5, [sp, #64]
    3168:	add	v0.2d, v0.2d, v2.2d
    316c:	ldr	q2, [sp, #96]
    3170:	adrp	x0, 1f000 <__FRAME_END__+0x17970>
    3174:	ldr	x0, [x0, #4040]
    3178:	add	v3.2d, v3.2d, v4.2d
    317c:	ldr	q4, [sp, #112]
    3180:	add	v2.2d, v2.2d, v5.2d
    3184:	ldr	x2, [sp, #136]
    3188:	ldr	x1, [x0]
    318c:	subs	x2, x2, x1
    3190:	mov	x1, #0x0                   	// #0
    3194:	add	v0.2d, v0.2d, v3.2d
    3198:	add	v1.2d, v1.2d, v4.2d
    319c:	add	v0.2d, v0.2d, v2.2d
    31a0:	add	v0.2d, v0.2d, v1.2d
    31a4:	mov	d1, v0.d[1]
    31a8:	add	d0, d1, d0
    31ac:	fmov	x0, d0
    31b0:	b.ne	31d0 <read_slice_acc8_k1+0x130>  // b.any
    31b4:	ldp	x29, x30, [sp, #144]
    31b8:	add	sp, sp, #0xa0
    31bc:	ret
    31c0:	ldp	q0, q2, [sp, #16]
    31c4:	movi	v1.4s, #0x0
    31c8:	ldr	q4, [sp, #48]
    31cc:	b	3164 <read_slice_acc8_k1+0xc4>
    31d0:	bl	12e0 <__stack_chk_fail@plt>

Disassembly of section .fini:

# ===== read_slice_acc8_k2 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000031e0 <read_slice_acc8_k2>:
    31e0:	adrp	x3, 1f000 <__FRAME_END__+0x17970>
    31e4:	ldr	x3, [x3, #4040]
    31e8:	sub	sp, sp, #0xa0
    31ec:	movi	v0.4s, #0x0
    31f0:	lsr	x1, x1, #1
    31f4:	mov	x2, sp
    31f8:	stp	x29, x30, [sp, #144]
    31fc:	add	x29, sp, #0x90
    3200:	ldr	x4, [x3]
    3204:	str	x4, [sp, #136]
    3208:	mov	x4, #0x0                   	// #0
    320c:	stp	q0, q0, [x2]
    3210:	stp	q0, q0, [x2, #32]
    3214:	stp	q0, q0, [x2, #64]
    3218:	stp	q0, q0, [x2, #96]
    321c:	cbz	x1, 3350 <read_slice_acc8_k2+0x170>
    3220:	movi	v4.4s, #0x0
    3224:	sub	x2, x1, #0x1
    3228:	add	x3, x0, #0x80
    322c:	add	x1, x0, x1, lsl #3
    3230:	lsr	x2, x2, #4
    3234:	add	x2, x3, x2, lsl #7
    3238:	mov	v6.16b, v4.16b
    323c:	mov	v7.16b, v4.16b
    3240:	mov	v16.16b, v4.16b
    3244:	mov	v17.16b, v4.16b
    3248:	mov	v18.16b, v4.16b
    324c:	mov	v19.16b, v4.16b
    3250:	mov	v5.16b, v4.16b
    3254:	nop
    3258:	nop
    325c:	nop
    3260:	ldp	q0, q21, [x1]
    3264:	ldp	q3, q2, [x0]
    3268:	ldr	q20, [x1, #32]
    326c:	ldr	q1, [x0, #32]
    3270:	add	v3.2d, v3.2d, v0.2d
    3274:	add	v2.2d, v2.2d, v21.2d
    3278:	add	v1.2d, v1.2d, v20.2d
    327c:	ldp	q21, q20, [x1, #48]
    3280:	add	v5.2d, v5.2d, v3.2d
    3284:	ldp	q0, q3, [x0, #48]
    3288:	add	v19.2d, v19.2d, v2.2d
    328c:	add	v18.2d, v18.2d, v1.2d
    3290:	ldp	q2, q1, [x0, #80]
    3294:	add	x0, x0, #0x80
    3298:	add	v0.2d, v0.2d, v21.2d
    329c:	add	v3.2d, v3.2d, v20.2d
    32a0:	ldp	q21, q20, [x1, #80]
    32a4:	add	x1, x1, #0x80
    32a8:	add	v17.2d, v17.2d, v0.2d
    32ac:	ldur	q0, [x0, #-16]
    32b0:	add	v16.2d, v16.2d, v3.2d
    32b4:	ldur	q3, [x1, #-16]
    32b8:	add	v2.2d, v2.2d, v21.2d
    32bc:	add	v1.2d, v1.2d, v20.2d
    32c0:	add	v0.2d, v0.2d, v3.2d
    32c4:	add	v7.2d, v7.2d, v2.2d
    32c8:	add	v6.2d, v6.2d, v1.2d
    32cc:	add	v4.2d, v4.2d, v0.2d
    32d0:	cmp	x0, x2
    32d4:	b.ne	3260 <read_slice_acc8_k2+0x80>  // b.any
    32d8:	mov	v0.16b, v19.16b
    32dc:	mov	v1.16b, v18.16b
    32e0:	str	q4, [sp, #112]
    32e4:	mov	v3.16b, v17.16b
    32e8:	mov	v2.16b, v16.16b
    32ec:	mov	v4.16b, v7.16b
    32f0:	stp	q19, q18, [sp, #16]
    32f4:	stp	q17, q16, [sp, #48]
    32f8:	stp	q7, q6, [sp, #80]
    32fc:	add	v0.2d, v0.2d, v1.2d
    3300:	add	v2.2d, v2.2d, v3.2d
    3304:	adrp	x0, 1f000 <__FRAME_END__+0x17970>
    3308:	ldr	x0, [x0, #4040]
    330c:	ldp	q1, q3, [sp, #96]
    3310:	add	v0.2d, v0.2d, v2.2d
    3314:	ldr	x2, [sp, #136]
    3318:	ldr	x1, [x0]
    331c:	subs	x2, x2, x1
    3320:	mov	x1, #0x0                   	// #0
    3324:	add	v1.2d, v1.2d, v4.2d
    3328:	add	v5.2d, v5.2d, v3.2d
    332c:	add	v0.2d, v0.2d, v1.2d
    3330:	add	v0.2d, v0.2d, v5.2d
    3334:	mov	d1, v0.d[1]
    3338:	add	d0, d1, d0
    333c:	fmov	x0, d0
    3340:	b.ne	3364 <read_slice_acc8_k2+0x184>  // b.any
    3344:	ldp	x29, x30, [sp, #144]
    3348:	add	sp, sp, #0xa0
    334c:	ret
    3350:	ldp	q0, q1, [sp, #16]
    3354:	movi	v5.4s, #0x0
    3358:	ldp	q3, q2, [sp, #48]
    335c:	ldr	q4, [sp, #80]
    3360:	b	32fc <read_slice_acc8_k2+0x11c>
    3364:	bl	12e0 <__stack_chk_fail@plt>

Disassembly of section .fini:

# ===== read_slice_acc8_k4 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003368 <read_slice_acc8_k4>:
    3368:	adrp	x3, 1f000 <__FRAME_END__+0x17970>
    336c:	ldr	x3, [x3, #4040]
    3370:	sub	sp, sp, #0xa0
    3374:	movi	v0.4s, #0x0
    3378:	lsr	x1, x1, #2
    337c:	mov	x2, sp
    3380:	stp	x29, x30, [sp, #144]
    3384:	add	x29, sp, #0x90
    3388:	ldr	x4, [x3]
    338c:	str	x4, [sp, #136]
    3390:	mov	x4, #0x0                   	// #0
    3394:	stp	q0, q0, [x2]
    3398:	stp	q0, q0, [x2, #32]
    339c:	stp	q0, q0, [x2, #64]
    33a0:	stp	q0, q0, [x2, #96]
    33a4:	cbz	x1, 3554 <read_slice_acc8_k4+0x1ec>
    33a8:	movi	v3.4s, #0x0
    33ac:	add	x2, x0, x1, lsl #4
    33b0:	sub	x4, x1, #0x1
    33b4:	add	x3, x0, #0x80
    33b8:	lsr	x4, x4, #4
    33bc:	add	x4, x3, x4, lsl #7
    33c0:	add	x3, x2, x1, lsl #3
    33c4:	mov	v5.16b, v3.16b
    33c8:	mov	v6.16b, v3.16b
    33cc:	add	x1, x0, x1, lsl #3
    33d0:	mov	v7.16b, v3.16b
    33d4:	mov	v16.16b, v3.16b
    33d8:	mov	v17.16b, v3.16b
    33dc:	mov	v18.16b, v3.16b
    33e0:	mov	v4.16b, v3.16b
    33e4:	ldp	q19, q21, [x1]
    33e8:	ldp	q1, q0, [x0]
    33ec:	ldp	q2, q22, [x3]
    33f0:	add	x3, x3, #0x80
    33f4:	add	v1.2d, v1.2d, v19.2d
    33f8:	ldp	q20, q19, [x2]
    33fc:	add	v0.2d, v0.2d, v21.2d
    3400:	ldr	q21, [x1, #32]
    3404:	add	v20.2d, v20.2d, v2.2d
    3408:	add	v19.2d, v19.2d, v22.2d
    340c:	ldur	q22, [x3, #-96]
    3410:	add	v1.2d, v1.2d, v20.2d
    3414:	add	v0.2d, v0.2d, v19.2d
    3418:	ldp	q20, q19, [x2, #32]
    341c:	add	v4.2d, v4.2d, v1.2d
    3420:	ldp	q2, q1, [x0, #32]
    3424:	add	x0, x0, #0x80
    3428:	add	v18.2d, v18.2d, v0.2d
    342c:	ldur	q0, [x0, #-64]
    3430:	add	v20.2d, v20.2d, v22.2d
    3434:	ldur	q22, [x3, #-80]
    3438:	add	v2.2d, v2.2d, v21.2d
    343c:	ldr	q21, [x1, #48]
    3440:	add	v19.2d, v19.2d, v22.2d
    3444:	ldur	q22, [x3, #-64]
    3448:	add	v2.2d, v2.2d, v20.2d
    344c:	ldr	q20, [x2, #64]
    3450:	add	v1.2d, v1.2d, v21.2d
    3454:	ldr	q21, [x1, #64]
    3458:	add	v17.2d, v17.2d, v2.2d
    345c:	ldur	q2, [x0, #-48]
    3460:	add	v1.2d, v1.2d, v19.2d
    3464:	add	v20.2d, v20.2d, v22.2d
    3468:	ldur	q22, [x3, #-48]
    346c:	add	v0.2d, v0.2d, v21.2d
    3470:	ldr	q21, [x1, #80]
    3474:	add	v16.2d, v16.2d, v1.2d
    3478:	ldp	q19, q1, [x2, #80]
    347c:	add	x2, x2, #0x80
    3480:	add	v0.2d, v0.2d, v20.2d
    3484:	ldur	q20, [x0, #-32]
    3488:	add	v2.2d, v2.2d, v21.2d
    348c:	ldur	q21, [x3, #-32]
    3490:	add	v7.2d, v7.2d, v0.2d
    3494:	ldur	q0, [x2, #-16]
    3498:	add	v19.2d, v19.2d, v22.2d
    349c:	add	v1.2d, v1.2d, v21.2d
    34a0:	ldur	q21, [x3, #-16]
    34a4:	add	v2.2d, v2.2d, v19.2d
    34a8:	ldur	q19, [x0, #-16]
    34ac:	add	v0.2d, v0.2d, v21.2d
    34b0:	add	v6.2d, v6.2d, v2.2d
    34b4:	ldp	q22, q2, [x1, #96]
    34b8:	add	x1, x1, #0x80
    34bc:	add	v20.2d, v20.2d, v22.2d
    34c0:	add	v2.2d, v19.2d, v2.2d
    34c4:	add	v1.2d, v1.2d, v20.2d
    34c8:	add	v0.2d, v0.2d, v2.2d
    34cc:	add	v5.2d, v5.2d, v1.2d
    34d0:	add	v3.2d, v3.2d, v0.2d
    34d4:	cmp	x0, x4
    34d8:	b.ne	33e4 <read_slice_acc8_k4+0x7c>  // b.any
    34dc:	mov	v0.16b, v18.16b
    34e0:	mov	v1.16b, v17.16b
    34e4:	str	q3, [sp, #112]
    34e8:	mov	v2.16b, v7.16b
    34ec:	mov	v3.16b, v16.16b
    34f0:	stp	q6, q5, [sp, #80]
    34f4:	mov	v5.16b, v6.16b
    34f8:	stp	q18, q17, [sp, #16]
    34fc:	stp	q16, q7, [sp, #48]
    3500:	add	v0.2d, v0.2d, v1.2d
    3504:	add	v2.2d, v2.2d, v3.2d
    3508:	adrp	x0, 1f000 <__FRAME_END__+0x17970>
    350c:	ldr	x0, [x0, #4040]
    3510:	ldp	q1, q3, [sp, #96]
    3514:	add	v0.2d, v0.2d, v2.2d
    3518:	ldr	x2, [sp, #136]
    351c:	ldr	x1, [x0]
    3520:	subs	x2, x2, x1
    3524:	mov	x1, #0x0                   	// #0
    3528:	add	v1.2d, v1.2d, v5.2d
    352c:	add	v4.2d, v4.2d, v3.2d
    3530:	add	v0.2d, v0.2d, v1.2d
    3534:	add	v0.2d, v0.2d, v4.2d
    3538:	mov	d1, v0.d[1]
    353c:	add	d0, d1, d0
    3540:	fmov	x0, d0
    3544:	b.ne	3568 <read_slice_acc8_k4+0x200>  // b.any
    3548:	ldp	x29, x30, [sp, #144]
    354c:	add	sp, sp, #0xa0
    3550:	ret
    3554:	ldp	q0, q1, [sp, #16]
    3558:	movi	v4.4s, #0x0
    355c:	ldp	q3, q2, [sp, #48]
    3560:	ldr	q5, [sp, #80]
    3564:	b	3500 <read_slice_acc8_k4+0x198>
    3568:	bl	12e0 <__stack_chk_fail@plt>

Disassembly of section .fini:

# ===== read_slice_acc8_k8 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

000000000000356c <read_slice_acc8_k8>:
    356c:	adrp	x4, 1f000 <__FRAME_END__+0x17970>
    3570:	ldr	x4, [x4, #4040]
    3574:	sub	sp, sp, #0xa0
    3578:	movi	v0.4s, #0x0
    357c:	mov	x3, x0
    3580:	mov	x2, sp
    3584:	lsr	x5, x1, #3
    3588:	stp	x29, x30, [sp, #144]
    358c:	add	x29, sp, #0x90
    3590:	ldr	x0, [x4]
    3594:	str	x0, [sp, #136]
    3598:	mov	x0, #0x0                   	// #0
    359c:	stp	q0, q0, [x2]
    35a0:	stp	q0, q0, [x2, #32]
    35a4:	stp	q0, q0, [x2, #64]
    35a8:	stp	q0, q0, [x2, #96]
    35ac:	cbz	x5, 36ac <read_slice_acc8_k8+0x140>
    35b0:	movi	v0.4s, #0x0
    35b4:	lsl	x2, x5, #3
    35b8:	mov	x4, #0x0                   	// #0
    35bc:	mov	v2.16b, v0.16b
    35c0:	mov	v3.16b, v0.16b
    35c4:	mov	v4.16b, v0.16b
    35c8:	mov	v5.16b, v0.16b
    35cc:	mov	v6.16b, v0.16b
    35d0:	mov	v7.16b, v0.16b
    35d4:	mov	v1.16b, v0.16b
    35d8:	nop
    35dc:	nop
    35e0:	mov	x0, x3
    35e4:	mov	w1, #0x8                   	// #8
    35e8:	ldp	q19, q18, [x0]
    35ec:	subs	w1, w1, #0x1
    35f0:	ldp	q17, q16, [x0, #32]
    35f4:	add	v1.2d, v1.2d, v19.2d
    35f8:	add	v7.2d, v7.2d, v18.2d
    35fc:	ldp	q19, q18, [x0, #64]
    3600:	add	v6.2d, v6.2d, v17.2d
    3604:	add	v5.2d, v5.2d, v16.2d
    3608:	ldp	q17, q16, [x0, #96]
    360c:	add	x0, x0, x2
    3610:	add	v4.2d, v4.2d, v19.2d
    3614:	add	v3.2d, v3.2d, v18.2d
    3618:	add	v2.2d, v2.2d, v17.2d
    361c:	add	v0.2d, v0.2d, v16.2d
    3620:	b.ne	35e8 <read_slice_acc8_k8+0x7c>  // b.any
    3624:	add	x4, x4, #0x10
    3628:	add	x3, x3, #0x80
    362c:	cmp	x5, x4
    3630:	b.hi	35e0 <read_slice_acc8_k8+0x74>  // b.pmore
    3634:	stp	q5, q4, [sp, #48]
    3638:	mov	v4.16b, v5.16b
    363c:	str	q0, [sp, #112]
    3640:	mov	v0.16b, v7.16b
    3644:	stp	q3, q2, [sp, #80]
    3648:	mov	v2.16b, v6.16b
    364c:	stp	q7, q6, [sp, #16]
    3650:	ldp	q3, q5, [sp, #64]
    3654:	add	v0.2d, v0.2d, v2.2d
    3658:	ldr	q2, [sp, #96]
    365c:	adrp	x0, 1f000 <__FRAME_END__+0x17970>
    3660:	ldr	x0, [x0, #4040]
    3664:	add	v3.2d, v3.2d, v4.2d
    3668:	ldr	q4, [sp, #112]
    366c:	add	v2.2d, v2.2d, v5.2d
    3670:	ldr	x2, [sp, #136]
    3674:	ldr	x1, [x0]
    3678:	subs	x2, x2, x1
    367c:	mov	x1, #0x0                   	// #0
    3680:	add	v0.2d, v0.2d, v3.2d
    3684:	add	v1.2d, v1.2d, v4.2d
    3688:	add	v0.2d, v0.2d, v2.2d
    368c:	add	v0.2d, v0.2d, v1.2d
    3690:	mov	d1, v0.d[1]
    3694:	add	d0, d1, d0
    3698:	fmov	x0, d0
    369c:	b.ne	36bc <read_slice_acc8_k8+0x150>  // b.any
    36a0:	ldp	x29, x30, [sp, #144]
    36a4:	add	sp, sp, #0xa0
    36a8:	ret
    36ac:	ldp	q0, q2, [sp, #16]
    36b0:	movi	v1.4s, #0x0
    36b4:	ldr	q4, [sp, #48]
    36b8:	b	3650 <read_slice_acc8_k8+0xe4>
    36bc:	bl	12e0 <__stack_chk_fail@plt>

Disassembly of section .fini:

# ===== read_slice_acc16_k1 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000036c0 <read_slice_acc16_k1>:
    36c0:	adrp	x3, 1f000 <__FRAME_END__+0x17970>
    36c4:	ldr	x3, [x3, #4040]
    36c8:	sub	sp, sp, #0x120
    36cc:	movi	v0.4s, #0x0
    36d0:	mov	x2, sp
    36d4:	stp	x29, x30, [sp, #272]
    36d8:	add	x29, sp, #0x110
    36dc:	ldr	x4, [x3]
    36e0:	str	x4, [sp, #264]
    36e4:	mov	x4, #0x0                   	// #0
    36e8:	stp	q0, q0, [x2]
    36ec:	stp	q0, q0, [x2, #32]
    36f0:	stp	q0, q0, [x2, #64]
    36f4:	stp	q0, q0, [x2, #96]
    36f8:	stp	q0, q0, [x2, #128]
    36fc:	stp	q0, q0, [x2, #160]
    3700:	stp	q0, q0, [x2, #192]
    3704:	stp	q0, q0, [x2, #224]
    3708:	cbz	x1, 3890 <read_slice_acc16_k1+0x1d0>
    370c:	movi	v0.4s, #0x0
    3710:	sub	x1, x1, #0x1
    3714:	add	x2, x0, #0x100
    3718:	lsr	x1, x1, #5
    371c:	add	x1, x2, x1, lsl #8
    3720:	mov	v2.16b, v0.16b
    3724:	mov	v3.16b, v0.16b
    3728:	mov	v4.16b, v0.16b
    372c:	mov	v5.16b, v0.16b
    3730:	mov	v6.16b, v0.16b
    3734:	mov	v7.16b, v0.16b
    3738:	mov	v16.16b, v0.16b
    373c:	mov	v17.16b, v0.16b
    3740:	mov	v18.16b, v0.16b
    3744:	mov	v19.16b, v0.16b
    3748:	mov	v20.16b, v0.16b
    374c:	mov	v21.16b, v0.16b
    3750:	mov	v22.16b, v0.16b
    3754:	mov	v23.16b, v0.16b
    3758:	mov	v1.16b, v0.16b
    375c:	nop
    3760:	ldp	q27, q26, [x0]
    3764:	ldp	q25, q24, [x0, #32]
    3768:	add	v1.2d, v1.2d, v27.2d
    376c:	add	v23.2d, v23.2d, v26.2d
    3770:	ldp	q27, q26, [x0, #64]
    3774:	add	v22.2d, v22.2d, v25.2d
    3778:	add	v21.2d, v21.2d, v24.2d
    377c:	ldp	q25, q24, [x0, #96]
    3780:	add	v20.2d, v20.2d, v27.2d
    3784:	add	v19.2d, v19.2d, v26.2d
    3788:	ldp	q27, q26, [x0, #128]
    378c:	add	v18.2d, v18.2d, v25.2d
    3790:	add	v17.2d, v17.2d, v24.2d
    3794:	ldp	q25, q24, [x0, #160]
    3798:	add	v16.2d, v16.2d, v27.2d
    379c:	add	v7.2d, v7.2d, v26.2d
    37a0:	ldp	q27, q26, [x0, #192]
    37a4:	add	v6.2d, v6.2d, v25.2d
    37a8:	add	v5.2d, v5.2d, v24.2d
    37ac:	ldp	q25, q24, [x0, #224]
    37b0:	add	x0, x0, #0x100
    37b4:	add	v4.2d, v4.2d, v27.2d
    37b8:	add	v3.2d, v3.2d, v26.2d
    37bc:	add	v2.2d, v2.2d, v25.2d
    37c0:	add	v0.2d, v0.2d, v24.2d
    37c4:	cmp	x1, x0
    37c8:	b.ne	3760 <read_slice_acc16_k1+0xa0>  // b.any
    37cc:	stp	q7, q6, [sp, #144]
    37d0:	mov	v7.16b, v19.16b
    37d4:	mov	v6.16b, v17.16b
    37d8:	str	q0, [sp, #240]
    37dc:	mov	v0.16b, v23.16b
    37e0:	stp	q5, q4, [sp, #176]
    37e4:	mov	v4.16b, v21.16b
    37e8:	mov	v5.16b, v16.16b
    37ec:	stp	q3, q2, [sp, #208]
    37f0:	mov	v2.16b, v22.16b
    37f4:	mov	v3.16b, v20.16b
    37f8:	stp	q23, q22, [sp, #16]
    37fc:	stp	q21, q20, [sp, #48]
    3800:	stp	q19, q18, [sp, #80]
    3804:	stp	q17, q16, [sp, #112]
    3808:	add	v0.2d, v0.2d, v2.2d
    380c:	ldr	q2, [sp, #96]
    3810:	add	v3.2d, v3.2d, v4.2d
    3814:	ldp	q4, q16, [sp, #144]
    3818:	add	v0.2d, v0.2d, v3.2d
    381c:	ldr	q3, [sp, #192]
    3820:	add	v2.2d, v2.2d, v7.2d
    3824:	ldr	q7, [sp, #176]
    3828:	adrp	x0, 1f000 <__FRAME_END__+0x17970>
    382c:	ldr	x0, [x0, #4040]
    3830:	add	v2.2d, v2.2d, v6.2d
    3834:	add	v4.2d, v4.2d, v5.2d
    3838:	ldp	q6, q5, [sp, #208]
    383c:	add	v3.2d, v3.2d, v7.2d
    3840:	ldr	x2, [sp, #264]
    3844:	ldr	x1, [x0]
    3848:	subs	x2, x2, x1
    384c:	mov	x1, #0x0                   	// #0
    3850:	add	v0.2d, v0.2d, v2.2d
    3854:	ldr	q2, [sp, #240]
    3858:	add	v4.2d, v4.2d, v16.2d
    385c:	add	v0.2d, v0.2d, v4.2d
    3860:	add	v3.2d, v3.2d, v6.2d
    3864:	add	v2.2d, v2.2d, v5.2d
    3868:	add	v0.2d, v0.2d, v3.2d
    386c:	add	v1.2d, v2.2d, v1.2d
    3870:	add	v0.2d, v0.2d, v1.2d
    3874:	mov	d1, v0.d[1]
    3878:	add	d0, d1, d0
    387c:	fmov	x0, d0
    3880:	b.ne	38a8 <read_slice_acc16_k1+0x1e8>  // b.any
    3884:	ldp	x29, x30, [sp, #272]
    3888:	add	sp, sp, #0x120
    388c:	ret
    3890:	ldp	q0, q2, [sp, #16]
    3894:	movi	v1.4s, #0x0
    3898:	ldp	q4, q3, [sp, #48]
    389c:	ldr	q7, [sp, #80]
    38a0:	ldp	q6, q5, [sp, #112]
    38a4:	b	3808 <read_slice_acc16_k1+0x148>
    38a8:	bl	12e0 <__stack_chk_fail@plt>

Disassembly of section .fini:

# ===== read_slice_acc16_k2 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000038ac <read_slice_acc16_k2>:
    38ac:	adrp	x3, 1f000 <__FRAME_END__+0x17970>
    38b0:	ldr	x3, [x3, #4040]
    38b4:	sub	sp, sp, #0x120
    38b8:	movi	v0.4s, #0x0
    38bc:	lsr	x1, x1, #1
    38c0:	mov	x2, sp
    38c4:	stp	x29, x30, [sp, #272]
    38c8:	add	x29, sp, #0x110
    38cc:	ldr	x4, [x3]
    38d0:	str	x4, [sp, #264]
    38d4:	mov	x4, #0x0                   	// #0
    38d8:	stp	q0, q0, [x2]
    38dc:	stp	q0, q0, [x2, #32]
    38e0:	stp	q0, q0, [x2, #64]
    38e4:	stp	q0, q0, [x2, #96]
    38e8:	stp	q0, q0, [x2, #128]
    38ec:	stp	q0, q0, [x2, #160]
    38f0:	stp	q0, q0, [x2, #192]
    38f4:	stp	q0, q0, [x2, #224]
    38f8:	cbz	x1, 3af0 <read_slice_acc16_k2+0x244>
    38fc:	movi	v4.4s, #0x0
    3900:	sub	x2, x1, #0x1
    3904:	add	x3, x0, #0x100
    3908:	add	x1, x0, x1, lsl #3
    390c:	lsr	x2, x2, #5
    3910:	add	x2, x3, x2, lsl #8
    3914:	mov	v6.16b, v4.16b
    3918:	mov	v7.16b, v4.16b
    391c:	mov	v16.16b, v4.16b
    3920:	mov	v17.16b, v4.16b
    3924:	mov	v18.16b, v4.16b
    3928:	mov	v19.16b, v4.16b
    392c:	mov	v20.16b, v4.16b
    3930:	mov	v21.16b, v4.16b
    3934:	mov	v22.16b, v4.16b
    3938:	mov	v23.16b, v4.16b
    393c:	mov	v24.16b, v4.16b
    3940:	mov	v25.16b, v4.16b
    3944:	mov	v26.16b, v4.16b
    3948:	mov	v27.16b, v4.16b
    394c:	mov	v5.16b, v4.16b
    3950:	ldp	q0, q29, [x1]
    3954:	ldp	q3, q2, [x0]
    3958:	ldr	q28, [x1, #32]
    395c:	ldr	q1, [x0, #32]
    3960:	add	v3.2d, v3.2d, v0.2d
    3964:	add	v2.2d, v2.2d, v29.2d
    3968:	add	v1.2d, v1.2d, v28.2d
    396c:	ldp	q29, q28, [x1, #48]
    3970:	add	v5.2d, v5.2d, v3.2d
    3974:	ldp	q0, q3, [x0, #48]
    3978:	add	v27.2d, v27.2d, v2.2d
    397c:	add	v26.2d, v26.2d, v1.2d
    3980:	ldp	q2, q1, [x0, #80]
    3984:	add	v0.2d, v0.2d, v29.2d
    3988:	add	v3.2d, v3.2d, v28.2d
    398c:	ldp	q29, q28, [x1, #80]
    3990:	add	v25.2d, v25.2d, v0.2d
    3994:	add	v24.2d, v24.2d, v3.2d
    3998:	ldp	q0, q3, [x0, #112]
    399c:	add	v2.2d, v2.2d, v29.2d
    39a0:	add	v1.2d, v1.2d, v28.2d
    39a4:	ldp	q29, q28, [x1, #112]
    39a8:	add	v23.2d, v23.2d, v2.2d
    39ac:	add	v22.2d, v22.2d, v1.2d
    39b0:	ldp	q2, q1, [x0, #144]
    39b4:	add	v0.2d, v0.2d, v29.2d
    39b8:	add	v3.2d, v3.2d, v28.2d
    39bc:	ldp	q29, q28, [x1, #144]
    39c0:	add	v21.2d, v21.2d, v0.2d
    39c4:	add	v20.2d, v20.2d, v3.2d
    39c8:	ldp	q0, q3, [x0, #176]
    39cc:	add	v2.2d, v2.2d, v29.2d
    39d0:	add	v1.2d, v1.2d, v28.2d
    39d4:	ldp	q29, q28, [x1, #176]
    39d8:	add	v19.2d, v19.2d, v2.2d
    39dc:	add	v18.2d, v18.2d, v1.2d
    39e0:	ldp	q2, q1, [x0, #208]
    39e4:	add	x0, x0, #0x100
    39e8:	add	v0.2d, v0.2d, v29.2d
    39ec:	add	v3.2d, v3.2d, v28.2d
    39f0:	ldp	q29, q28, [x1, #208]
    39f4:	add	x1, x1, #0x100
    39f8:	add	v17.2d, v17.2d, v0.2d
    39fc:	ldur	q0, [x0, #-16]
    3a00:	add	v16.2d, v16.2d, v3.2d
    3a04:	ldur	q3, [x1, #-16]
    3a08:	add	v2.2d, v2.2d, v29.2d
    3a0c:	add	v1.2d, v1.2d, v28.2d
    3a10:	add	v0.2d, v0.2d, v3.2d
    3a14:	add	v7.2d, v7.2d, v2.2d
    3a18:	add	v6.2d, v6.2d, v1.2d
    3a1c:	add	v4.2d, v4.2d, v0.2d
    3a20:	cmp	x0, x2
    3a24:	b.ne	3950 <read_slice_acc16_k2+0xa4>  // b.any
    3a28:	mov	v0.16b, v27.16b
    3a2c:	mov	v1.16b, v26.16b
    3a30:	str	q4, [sp, #240]
    3a34:	mov	v3.16b, v25.16b
    3a38:	mov	v2.16b, v24.16b
    3a3c:	mov	v4.16b, v20.16b
    3a40:	stp	q17, q16, [sp, #176]
    3a44:	mov	v16.16b, v18.16b
    3a48:	stp	q7, q6, [sp, #208]
    3a4c:	mov	v7.16b, v23.16b
    3a50:	mov	v6.16b, v21.16b
    3a54:	stp	q27, q26, [sp, #16]
    3a58:	stp	q25, q24, [sp, #48]
    3a5c:	stp	q23, q22, [sp, #80]
    3a60:	stp	q21, q20, [sp, #112]
    3a64:	stp	q19, q18, [sp, #144]
    3a68:	add	v0.2d, v0.2d, v1.2d
    3a6c:	ldr	q1, [sp, #96]
    3a70:	add	v2.2d, v2.2d, v3.2d
    3a74:	ldr	q3, [sp, #144]
    3a78:	add	v0.2d, v0.2d, v2.2d
    3a7c:	ldr	q2, [sp, #192]
    3a80:	add	v1.2d, v1.2d, v7.2d
    3a84:	ldr	q7, [sp, #176]
    3a88:	add	v3.2d, v3.2d, v4.2d
    3a8c:	adrp	x0, 1f000 <__FRAME_END__+0x17970>
    3a90:	ldr	x0, [x0, #4040]
    3a94:	add	v1.2d, v1.2d, v6.2d
    3a98:	ldp	q6, q4, [sp, #208]
    3a9c:	add	v3.2d, v3.2d, v16.2d
    3aa0:	add	v2.2d, v2.2d, v7.2d
    3aa4:	ldr	x2, [sp, #264]
    3aa8:	ldr	x1, [x0]
    3aac:	subs	x2, x2, x1
    3ab0:	mov	x1, #0x0                   	// #0
    3ab4:	add	v0.2d, v0.2d, v1.2d
    3ab8:	ldr	q1, [sp, #240]
    3abc:	add	v0.2d, v0.2d, v3.2d
    3ac0:	add	v2.2d, v2.2d, v6.2d
    3ac4:	add	v1.2d, v1.2d, v4.2d
    3ac8:	add	v0.2d, v0.2d, v2.2d
    3acc:	add	v1.2d, v1.2d, v5.2d
    3ad0:	add	v0.2d, v0.2d, v1.2d
    3ad4:	mov	d1, v0.d[1]
    3ad8:	add	d0, d1, d0
    3adc:	fmov	x0, d0
    3ae0:	b.ne	3b0c <read_slice_acc16_k2+0x260>  // b.any
    3ae4:	ldp	x29, x30, [sp, #272]
    3ae8:	add	sp, sp, #0x120
    3aec:	ret
    3af0:	ldp	q0, q1, [sp, #16]
    3af4:	movi	v5.4s, #0x0
    3af8:	ldp	q3, q2, [sp, #48]
    3afc:	ldr	q7, [sp, #80]
    3b00:	ldp	q6, q4, [sp, #112]
    3b04:	ldr	q16, [sp, #160]
    3b08:	b	3a68 <read_slice_acc16_k2+0x1bc>
    3b0c:	bl	12e0 <__stack_chk_fail@plt>

Disassembly of section .fini:

# ===== read_slice_acc16_k4 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003b10 <read_slice_acc16_k4>:
    3b10:	adrp	x4, 1f000 <__FRAME_END__+0x17970>
    3b14:	ldr	x4, [x4, #4040]
    3b18:	sub	sp, sp, #0x120
    3b1c:	movi	v0.4s, #0x0
    3b20:	mov	x3, x0
    3b24:	mov	x2, sp
    3b28:	lsr	x5, x1, #2
    3b2c:	stp	x29, x30, [sp, #272]
    3b30:	add	x29, sp, #0x110
    3b34:	ldr	x0, [x4]
    3b38:	str	x0, [sp, #264]
    3b3c:	mov	x0, #0x0                   	// #0
    3b40:	stp	q0, q0, [x2]
    3b44:	stp	q0, q0, [x2, #32]
    3b48:	stp	q0, q0, [x2, #64]
    3b4c:	stp	q0, q0, [x2, #96]
    3b50:	stp	q0, q0, [x2, #128]
    3b54:	stp	q0, q0, [x2, #160]
    3b58:	stp	q0, q0, [x2, #192]
    3b5c:	stp	q0, q0, [x2, #224]
    3b60:	cbz	x5, 3cf4 <read_slice_acc16_k4+0x1e4>
    3b64:	movi	v0.4s, #0x0
    3b68:	lsl	x2, x5, #3
    3b6c:	mov	x4, #0x0                   	// #0
    3b70:	mov	v2.16b, v0.16b
    3b74:	mov	v3.16b, v0.16b
    3b78:	mov	v4.16b, v0.16b
    3b7c:	mov	v5.16b, v0.16b
    3b80:	mov	v6.16b, v0.16b
    3b84:	mov	v7.16b, v0.16b
    3b88:	mov	v16.16b, v0.16b
    3b8c:	mov	v17.16b, v0.16b
    3b90:	mov	v18.16b, v0.16b
    3b94:	mov	v19.16b, v0.16b
    3b98:	mov	v20.16b, v0.16b
    3b9c:	mov	v21.16b, v0.16b
    3ba0:	mov	v22.16b, v0.16b
    3ba4:	mov	v23.16b, v0.16b
    3ba8:	mov	v1.16b, v0.16b
    3bac:	mov	x0, x3
    3bb0:	mov	w1, #0x4                   	// #4
    3bb4:	ldp	q27, q26, [x0]
    3bb8:	subs	w1, w1, #0x1
    3bbc:	ldp	q25, q24, [x0, #32]
    3bc0:	add	v1.2d, v1.2d, v27.2d
    3bc4:	add	v23.2d, v23.2d, v26.2d
    3bc8:	ldp	q27, q26, [x0, #64]
    3bcc:	add	v22.2d, v22.2d, v25.2d
    3bd0:	add	v21.2d, v21.2d, v24.2d
    3bd4:	ldp	q25, q24, [x0, #96]
    3bd8:	add	v20.2d, v20.2d, v27.2d
    3bdc:	add	v19.2d, v19.2d, v26.2d
    3be0:	ldp	q27, q26, [x0, #128]
    3be4:	add	v18.2d, v18.2d, v25.2d
    3be8:	add	v17.2d, v17.2d, v24.2d
    3bec:	ldp	q25, q24, [x0, #160]
    3bf0:	add	v16.2d, v16.2d, v27.2d
    3bf4:	add	v7.2d, v7.2d, v26.2d
    3bf8:	ldp	q27, q26, [x0, #192]
    3bfc:	add	v6.2d, v6.2d, v25.2d
    3c00:	add	v5.2d, v5.2d, v24.2d
    3c04:	ldp	q25, q24, [x0, #224]
    3c08:	add	x0, x0, x2
    3c0c:	add	v4.2d, v4.2d, v27.2d
    3c10:	add	v3.2d, v3.2d, v26.2d
    3c14:	add	v2.2d, v2.2d, v25.2d
    3c18:	add	v0.2d, v0.2d, v24.2d
    3c1c:	b.ne	3bb4 <read_slice_acc16_k4+0xa4>  // b.any
    3c20:	add	x4, x4, #0x20
    3c24:	add	x3, x3, #0x100
    3c28:	cmp	x5, x4
    3c2c:	b.hi	3bac <read_slice_acc16_k4+0x9c>  // b.pmore
    3c30:	stp	q7, q6, [sp, #144]
    3c34:	mov	v7.16b, v19.16b
    3c38:	mov	v6.16b, v17.16b
    3c3c:	str	q0, [sp, #240]
    3c40:	mov	v0.16b, v23.16b
    3c44:	stp	q5, q4, [sp, #176]
    3c48:	mov	v4.16b, v21.16b
    3c4c:	mov	v5.16b, v16.16b
    3c50:	stp	q3, q2, [sp, #208]
    3c54:	mov	v2.16b, v22.16b
    3c58:	mov	v3.16b, v20.16b
    3c5c:	stp	q23, q22, [sp, #16]
    3c60:	stp	q21, q20, [sp, #48]
    3c64:	stp	q19, q18, [sp, #80]
    3c68:	stp	q17, q16, [sp, #112]
    3c6c:	add	v0.2d, v0.2d, v2.2d
    3c70:	ldr	q2, [sp, #96]
    3c74:	add	v3.2d, v3.2d, v4.2d
    3c78:	ldp	q4, q16, [sp, #144]
    3c7c:	add	v0.2d, v0.2d, v3.2d
    3c80:	ldr	q3, [sp, #192]
    3c84:	add	v2.2d, v2.2d, v7.2d
    3c88:	ldr	q7, [sp, #176]
    3c8c:	adrp	x0, 1f000 <__FRAME_END__+0x17970>
    3c90:	ldr	x0, [x0, #4040]
    3c94:	add	v2.2d, v2.2d, v6.2d
    3c98:	add	v4.2d, v4.2d, v5.2d
    3c9c:	ldp	q6, q5, [sp, #208]
    3ca0:	add	v3.2d, v3.2d, v7.2d
    3ca4:	ldr	x2, [sp, #264]
    3ca8:	ldr	x1, [x0]
    3cac:	subs	x2, x2, x1
    3cb0:	mov	x1, #0x0                   	// #0
    3cb4:	add	v0.2d, v0.2d, v2.2d
    3cb8:	ldr	q2, [sp, #240]
    3cbc:	add	v4.2d, v4.2d, v16.2d
    3cc0:	add	v0.2d, v0.2d, v4.2d
    3cc4:	add	v3.2d, v3.2d, v6.2d
    3cc8:	add	v2.2d, v2.2d, v5.2d
    3ccc:	add	v0.2d, v0.2d, v3.2d
    3cd0:	add	v1.2d, v2.2d, v1.2d
    3cd4:	add	v0.2d, v0.2d, v1.2d
    3cd8:	mov	d1, v0.d[1]
    3cdc:	add	d0, d1, d0
    3ce0:	fmov	x0, d0
    3ce4:	b.ne	3d0c <read_slice_acc16_k4+0x1fc>  // b.any
    3ce8:	ldp	x29, x30, [sp, #272]
    3cec:	add	sp, sp, #0x120
    3cf0:	ret
    3cf4:	ldp	q0, q2, [sp, #16]
    3cf8:	movi	v1.4s, #0x0
    3cfc:	ldp	q4, q3, [sp, #48]
    3d00:	ldr	q7, [sp, #80]
    3d04:	ldp	q6, q5, [sp, #112]
    3d08:	b	3c6c <read_slice_acc16_k4+0x15c>
    3d0c:	bl	12e0 <__stack_chk_fail@plt>

Disassembly of section .fini:

# ===== read_slice_acc16_k8 =====

/home/adnancheema917/edge-llm-on-arm/work/bin/bandwidth:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003d10 <read_slice_acc16_k8>:
    3d10:	adrp	x4, 1f000 <__FRAME_END__+0x17970>
    3d14:	ldr	x4, [x4, #4040]
    3d18:	sub	sp, sp, #0x120
    3d1c:	movi	v0.4s, #0x0
    3d20:	mov	x3, x0
    3d24:	mov	x2, sp
    3d28:	lsr	x5, x1, #3
    3d2c:	stp	x29, x30, [sp, #272]
    3d30:	add	x29, sp, #0x110
    3d34:	ldr	x0, [x4]
    3d38:	str	x0, [sp, #264]
    3d3c:	mov	x0, #0x0                   	// #0
    3d40:	stp	q0, q0, [x2]
    3d44:	stp	q0, q0, [x2, #32]
    3d48:	stp	q0, q0, [x2, #64]
    3d4c:	stp	q0, q0, [x2, #96]
    3d50:	stp	q0, q0, [x2, #128]
    3d54:	stp	q0, q0, [x2, #160]
    3d58:	stp	q0, q0, [x2, #192]
    3d5c:	stp	q0, q0, [x2, #224]
    3d60:	cbz	x5, 3f00 <read_slice_acc16_k8+0x1f0>
    3d64:	movi	v0.4s, #0x0
    3d68:	lsl	x2, x5, #3
    3d6c:	mov	x4, #0x0                   	// #0
    3d70:	mov	v2.16b, v0.16b
    3d74:	mov	v3.16b, v0.16b
    3d78:	mov	v4.16b, v0.16b
    3d7c:	mov	v5.16b, v0.16b
    3d80:	mov	v6.16b, v0.16b
    3d84:	mov	v7.16b, v0.16b
    3d88:	mov	v16.16b, v0.16b
    3d8c:	mov	v17.16b, v0.16b
    3d90:	mov	v18.16b, v0.16b
    3d94:	mov	v19.16b, v0.16b
    3d98:	mov	v20.16b, v0.16b
    3d9c:	mov	v21.16b, v0.16b
    3da0:	mov	v22.16b, v0.16b
    3da4:	mov	v23.16b, v0.16b
    3da8:	mov	v1.16b, v0.16b
    3dac:	mov	x0, x3
    3db0:	mov	w1, #0x8                   	// #8
    3db4:	nop
    3db8:	nop
    3dbc:	nop
    3dc0:	ldp	q27, q26, [x0]
    3dc4:	subs	w1, w1, #0x1
    3dc8:	ldp	q25, q24, [x0, #32]
    3dcc:	add	v1.2d, v1.2d, v27.2d
    3dd0:	add	v23.2d, v23.2d, v26.2d
    3dd4:	ldp	q27, q26, [x0, #64]
    3dd8:	add	v22.2d, v22.2d, v25.2d
    3ddc:	add	v21.2d, v21.2d, v24.2d
    3de0:	ldp	q25, q24, [x0, #96]
    3de4:	add	v20.2d, v20.2d, v27.2d
    3de8:	add	v19.2d, v19.2d, v26.2d
    3dec:	ldp	q27, q26, [x0, #128]
    3df0:	add	v18.2d, v18.2d, v25.2d
    3df4:	add	v17.2d, v17.2d, v24.2d
    3df8:	ldp	q25, q24, [x0, #160]
    3dfc:	add	v16.2d, v16.2d, v27.2d
    3e00:	add	v7.2d, v7.2d, v26.2d
    3e04:	ldp	q27, q26, [x0, #192]
    3e08:	add	v6.2d, v6.2d, v25.2d
    3e0c:	add	v5.2d, v5.2d, v24.2d
    3e10:	ldp	q25, q24, [x0, #224]
    3e14:	add	x0, x0, x2
    3e18:	add	v4.2d, v4.2d, v27.2d
    3e1c:	add	v3.2d, v3.2d, v26.2d
    3e20:	add	v2.2d, v2.2d, v25.2d
    3e24:	add	v0.2d, v0.2d, v24.2d
    3e28:	b.ne	3dc0 <read_slice_acc16_k8+0xb0>  // b.any
    3e2c:	add	x4, x4, #0x20
    3e30:	add	x3, x3, #0x100
    3e34:	cmp	x5, x4
    3e38:	b.hi	3dac <read_slice_acc16_k8+0x9c>  // b.pmore
    3e3c:	stp	q7, q6, [sp, #144]
    3e40:	mov	v7.16b, v19.16b
    3e44:	mov	v6.16b, v17.16b
    3e48:	str	q0, [sp, #240]
    3e4c:	mov	v0.16b, v23.16b
    3e50:	stp	q5, q4, [sp, #176]
    3e54:	mov	v4.16b, v21.16b
    3e58:	mov	v5.16b, v16.16b
    3e5c:	stp	q3, q2, [sp, #208]
    3e60:	mov	v2.16b, v22.16b
    3e64:	mov	v3.16b, v20.16b
    3e68:	stp	q23, q22, [sp, #16]
    3e6c:	stp	q21, q20, [sp, #48]
    3e70:	stp	q19, q18, [sp, #80]
    3e74:	stp	q17, q16, [sp, #112]
    3e78:	add	v0.2d, v0.2d, v2.2d
    3e7c:	ldr	q2, [sp, #96]
    3e80:	add	v3.2d, v3.2d, v4.2d
    3e84:	ldp	q4, q16, [sp, #144]
    3e88:	add	v0.2d, v0.2d, v3.2d
    3e8c:	ldr	q3, [sp, #192]
    3e90:	add	v2.2d, v2.2d, v7.2d
    3e94:	ldr	q7, [sp, #176]
    3e98:	adrp	x0, 1f000 <__FRAME_END__+0x17970>
    3e9c:	ldr	x0, [x0, #4040]
    3ea0:	add	v2.2d, v2.2d, v6.2d
    3ea4:	add	v4.2d, v4.2d, v5.2d
    3ea8:	ldp	q6, q5, [sp, #208]
    3eac:	add	v3.2d, v3.2d, v7.2d
    3eb0:	ldr	x2, [sp, #264]
    3eb4:	ldr	x1, [x0]
    3eb8:	subs	x2, x2, x1
    3ebc:	mov	x1, #0x0                   	// #0
    3ec0:	add	v0.2d, v0.2d, v2.2d
    3ec4:	ldr	q2, [sp, #240]
    3ec8:	add	v4.2d, v4.2d, v16.2d
    3ecc:	add	v0.2d, v0.2d, v4.2d
    3ed0:	add	v3.2d, v3.2d, v6.2d
    3ed4:	add	v2.2d, v2.2d, v5.2d
    3ed8:	add	v0.2d, v0.2d, v3.2d
    3edc:	add	v1.2d, v2.2d, v1.2d
    3ee0:	add	v0.2d, v0.2d, v1.2d
    3ee4:	mov	d1, v0.d[1]
    3ee8:	add	d0, d1, d0
    3eec:	fmov	x0, d0
    3ef0:	b.ne	3f18 <read_slice_acc16_k8+0x208>  // b.any
    3ef4:	ldp	x29, x30, [sp, #272]
    3ef8:	add	sp, sp, #0x120
    3efc:	ret
    3f00:	ldp	q0, q2, [sp, #16]
    3f04:	movi	v1.4s, #0x0
    3f08:	ldp	q4, q3, [sp, #48]
    3f0c:	ldr	q7, [sp, #80]
    3f10:	ldp	q6, q5, [sp, #112]
    3f14:	b	3e78 <read_slice_acc16_k8+0x168>
    3f18:	bl	12e0 <__stack_chk_fail@plt>

Disassembly of section .fini:
