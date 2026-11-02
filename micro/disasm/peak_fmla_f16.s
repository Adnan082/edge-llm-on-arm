# ===== peak_fmla_f16_a8: hot loop = the 11 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003028 <peak_fmla_f16_a8>:
    3028:	adrp	x1, 20000 <__data_start>
    302c:	adrp	x2, 20000 <__data_start>
    3030:	movi	v2.8h, #0x0
    3034:	add	x1, x1, #0x10
    3038:	ldr	s0, [x1, #16]
    303c:	ldr	s1, [x2, #424]
    3040:	fcvt	h0, s0
    3044:	fcvt	h1, s1
    3048:	dup	v0.8h, v0.h[0]
    304c:	dup	v1.8h, v1.h[0]
    3050:	cbz	x0, 3140 <peak_fmla_f16_a8+0x118>
    3054:	mov	v3.16b, v2.16b
    3058:	mov	v4.16b, v2.16b
    305c:	mov	x1, #0x0                   	// #0
    3060:	mov	v5.16b, v2.16b
    3064:	mov	v6.16b, v2.16b
    3068:	mov	v7.16b, v2.16b
    306c:	mov	v16.16b, v2.16b
    3070:	mov	v17.16b, v2.16b
    3074:	nop
    3078:	nop
    307c:	nop
    3080:	fmla	v17.8h, v0.8h, v1.8h
    3084:	fmla	v16.8h, v0.8h, v1.8h
    3088:	fmla	v7.8h, v0.8h, v1.8h
    308c:	fmla	v6.8h, v0.8h, v1.8h
    3090:	fmla	v5.8h, v0.8h, v1.8h
    3094:	fmla	v4.8h, v0.8h, v1.8h
    3098:	fmla	v3.8h, v0.8h, v1.8h
    309c:	fmla	v2.8h, v0.8h, v1.8h
    30a0:	add	x1, x1, #0x1
    30a4:	cmp	x0, x1
    30a8:	b.ne	3080 <peak_fmla_f16_a8+0x58>  // b.any
    30ac:	fcvtl	v0.4s, v17.4h
    30b0:	movi	v1.4s, #0x0
    30b4:	fcvtl2	v17.4s, v17.8h
    30b8:	fcvtl	v23.4s, v16.4h
    30bc:	fcvtl2	v16.4s, v16.8h
    30c0:	fcvtl	v22.4s, v7.4h
    30c4:	fcvtl2	v7.4s, v7.8h
    30c8:	fcvtl	v21.4s, v6.4h
    30cc:	fadd	v0.4s, v0.4s, v1.4s
    30d0:	fcvtl2	v6.4s, v6.8h
    30d4:	fcvtl	v20.4s, v5.4h
    30d8:	fcvtl2	v5.4s, v5.8h
    30dc:	fcvtl	v19.4s, v4.4h
    30e0:	fcvtl2	v4.4s, v4.8h
    30e4:	fcvtl	v18.4s, v3.4h
    30e8:	fcvtl2	v3.4s, v3.8h
    30ec:	fcvtl	v1.4s, v2.4h
    30f0:	fcvtl2	v2.4s, v2.8h
    30f4:	fadd	v0.4s, v0.4s, v17.4s
    30f8:	fadd	v0.4s, v0.4s, v23.4s
    30fc:	fadd	v0.4s, v0.4s, v16.4s
    3100:	fadd	v0.4s, v0.4s, v22.4s
    3104:	fadd	v0.4s, v0.4s, v7.4s
    3108:	fadd	v0.4s, v0.4s, v21.4s
    310c:	fadd	v0.4s, v0.4s, v6.4s
    3110:	fadd	v0.4s, v0.4s, v20.4s
    3114:	fadd	v0.4s, v0.4s, v5.4s
    3118:	fadd	v0.4s, v0.4s, v19.4s
    311c:	fadd	v0.4s, v0.4s, v4.4s
    3120:	fadd	v0.4s, v0.4s, v18.4s
    3124:	fadd	v0.4s, v0.4s, v3.4s
    3128:	fadd	v0.4s, v0.4s, v1.4s
    312c:	fadd	v0.4s, v0.4s, v2.4s
    3130:	faddp	v0.4s, v0.4s, v0.4s
    3134:	faddp	v0.4s, v0.4s, v0.4s
    3138:	fmov	w0, s0
    313c:	ret
    3140:	mov	v3.16b, v2.16b
    3144:	mov	v4.16b, v2.16b
    3148:	mov	v5.16b, v2.16b
    314c:	mov	v6.16b, v2.16b
    3150:	mov	v7.16b, v2.16b
    3154:	mov	v16.16b, v2.16b
    3158:	mov	v17.16b, v2.16b
    315c:	b	30ac <peak_fmla_f16_a8+0x84>

Disassembly of section .fini:

# ===== peak_fmla_f16_a16: hot loop = the 19 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003160 <peak_fmla_f16_a16>:
    3160:	adrp	x1, 20000 <__data_start>
    3164:	adrp	x2, 20000 <__data_start>
    3168:	stp	d8, d9, [sp, #-48]!
    316c:	add	x1, x1, #0x10
    3170:	stp	d10, d11, [sp, #16]
    3174:	ldr	s0, [x1, #16]
    3178:	str	d12, [sp, #32]
    317c:	ldr	s1, [x2, #424]
    3180:	cbz	x0, 334c <peak_fmla_f16_a16+0x1ec>
    3184:	fcvt	h0, s0
    3188:	fcvt	h1, s1
    318c:	mov	x1, #0x0                   	// #0
    3190:	movi	v2.8h, #0x0
    3194:	mov	v5.16b, v2.16b
    3198:	mov	v3.16b, v2.16b
    319c:	dup	v0.8h, v0.h[0]
    31a0:	dup	v1.8h, v1.h[0]
    31a4:	mov	v4.16b, v2.16b
    31a8:	mov	v16.16b, v2.16b
    31ac:	mov	v19.16b, v2.16b
    31b0:	mov	v21.16b, v2.16b
    31b4:	mov	v23.16b, v2.16b
    31b8:	mov	v25.16b, v2.16b
    31bc:	mov	v27.16b, v2.16b
    31c0:	mov	v29.16b, v2.16b
    31c4:	mov	v31.16b, v2.16b
    31c8:	mov	v9.16b, v2.16b
    31cc:	mov	v11.16b, v2.16b
    31d0:	mov	v8.16b, v2.16b
    31d4:	mov	v6.16b, v2.16b
    31d8:	nop
    31dc:	nop
    31e0:	fmla	v6.8h, v0.8h, v1.8h
    31e4:	fmla	v8.8h, v0.8h, v1.8h
    31e8:	fmla	v11.8h, v0.8h, v1.8h
    31ec:	fmla	v9.8h, v0.8h, v1.8h
    31f0:	fmla	v31.8h, v0.8h, v1.8h
    31f4:	fmla	v29.8h, v0.8h, v1.8h
    31f8:	fmla	v27.8h, v0.8h, v1.8h
    31fc:	fmla	v25.8h, v0.8h, v1.8h
    3200:	fmla	v23.8h, v0.8h, v1.8h
    3204:	fmla	v21.8h, v0.8h, v1.8h
    3208:	fmla	v19.8h, v0.8h, v1.8h
    320c:	fmla	v16.8h, v0.8h, v1.8h
    3210:	fmla	v4.8h, v0.8h, v1.8h
    3214:	fmla	v3.8h, v0.8h, v1.8h
    3218:	fmla	v5.8h, v0.8h, v1.8h
    321c:	fmla	v2.8h, v0.8h, v1.8h
    3220:	add	x1, x1, #0x1
    3224:	cmp	x0, x1
    3228:	b.ne	31e0 <peak_fmla_f16_a16+0x80>  // b.any
    322c:	fcvtl	v0.4s, v6.4h
    3230:	movi	v17.4s, #0x0
    3234:	fcvtl2	v6.4s, v6.8h
    3238:	fcvtl	v7.4s, v8.4h
    323c:	fcvtl2	v1.4s, v8.8h
    3240:	fcvtl	v12.4s, v11.4h
    3244:	fcvtl2	v11.4s, v11.8h
    3248:	fcvtl	v10.4s, v9.4h
    324c:	fadd	v0.4s, v0.4s, v17.4s
    3250:	fcvtl2	v9.4s, v9.8h
    3254:	fcvtl	v8.4s, v31.4h
    3258:	fcvtl2	v31.4s, v31.8h
    325c:	fcvtl	v30.4s, v29.4h
    3260:	fcvtl2	v29.4s, v29.8h
    3264:	fcvtl	v28.4s, v27.4h
    3268:	fcvtl2	v27.4s, v27.8h
    326c:	fcvtl	v26.4s, v25.4h
    3270:	fcvtl2	v25.4s, v25.8h
    3274:	fcvtl	v24.4s, v23.4h
    3278:	fadd	v0.4s, v0.4s, v6.4s
    327c:	fcvtl2	v23.4s, v23.8h
    3280:	fcvtl	v22.4s, v21.4h
    3284:	fcvtl2	v21.4s, v21.8h
    3288:	fcvtl	v20.4s, v19.4h
    328c:	fcvtl2	v19.4s, v19.8h
    3290:	fcvtl	v18.4s, v16.4h
    3294:	fcvtl2	v16.4s, v16.8h
    3298:	fcvtl	v17.4s, v4.4h
    329c:	fcvtl2	v4.4s, v4.8h
    32a0:	fcvtl	v6.4s, v5.4h
    32a4:	fadd	v0.4s, v0.4s, v7.4s
    32a8:	fcvtl	v7.4s, v3.4h
    32ac:	fcvtl2	v3.4s, v3.8h
    32b0:	fadd	v0.4s, v0.4s, v1.4s
    32b4:	fcvtl2	v1.4s, v5.8h
    32b8:	fcvtl	v5.4s, v2.4h
    32bc:	fcvtl2	v2.4s, v2.8h
    32c0:	fadd	v0.4s, v0.4s, v12.4s
    32c4:	ldr	d12, [sp, #32]
    32c8:	fadd	v0.4s, v0.4s, v11.4s
    32cc:	fadd	v0.4s, v0.4s, v10.4s
    32d0:	ldp	d10, d11, [sp, #16]
    32d4:	fadd	v0.4s, v0.4s, v9.4s
    32d8:	fadd	v0.4s, v0.4s, v8.4s
    32dc:	ldp	d8, d9, [sp], #48
    32e0:	fadd	v0.4s, v0.4s, v31.4s
    32e4:	fadd	v0.4s, v0.4s, v30.4s
    32e8:	fadd	v0.4s, v0.4s, v29.4s
    32ec:	fadd	v0.4s, v0.4s, v28.4s
    32f0:	fadd	v0.4s, v0.4s, v27.4s
    32f4:	fadd	v0.4s, v0.4s, v26.4s
    32f8:	fadd	v0.4s, v0.4s, v25.4s
    32fc:	fadd	v0.4s, v0.4s, v24.4s
    3300:	fadd	v0.4s, v0.4s, v23.4s
    3304:	fadd	v0.4s, v0.4s, v22.4s
    3308:	fadd	v0.4s, v0.4s, v21.4s
    330c:	fadd	v0.4s, v0.4s, v20.4s
    3310:	fadd	v0.4s, v0.4s, v19.4s
    3314:	fadd	v0.4s, v0.4s, v18.4s
    3318:	fadd	v0.4s, v0.4s, v16.4s
    331c:	fadd	v0.4s, v0.4s, v17.4s
    3320:	fadd	v0.4s, v0.4s, v4.4s
    3324:	fadd	v0.4s, v0.4s, v7.4s
    3328:	fadd	v0.4s, v0.4s, v3.4s
    332c:	fadd	v0.4s, v0.4s, v6.4s
    3330:	fadd	v0.4s, v0.4s, v1.4s
    3334:	fadd	v0.4s, v0.4s, v5.4s
    3338:	fadd	v0.4s, v0.4s, v2.4s
    333c:	faddp	v0.4s, v0.4s, v0.4s
    3340:	faddp	v0.4s, v0.4s, v0.4s
    3344:	fmov	w0, s0
    3348:	ret
    334c:	movi	v2.8h, #0x0
    3350:	mov	v5.16b, v2.16b
    3354:	mov	v3.16b, v2.16b
    3358:	mov	v4.16b, v2.16b
    335c:	mov	v16.16b, v2.16b
    3360:	mov	v19.16b, v2.16b
    3364:	mov	v21.16b, v2.16b
    3368:	mov	v23.16b, v2.16b
    336c:	mov	v25.16b, v2.16b
    3370:	mov	v27.16b, v2.16b
    3374:	mov	v29.16b, v2.16b
    3378:	mov	v31.16b, v2.16b
    337c:	mov	v9.16b, v2.16b
    3380:	mov	v11.16b, v2.16b
    3384:	mov	v8.16b, v2.16b
    3388:	mov	v6.16b, v2.16b
    338c:	b	322c <peak_fmla_f16_a16+0xcc>

Disassembly of section .fini:

# ===== peak_fmla_f16_a28: hot loop = the 31 instructions of the innermost conditional backward branch holding the expected instruction =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003390 <peak_fmla_f16_a28>:
    3390:	adrp	x1, 20000 <__data_start>
    3394:	adrp	x2, 20000 <__data_start>
    3398:	stp	d8, d9, [sp, #-128]!
    339c:	add	x1, x1, #0x10
    33a0:	stp	d12, d13, [sp, #32]
    33a4:	stp	d10, d11, [sp, #16]
    33a8:	ldr	s0, [x1, #16]
    33ac:	stp	d14, d15, [sp, #48]
    33b0:	ldr	s13, [x2, #424]
    33b4:	cbz	x0, 36c8 <peak_fmla_f16_a28+0x338>
    33b8:	fcvt	h0, s0
    33bc:	fcvt	h13, s13
    33c0:	mov	x1, #0x0                   	// #0
    33c4:	movi	v1.8h, #0x0
    33c8:	mov	v2.16b, v1.16b
    33cc:	mov	v3.16b, v1.16b
    33d0:	dup	v0.8h, v0.h[0]
    33d4:	dup	v13.8h, v13.h[0]
    33d8:	mov	v4.16b, v1.16b
    33dc:	mov	v5.16b, v1.16b
    33e0:	mov	v6.16b, v1.16b
    33e4:	mov	v7.16b, v1.16b
    33e8:	mov	v16.16b, v1.16b
    33ec:	mov	v17.16b, v1.16b
    33f0:	mov	v18.16b, v1.16b
    33f4:	mov	v19.16b, v1.16b
    33f8:	mov	v20.16b, v1.16b
    33fc:	mov	v21.16b, v1.16b
    3400:	mov	v22.16b, v1.16b
    3404:	mov	v23.16b, v1.16b
    3408:	mov	v24.16b, v1.16b
    340c:	mov	v29.16b, v1.16b
    3410:	mov	v30.16b, v1.16b
    3414:	mov	v31.16b, v1.16b
    3418:	mov	v8.16b, v1.16b
    341c:	mov	v9.16b, v1.16b
    3420:	mov	v10.16b, v1.16b
    3424:	mov	v11.16b, v1.16b
    3428:	mov	v12.16b, v1.16b
    342c:	mov	v25.16b, v1.16b
    3430:	mov	v26.16b, v1.16b
    3434:	mov	v27.16b, v1.16b
    3438:	mov	v28.16b, v1.16b
    343c:	nop
    3440:	fmla	v28.8h, v0.8h, v13.8h
    3444:	fmla	v27.8h, v0.8h, v13.8h
    3448:	fmla	v26.8h, v0.8h, v13.8h
    344c:	fmla	v25.8h, v0.8h, v13.8h
    3450:	fmla	v12.8h, v0.8h, v13.8h
    3454:	fmla	v11.8h, v0.8h, v13.8h
    3458:	fmla	v10.8h, v0.8h, v13.8h
    345c:	fmla	v9.8h, v0.8h, v13.8h
    3460:	fmla	v8.8h, v0.8h, v13.8h
    3464:	fmla	v31.8h, v0.8h, v13.8h
    3468:	fmla	v30.8h, v0.8h, v13.8h
    346c:	fmla	v29.8h, v0.8h, v13.8h
    3470:	fmla	v24.8h, v0.8h, v13.8h
    3474:	fmla	v23.8h, v0.8h, v13.8h
    3478:	fmla	v22.8h, v0.8h, v13.8h
    347c:	fmla	v21.8h, v0.8h, v13.8h
    3480:	fmla	v20.8h, v0.8h, v13.8h
    3484:	fmla	v19.8h, v0.8h, v13.8h
    3488:	fmla	v18.8h, v0.8h, v13.8h
    348c:	fmla	v17.8h, v0.8h, v13.8h
    3490:	fmla	v16.8h, v0.8h, v13.8h
    3494:	fmla	v7.8h, v0.8h, v13.8h
    3498:	fmla	v6.8h, v0.8h, v13.8h
    349c:	fmla	v5.8h, v0.8h, v13.8h
    34a0:	fmla	v4.8h, v0.8h, v13.8h
    34a4:	fmla	v3.8h, v0.8h, v13.8h
    34a8:	fmla	v2.8h, v0.8h, v13.8h
    34ac:	fmla	v1.8h, v0.8h, v13.8h
    34b0:	add	x1, x1, #0x1
    34b4:	cmp	x0, x1
    34b8:	b.ne	3440 <peak_fmla_f16_a28+0xb0>  // b.any
    34bc:	str	q2, [sp, #112]
    34c0:	fcvtl	v0.4s, v28.4h
    34c4:	movi	v13.4s, #0x0
    34c8:	fcvtl2	v28.4s, v28.8h
    34cc:	fcvtl	v15.4s, v27.4h
    34d0:	fcvtl2	v27.4s, v27.8h
    34d4:	fcvtl	v14.4s, v26.4h
    34d8:	fcvtl2	v26.4s, v26.8h
    34dc:	fcvtl	v2.4s, v12.4h
    34e0:	fadd	v0.4s, v0.4s, v13.4s
    34e4:	fcvtl	v13.4s, v25.4h
    34e8:	fcvtl2	v25.4s, v25.8h
    34ec:	fcvtl2	v12.4s, v12.8h
    34f0:	str	q2, [sp, #96]
    34f4:	fcvtl	v2.4s, v10.4h
    34f8:	fcvtl2	v10.4s, v10.8h
    34fc:	fadd	v0.4s, v0.4s, v28.4s
    3500:	str	q2, [sp, #80]
    3504:	fcvtl	v28.4s, v11.4h
    3508:	fcvtl2	v11.4s, v11.8h
    350c:	ldr	q2, [sp, #96]
    3510:	fadd	v0.4s, v0.4s, v15.4s
    3514:	fcvtl	v15.4s, v9.4h
    3518:	fcvtl2	v9.4s, v9.8h
    351c:	fadd	v0.4s, v0.4s, v27.4s
    3520:	fcvtl	v27.4s, v8.4h
    3524:	fcvtl2	v8.4s, v8.8h
    3528:	fadd	v0.4s, v0.4s, v14.4s
    352c:	fcvtl	v14.4s, v31.4h
    3530:	fcvtl2	v31.4s, v31.8h
    3534:	fadd	v0.4s, v0.4s, v26.4s
    3538:	fcvtl	v26.4s, v30.4h
    353c:	fcvtl2	v30.4s, v30.8h
    3540:	fadd	v0.4s, v0.4s, v13.4s
    3544:	fcvtl	v13.4s, v29.4h
    3548:	fcvtl2	v29.4s, v29.8h
    354c:	fadd	v0.4s, v0.4s, v25.4s
    3550:	fcvtl	v25.4s, v24.4h
    3554:	fcvtl2	v24.4s, v24.8h
    3558:	str	q25, [sp, #64]
    355c:	fcvtl	v25.4s, v23.4h
    3560:	fcvtl2	v23.4s, v23.8h
    3564:	fadd	v0.4s, v0.4s, v2.4s
    3568:	ldr	q2, [sp, #80]
    356c:	fadd	v0.4s, v0.4s, v12.4s
    3570:	fcvtl	v12.4s, v22.4h
    3574:	fcvtl2	v22.4s, v22.8h
    3578:	fadd	v0.4s, v0.4s, v28.4s
    357c:	fcvtl	v28.4s, v21.4h
    3580:	fcvtl2	v21.4s, v21.8h
    3584:	fadd	v0.4s, v0.4s, v11.4s
    3588:	fcvtl	v11.4s, v20.4h
    358c:	fcvtl2	v20.4s, v20.8h
    3590:	fadd	v0.4s, v0.4s, v2.4s
    3594:	fcvtl	v2.4s, v19.4h
    3598:	fcvtl2	v19.4s, v19.8h
    359c:	str	q2, [sp, #80]
    35a0:	fadd	v0.4s, v0.4s, v10.4s
    35a4:	ldr	q2, [sp, #112]
    35a8:	fcvtl	v10.4s, v18.4h
    35ac:	fcvtl2	v18.4s, v18.8h
    35b0:	fadd	v0.4s, v0.4s, v15.4s
    35b4:	fcvtl	v15.4s, v17.4h
    35b8:	fcvtl2	v17.4s, v17.8h
    35bc:	fadd	v0.4s, v0.4s, v9.4s
    35c0:	fcvtl	v9.4s, v16.4h
    35c4:	fcvtl2	v16.4s, v16.8h
    35c8:	fadd	v0.4s, v0.4s, v27.4s
    35cc:	fcvtl	v27.4s, v7.4h
    35d0:	fcvtl2	v7.4s, v7.8h
    35d4:	fadd	v0.4s, v0.4s, v8.4s
    35d8:	fcvtl	v8.4s, v6.4h
    35dc:	fcvtl2	v6.4s, v6.8h
    35e0:	fadd	v0.4s, v0.4s, v14.4s
    35e4:	fcvtl	v14.4s, v5.4h
    35e8:	fcvtl2	v5.4s, v5.8h
    35ec:	fadd	v0.4s, v0.4s, v31.4s
    35f0:	fcvtl	v31.4s, v4.4h
    35f4:	fcvtl2	v4.4s, v4.8h
    35f8:	fadd	v0.4s, v0.4s, v26.4s
    35fc:	fcvtl	v26.4s, v3.4h
    3600:	fcvtl2	v3.4s, v3.8h
    3604:	fadd	v0.4s, v0.4s, v30.4s
    3608:	fcvtl	v30.4s, v2.4h
    360c:	fcvtl2	v2.4s, v2.8h
    3610:	fadd	v0.4s, v0.4s, v13.4s
    3614:	fcvtl	v13.4s, v1.4h
    3618:	fcvtl2	v1.4s, v1.8h
    361c:	fadd	v0.4s, v0.4s, v29.4s
    3620:	ldr	q29, [sp, #64]
    3624:	fadd	v0.4s, v0.4s, v29.4s
    3628:	fadd	v0.4s, v0.4s, v24.4s
    362c:	fadd	v0.4s, v0.4s, v25.4s
    3630:	fadd	v0.4s, v0.4s, v23.4s
    3634:	fadd	v0.4s, v0.4s, v12.4s
    3638:	fadd	v0.4s, v0.4s, v22.4s
    363c:	fadd	v0.4s, v0.4s, v28.4s
    3640:	fadd	v0.4s, v0.4s, v21.4s
    3644:	fadd	v0.4s, v0.4s, v11.4s
    3648:	ldr	q11, [sp, #80]
    364c:	fadd	v0.4s, v0.4s, v20.4s
    3650:	fadd	v0.4s, v0.4s, v11.4s
    3654:	fadd	v0.4s, v0.4s, v19.4s
    3658:	fadd	v0.4s, v0.4s, v10.4s
    365c:	ldp	d10, d11, [sp, #16]
    3660:	fadd	v0.4s, v0.4s, v18.4s
    3664:	fadd	v0.4s, v0.4s, v15.4s
    3668:	fadd	v0.4s, v0.4s, v17.4s
    366c:	fadd	v0.4s, v0.4s, v9.4s
    3670:	fadd	v0.4s, v0.4s, v16.4s
    3674:	fadd	v0.4s, v0.4s, v27.4s
    3678:	fadd	v0.4s, v0.4s, v7.4s
    367c:	fadd	v0.4s, v0.4s, v8.4s
    3680:	fadd	v0.4s, v0.4s, v6.4s
    3684:	fadd	v0.4s, v0.4s, v14.4s
    3688:	ldp	d14, d15, [sp, #48]
    368c:	fadd	v0.4s, v0.4s, v5.4s
    3690:	fadd	v0.4s, v0.4s, v31.4s
    3694:	fadd	v0.4s, v0.4s, v4.4s
    3698:	fadd	v0.4s, v0.4s, v26.4s
    369c:	fadd	v0.4s, v0.4s, v3.4s
    36a0:	fadd	v0.4s, v0.4s, v30.4s
    36a4:	fadd	v0.4s, v0.4s, v2.4s
    36a8:	fadd	v0.4s, v0.4s, v13.4s
    36ac:	ldp	d12, d13, [sp, #32]
    36b0:	ldp	d8, d9, [sp], #128
    36b4:	fadd	v0.4s, v0.4s, v1.4s
    36b8:	faddp	v0.4s, v0.4s, v0.4s
    36bc:	faddp	v0.4s, v0.4s, v0.4s
    36c0:	fmov	w0, s0
    36c4:	ret
    36c8:	movi	v1.8h, #0x0
    36cc:	mov	v3.16b, v1.16b
    36d0:	mov	v4.16b, v1.16b
    36d4:	str	q1, [sp, #112]
    36d8:	mov	v5.16b, v1.16b
    36dc:	mov	v6.16b, v1.16b
    36e0:	mov	v7.16b, v1.16b
    36e4:	mov	v16.16b, v1.16b
    36e8:	mov	v17.16b, v1.16b
    36ec:	mov	v18.16b, v1.16b
    36f0:	mov	v19.16b, v1.16b
    36f4:	mov	v20.16b, v1.16b
    36f8:	mov	v21.16b, v1.16b
    36fc:	mov	v22.16b, v1.16b
    3700:	mov	v23.16b, v1.16b
    3704:	mov	v24.16b, v1.16b
    3708:	mov	v29.16b, v1.16b
    370c:	mov	v30.16b, v1.16b
    3710:	mov	v31.16b, v1.16b
    3714:	mov	v8.16b, v1.16b
    3718:	mov	v9.16b, v1.16b
    371c:	mov	v10.16b, v1.16b
    3720:	mov	v11.16b, v1.16b
    3724:	mov	v12.16b, v1.16b
    3728:	mov	v25.16b, v1.16b
    372c:	mov	v26.16b, v1.16b
    3730:	mov	v27.16b, v1.16b
    3734:	mov	v28.16b, v1.16b
    3738:	b	34c0 <peak_fmla_f16_a28+0x130>

Disassembly of section .fini:
