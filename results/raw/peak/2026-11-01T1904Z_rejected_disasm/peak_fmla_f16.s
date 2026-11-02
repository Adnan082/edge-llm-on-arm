# ===== peak_fmla_f16_a8: hot loop = the 45 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000002fe8 <peak_fmla_f16_a8>:
    2fe8:	adrp	x1, 20000 <__data_start>
    2fec:	movi	v3.8h, #0x0
    2ff0:	add	x1, x1, #0x10
    2ff4:	ldr	s0, [x1, #16]
    2ff8:	ldr	s1, [x1, #20]
    2ffc:	fcvt	h0, s0
    3000:	fcvt	h1, s1
    3004:	dup	v0.8h, v0.h[0]
    3008:	fneg	h2, h1
    300c:	dup	v1.8h, v1.h[0]
    3010:	dup	v2.8h, v2.h[0]
    3014:	cbz	x0, 3120 <peak_fmla_f16_a8+0x138>
    3018:	mov	v4.16b, v3.16b
    301c:	mov	v5.16b, v3.16b
    3020:	mov	x1, #0x0                   	// #0
    3024:	mov	v6.16b, v3.16b
    3028:	mov	v7.16b, v3.16b
    302c:	mov	v16.16b, v3.16b
    3030:	mov	v17.16b, v3.16b
    3034:	mov	v18.16b, v3.16b
    3038:	nop
    303c:	nop
    3040:	fmla	v18.8h, v0.8h, v1.8h
    3044:	add	x1, x1, #0x1
    3048:	fmla	v17.8h, v0.8h, v1.8h
    304c:	fmla	v16.8h, v0.8h, v1.8h
    3050:	fmla	v7.8h, v0.8h, v1.8h
    3054:	fmla	v6.8h, v0.8h, v1.8h
    3058:	fmla	v5.8h, v0.8h, v1.8h
    305c:	fmla	v4.8h, v0.8h, v1.8h
    3060:	fmla	v3.8h, v0.8h, v1.8h
    3064:	fmla	v18.8h, v0.8h, v2.8h
    3068:	fmla	v17.8h, v0.8h, v2.8h
    306c:	fmla	v16.8h, v0.8h, v2.8h
    3070:	fmla	v7.8h, v0.8h, v2.8h
    3074:	fmla	v6.8h, v0.8h, v2.8h
    3078:	fmla	v5.8h, v0.8h, v2.8h
    307c:	fmla	v4.8h, v0.8h, v2.8h
    3080:	fmla	v3.8h, v0.8h, v2.8h
    3084:	cmp	x0, x1
    3088:	b.ne	3040 <peak_fmla_f16_a8+0x58>  // b.any
    308c:	fcvtl	v0.4s, v18.4h
    3090:	movi	v1.4s, #0x0
    3094:	fcvtl2	v18.4s, v18.8h
    3098:	fcvtl	v23.4s, v17.4h
    309c:	fcvtl2	v17.4s, v17.8h
    30a0:	fcvtl	v22.4s, v16.4h
    30a4:	fcvtl2	v16.4s, v16.8h
    30a8:	fcvtl	v21.4s, v7.4h
    30ac:	fadd	v0.4s, v0.4s, v1.4s
    30b0:	fcvtl2	v7.4s, v7.8h
    30b4:	fcvtl	v20.4s, v6.4h
    30b8:	fcvtl2	v6.4s, v6.8h
    30bc:	fcvtl	v19.4s, v5.4h
    30c0:	fcvtl2	v5.4s, v5.8h
    30c4:	fcvtl	v2.4s, v4.4h
    30c8:	fcvtl2	v4.4s, v4.8h
    30cc:	fcvtl	v1.4s, v3.4h
    30d0:	fcvtl2	v3.4s, v3.8h
    30d4:	fadd	v0.4s, v0.4s, v18.4s
    30d8:	fadd	v0.4s, v0.4s, v23.4s
    30dc:	fadd	v0.4s, v0.4s, v17.4s
    30e0:	fadd	v0.4s, v0.4s, v22.4s
    30e4:	fadd	v0.4s, v0.4s, v16.4s
    30e8:	fadd	v0.4s, v0.4s, v21.4s
    30ec:	fadd	v0.4s, v0.4s, v7.4s
    30f0:	fadd	v0.4s, v0.4s, v20.4s
    30f4:	fadd	v0.4s, v0.4s, v6.4s
    30f8:	fadd	v0.4s, v0.4s, v19.4s
    30fc:	fadd	v0.4s, v0.4s, v5.4s
    3100:	fadd	v0.4s, v0.4s, v2.4s
    3104:	fadd	v0.4s, v0.4s, v4.4s
    3108:	fadd	v0.4s, v0.4s, v1.4s
    310c:	fadd	v0.4s, v0.4s, v3.4s
    3110:	faddp	v0.4s, v0.4s, v0.4s
    3114:	faddp	v0.4s, v0.4s, v0.4s
    3118:	fmov	w0, s0
    311c:	ret
    3120:	mov	v4.16b, v3.16b
    3124:	mov	v5.16b, v3.16b
    3128:	mov	v6.16b, v3.16b
    312c:	mov	v7.16b, v3.16b
    3130:	mov	v16.16b, v3.16b
    3134:	mov	v17.16b, v3.16b
    3138:	mov	v18.16b, v3.16b
    313c:	b	308c <peak_fmla_f16_a8+0xa4>

Disassembly of section .fini:

# ===== peak_fmla_f16_a16: hot loop = the 88 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000003140 <peak_fmla_f16_a16>:
    3140:	adrp	x1, 20000 <__data_start>
    3144:	stp	d8, d9, [sp, #-32]!
    3148:	add	x1, x1, #0x10
    314c:	stp	d10, d11, [sp, #16]
    3150:	ldr	s0, [x1, #16]
    3154:	ldr	s1, [x1, #20]
    3158:	cbz	x0, 3368 <peak_fmla_f16_a16+0x228>
    315c:	fcvt	h1, s1
    3160:	fcvt	h0, s0
    3164:	mov	x1, #0x0                   	// #0
    3168:	movi	v25.8h, #0x0
    316c:	mov	v26.16b, v25.16b
    3170:	mov	v3.16b, v25.16b
    3174:	fneg	h2, h1
    3178:	dup	v0.8h, v0.h[0]
    317c:	dup	v1.8h, v1.h[0]
    3180:	mov	v4.16b, v25.16b
    3184:	mov	v5.16b, v25.16b
    3188:	mov	v6.16b, v25.16b
    318c:	mov	v7.16b, v25.16b
    3190:	mov	v16.16b, v25.16b
    3194:	dup	v2.8h, v2.h[0]
    3198:	mov	v17.16b, v25.16b
    319c:	mov	v18.16b, v25.16b
    31a0:	mov	v19.16b, v25.16b
    31a4:	mov	v20.16b, v25.16b
    31a8:	mov	v21.16b, v25.16b
    31ac:	mov	v22.16b, v25.16b
    31b0:	mov	v23.16b, v25.16b
    31b4:	mov	v24.16b, v25.16b
    31b8:	nop
    31bc:	nop
    31c0:	fmla	v24.8h, v0.8h, v1.8h
    31c4:	add	x1, x1, #0x1
    31c8:	fmla	v23.8h, v0.8h, v1.8h
    31cc:	fmla	v22.8h, v0.8h, v1.8h
    31d0:	fmla	v21.8h, v0.8h, v1.8h
    31d4:	fmla	v20.8h, v0.8h, v1.8h
    31d8:	fmla	v19.8h, v0.8h, v1.8h
    31dc:	fmla	v18.8h, v0.8h, v1.8h
    31e0:	fmla	v17.8h, v0.8h, v1.8h
    31e4:	fmla	v16.8h, v0.8h, v1.8h
    31e8:	fmla	v7.8h, v0.8h, v1.8h
    31ec:	fmla	v6.8h, v0.8h, v1.8h
    31f0:	fmla	v5.8h, v0.8h, v1.8h
    31f4:	fmla	v4.8h, v0.8h, v1.8h
    31f8:	fmla	v3.8h, v0.8h, v1.8h
    31fc:	fmla	v26.8h, v0.8h, v1.8h
    3200:	fmla	v25.8h, v0.8h, v1.8h
    3204:	fmla	v24.8h, v0.8h, v2.8h
    3208:	fmla	v23.8h, v0.8h, v2.8h
    320c:	fmla	v22.8h, v0.8h, v2.8h
    3210:	fmla	v21.8h, v0.8h, v2.8h
    3214:	fmla	v20.8h, v0.8h, v2.8h
    3218:	fmla	v19.8h, v0.8h, v2.8h
    321c:	fmla	v18.8h, v0.8h, v2.8h
    3220:	fmla	v17.8h, v0.8h, v2.8h
    3224:	fmla	v16.8h, v0.8h, v2.8h
    3228:	fmla	v7.8h, v0.8h, v2.8h
    322c:	fmla	v6.8h, v0.8h, v2.8h
    3230:	fmla	v5.8h, v0.8h, v2.8h
    3234:	fmla	v4.8h, v0.8h, v2.8h
    3238:	fmla	v3.8h, v0.8h, v2.8h
    323c:	fmla	v26.8h, v0.8h, v2.8h
    3240:	fmla	v25.8h, v0.8h, v2.8h
    3244:	cmp	x0, x1
    3248:	b.ne	31c0 <peak_fmla_f16_a16+0x80>  // b.any
    324c:	fcvtl	v11.4s, v24.4h
    3250:	movi	v0.4s, #0x0
    3254:	fcvtl2	v24.4s, v24.8h
    3258:	fcvtl	v2.4s, v23.4h
    325c:	fcvtl2	v23.4s, v23.8h
    3260:	fcvtl	v1.4s, v22.4h
    3264:	fcvtl2	v22.4s, v22.8h
    3268:	fcvtl	v10.4s, v21.4h
    326c:	fadd	v11.4s, v11.4s, v0.4s
    3270:	fcvtl2	v21.4s, v21.8h
    3274:	fcvtl	v9.4s, v20.4h
    3278:	fcvtl2	v20.4s, v20.8h
    327c:	fcvtl	v8.4s, v19.4h
    3280:	fcvtl2	v19.4s, v19.8h
    3284:	fcvtl	v0.4s, v18.4h
    3288:	fcvtl2	v18.4s, v18.8h
    328c:	fcvtl	v31.4s, v17.4h
    3290:	fcvtl2	v17.4s, v17.8h
    3294:	fcvtl	v30.4s, v16.4h
    3298:	fadd	v11.4s, v11.4s, v24.4s
    329c:	fcvtl2	v16.4s, v16.8h
    32a0:	fcvtl	v29.4s, v7.4h
    32a4:	fcvtl2	v7.4s, v7.8h
    32a8:	fcvtl	v28.4s, v6.4h
    32ac:	fcvtl2	v6.4s, v6.8h
    32b0:	fcvtl	v27.4s, v5.4h
    32b4:	fcvtl2	v5.4s, v5.8h
    32b8:	fcvtl	v24.4s, v3.4h
    32bc:	fcvtl2	v3.4s, v3.8h
    32c0:	fadd	v2.4s, v11.4s, v2.4s
    32c4:	fcvtl	v11.4s, v4.4h
    32c8:	fcvtl2	v4.4s, v4.8h
    32cc:	fadd	v23.4s, v2.4s, v23.4s
    32d0:	fcvtl	v2.4s, v26.4h
    32d4:	fcvtl2	v26.4s, v26.8h
    32d8:	fadd	v23.4s, v23.4s, v1.4s
    32dc:	fcvtl	v1.4s, v25.4h
    32e0:	fcvtl2	v25.4s, v25.8h
    32e4:	fadd	v22.4s, v23.4s, v22.4s
    32e8:	fadd	v10.4s, v22.4s, v10.4s
    32ec:	fadd	v10.4s, v10.4s, v21.4s
    32f0:	fadd	v9.4s, v10.4s, v9.4s
    32f4:	fadd	v9.4s, v9.4s, v20.4s
    32f8:	fadd	v8.4s, v9.4s, v8.4s
    32fc:	fadd	v8.4s, v8.4s, v19.4s
    3300:	fadd	v0.4s, v8.4s, v0.4s
    3304:	fadd	v0.4s, v0.4s, v18.4s
    3308:	fadd	v0.4s, v0.4s, v31.4s
    330c:	fadd	v0.4s, v0.4s, v17.4s
    3310:	fadd	v0.4s, v0.4s, v30.4s
    3314:	fadd	v0.4s, v0.4s, v16.4s
    3318:	fadd	v0.4s, v0.4s, v29.4s
    331c:	fadd	v0.4s, v0.4s, v7.4s
    3320:	fadd	v0.4s, v0.4s, v28.4s
    3324:	fadd	v0.4s, v0.4s, v6.4s
    3328:	fadd	v0.4s, v0.4s, v27.4s
    332c:	fadd	v0.4s, v0.4s, v5.4s
    3330:	fadd	v0.4s, v0.4s, v11.4s
    3334:	ldp	d10, d11, [sp, #16]
    3338:	ldp	d8, d9, [sp], #32
    333c:	fadd	v0.4s, v0.4s, v4.4s
    3340:	fadd	v0.4s, v0.4s, v24.4s
    3344:	fadd	v0.4s, v0.4s, v3.4s
    3348:	fadd	v0.4s, v0.4s, v2.4s
    334c:	fadd	v0.4s, v0.4s, v26.4s
    3350:	fadd	v0.4s, v0.4s, v1.4s
    3354:	fadd	v0.4s, v0.4s, v25.4s
    3358:	faddp	v0.4s, v0.4s, v0.4s
    335c:	faddp	v0.4s, v0.4s, v0.4s
    3360:	fmov	w0, s0
    3364:	ret
    3368:	movi	v25.8h, #0x0
    336c:	mov	v26.16b, v25.16b
    3370:	mov	v3.16b, v25.16b
    3374:	mov	v4.16b, v25.16b
    3378:	mov	v5.16b, v25.16b
    337c:	mov	v6.16b, v25.16b
    3380:	mov	v7.16b, v25.16b
    3384:	mov	v16.16b, v25.16b
    3388:	mov	v17.16b, v25.16b
    338c:	mov	v18.16b, v25.16b
    3390:	mov	v19.16b, v25.16b
    3394:	mov	v20.16b, v25.16b
    3398:	mov	v21.16b, v25.16b
    339c:	mov	v22.16b, v25.16b
    33a0:	mov	v23.16b, v25.16b
    33a4:	mov	v24.16b, v25.16b
    33a8:	b	324c <peak_fmla_f16_a16+0x10c>

Disassembly of section .fini:

# ===== peak_fmla_f16_a28: hot loop = the 158 instructions ending in the last backward branch =====

/home/adnancheema917/edge-llm-on-arm/work/bin/peak:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000033ac <peak_fmla_f16_a28>:
    33ac:	adrp	x1, 20000 <__data_start>
    33b0:	stp	d8, d9, [sp, #-128]!
    33b4:	add	x1, x1, #0x10
    33b8:	stp	d10, d11, [sp, #16]
    33bc:	stp	d12, d13, [sp, #32]
    33c0:	ldr	s0, [x1, #16]
    33c4:	stp	d14, d15, [sp, #48]
    33c8:	ldr	s1, [x1, #20]
    33cc:	cbz	x0, 375c <peak_fmla_f16_a28+0x3b0>
    33d0:	fcvt	h1, s1
    33d4:	fcvt	h0, s0
    33d8:	mov	x1, #0x0                   	// #0
    33dc:	movi	v14.8h, #0x0
    33e0:	mov	v13.16b, v14.16b
    33e4:	mov	v7.16b, v14.16b
    33e8:	fneg	h2, h1
    33ec:	dup	v0.8h, v0.h[0]
    33f0:	dup	v1.8h, v1.h[0]
    33f4:	mov	v16.16b, v14.16b
    33f8:	mov	v17.16b, v14.16b
    33fc:	mov	v18.16b, v14.16b
    3400:	mov	v19.16b, v14.16b
    3404:	mov	v20.16b, v14.16b
    3408:	dup	v2.8h, v2.h[0]
    340c:	mov	v21.16b, v14.16b
    3410:	mov	v22.16b, v14.16b
    3414:	mov	v23.16b, v14.16b
    3418:	mov	v24.16b, v14.16b
    341c:	mov	v25.16b, v14.16b
    3420:	mov	v26.16b, v14.16b
    3424:	mov	v27.16b, v14.16b
    3428:	mov	v28.16b, v14.16b
    342c:	mov	v29.16b, v14.16b
    3430:	mov	v30.16b, v14.16b
    3434:	mov	v31.16b, v14.16b
    3438:	mov	v8.16b, v14.16b
    343c:	mov	v9.16b, v14.16b
    3440:	mov	v10.16b, v14.16b
    3444:	mov	v11.16b, v14.16b
    3448:	mov	v12.16b, v14.16b
    344c:	mov	v3.16b, v14.16b
    3450:	mov	v4.16b, v14.16b
    3454:	mov	v5.16b, v14.16b
    3458:	mov	v6.16b, v14.16b
    345c:	nop
    3460:	mov	v15.16b, v31.16b
    3464:	add	x1, x1, #0x1
    3468:	fmla	v6.8h, v0.8h, v1.8h
    346c:	fmla	v15.8h, v0.8h, v1.8h
    3470:	fmla	v5.8h, v0.8h, v1.8h
    3474:	fmla	v15.8h, v0.8h, v2.8h
    3478:	fmla	v4.8h, v0.8h, v1.8h
    347c:	fmla	v3.8h, v0.8h, v1.8h
    3480:	fmla	v12.8h, v0.8h, v1.8h
    3484:	mov	v31.16b, v15.16b
    3488:	fmla	v11.8h, v0.8h, v1.8h
    348c:	fmla	v10.8h, v0.8h, v1.8h
    3490:	fmla	v9.8h, v0.8h, v1.8h
    3494:	fmla	v8.8h, v0.8h, v1.8h
    3498:	fmla	v30.8h, v0.8h, v1.8h
    349c:	fmla	v29.8h, v0.8h, v1.8h
    34a0:	fmla	v28.8h, v0.8h, v1.8h
    34a4:	fmla	v27.8h, v0.8h, v1.8h
    34a8:	fmla	v26.8h, v0.8h, v1.8h
    34ac:	fmla	v25.8h, v0.8h, v1.8h
    34b0:	fmla	v24.8h, v0.8h, v1.8h
    34b4:	fmla	v23.8h, v0.8h, v1.8h
    34b8:	fmla	v22.8h, v0.8h, v1.8h
    34bc:	fmla	v21.8h, v0.8h, v1.8h
    34c0:	fmla	v20.8h, v0.8h, v1.8h
    34c4:	fmla	v19.8h, v0.8h, v1.8h
    34c8:	fmla	v18.8h, v0.8h, v1.8h
    34cc:	fmla	v17.8h, v0.8h, v1.8h
    34d0:	fmla	v16.8h, v0.8h, v1.8h
    34d4:	fmla	v7.8h, v0.8h, v1.8h
    34d8:	fmla	v13.8h, v0.8h, v1.8h
    34dc:	fmla	v14.8h, v0.8h, v1.8h
    34e0:	fmla	v6.8h, v0.8h, v2.8h
    34e4:	fmla	v5.8h, v0.8h, v2.8h
    34e8:	fmla	v4.8h, v0.8h, v2.8h
    34ec:	fmla	v3.8h, v0.8h, v2.8h
    34f0:	fmla	v12.8h, v0.8h, v2.8h
    34f4:	fmla	v11.8h, v0.8h, v2.8h
    34f8:	fmla	v10.8h, v0.8h, v2.8h
    34fc:	fmla	v9.8h, v0.8h, v2.8h
    3500:	fmla	v8.8h, v0.8h, v2.8h
    3504:	fmla	v30.8h, v0.8h, v2.8h
    3508:	fmla	v29.8h, v0.8h, v2.8h
    350c:	fmla	v28.8h, v0.8h, v2.8h
    3510:	fmla	v27.8h, v0.8h, v2.8h
    3514:	fmla	v26.8h, v0.8h, v2.8h
    3518:	fmla	v25.8h, v0.8h, v2.8h
    351c:	fmla	v24.8h, v0.8h, v2.8h
    3520:	fmla	v23.8h, v0.8h, v2.8h
    3524:	fmla	v22.8h, v0.8h, v2.8h
    3528:	fmla	v21.8h, v0.8h, v2.8h
    352c:	fmla	v20.8h, v0.8h, v2.8h
    3530:	fmla	v19.8h, v0.8h, v2.8h
    3534:	fmla	v18.8h, v0.8h, v2.8h
    3538:	fmla	v17.8h, v0.8h, v2.8h
    353c:	fmla	v16.8h, v0.8h, v2.8h
    3540:	fmla	v7.8h, v0.8h, v2.8h
    3544:	fmla	v13.8h, v0.8h, v2.8h
    3548:	fmla	v14.8h, v0.8h, v2.8h
    354c:	cmp	x0, x1
    3550:	b.ne	3460 <peak_fmla_f16_a28+0xb4>  // b.any
    3554:	str	q7, [sp, #112]
    3558:	fcvtl	v15.4s, v6.4h
    355c:	movi	v0.4s, #0x0
    3560:	fcvtl2	v6.4s, v6.8h
    3564:	fcvtl	v2.4s, v5.4h
    3568:	fcvtl2	v5.4s, v5.8h
    356c:	fcvtl	v1.4s, v4.4h
    3570:	fcvtl2	v4.4s, v4.8h
    3574:	fcvtl	v7.4s, v12.4h
    3578:	fcvtl2	v12.4s, v12.8h
    357c:	fadd	v0.4s, v15.4s, v0.4s
    3580:	fcvtl	v15.4s, v3.4h
    3584:	fcvtl2	v3.4s, v3.8h
    3588:	fadd	v0.4s, v0.4s, v6.4s
    358c:	fcvtl	v6.4s, v11.4h
    3590:	fcvtl2	v11.4s, v11.8h
    3594:	fadd	v0.4s, v0.4s, v2.4s
    3598:	fcvtl	v2.4s, v9.4h
    359c:	fcvtl2	v9.4s, v9.8h
    35a0:	fadd	v0.4s, v0.4s, v5.4s
    35a4:	fcvtl	v5.4s, v8.4h
    35a8:	fcvtl2	v8.4s, v8.8h
    35ac:	fadd	v0.4s, v0.4s, v1.4s
    35b0:	fcvtl	v1.4s, v31.4h
    35b4:	fcvtl2	v31.4s, v31.8h
    35b8:	fadd	v0.4s, v0.4s, v4.4s
    35bc:	fcvtl	v4.4s, v30.4h
    35c0:	fcvtl2	v30.4s, v30.8h
    35c4:	fadd	v0.4s, v0.4s, v15.4s
    35c8:	fcvtl	v15.4s, v29.4h
    35cc:	fcvtl2	v29.4s, v29.8h
    35d0:	fadd	v0.4s, v0.4s, v3.4s
    35d4:	fcvtl	v3.4s, v28.4h
    35d8:	stp	q3, q7, [sp, #80]
    35dc:	fcvtl	v7.4s, v10.4h
    35e0:	fcvtl2	v10.4s, v10.8h
    35e4:	fcvtl2	v3.4s, v28.8h
    35e8:	fcvtl	v28.4s, v27.4h
    35ec:	fcvtl2	v27.4s, v27.8h
    35f0:	str	q7, [sp, #64]
    35f4:	ldr	q7, [sp, #96]
    35f8:	fadd	v0.4s, v0.4s, v7.4s
    35fc:	ldr	q7, [sp, #64]
    3600:	fadd	v0.4s, v0.4s, v12.4s
    3604:	fcvtl	v12.4s, v26.4h
    3608:	fcvtl2	v26.4s, v26.8h
    360c:	fadd	v0.4s, v0.4s, v6.4s
    3610:	fcvtl	v6.4s, v25.4h
    3614:	fcvtl2	v25.4s, v25.8h
    3618:	fadd	v0.4s, v0.4s, v11.4s
    361c:	fcvtl	v11.4s, v24.4h
    3620:	fcvtl2	v24.4s, v24.8h
    3624:	fadd	v0.4s, v0.4s, v7.4s
    3628:	fcvtl	v7.4s, v23.4h
    362c:	fcvtl2	v23.4s, v23.8h
    3630:	str	q7, [sp, #64]
    3634:	fadd	v0.4s, v0.4s, v10.4s
    3638:	ldr	q7, [sp, #112]
    363c:	fcvtl	v10.4s, v22.4h
    3640:	fcvtl2	v22.4s, v22.8h
    3644:	fadd	v0.4s, v0.4s, v2.4s
    3648:	fcvtl	v2.4s, v21.4h
    364c:	fcvtl2	v21.4s, v21.8h
    3650:	fadd	v0.4s, v0.4s, v9.4s
    3654:	fcvtl	v9.4s, v20.4h
    3658:	fcvtl2	v20.4s, v20.8h
    365c:	fadd	v0.4s, v0.4s, v5.4s
    3660:	fcvtl	v5.4s, v19.4h
    3664:	fcvtl2	v19.4s, v19.8h
    3668:	fadd	v0.4s, v0.4s, v8.4s
    366c:	fcvtl	v8.4s, v18.4h
    3670:	fcvtl2	v18.4s, v18.8h
    3674:	fadd	v0.4s, v0.4s, v1.4s
    3678:	fcvtl	v1.4s, v17.4h
    367c:	fcvtl2	v17.4s, v17.8h
    3680:	fadd	v0.4s, v0.4s, v31.4s
    3684:	fcvtl	v31.4s, v16.4h
    3688:	fcvtl2	v16.4s, v16.8h
    368c:	fadd	v0.4s, v0.4s, v4.4s
    3690:	fcvtl	v4.4s, v7.4h
    3694:	fcvtl2	v7.4s, v7.8h
    3698:	fadd	v0.4s, v0.4s, v30.4s
    369c:	fcvtl	v30.4s, v13.4h
    36a0:	fcvtl2	v13.4s, v13.8h
    36a4:	fadd	v0.4s, v0.4s, v15.4s
    36a8:	fcvtl	v15.4s, v14.4h
    36ac:	fcvtl2	v14.4s, v14.8h
    36b0:	fadd	v0.4s, v0.4s, v29.4s
    36b4:	ldr	q29, [sp, #80]
    36b8:	fadd	v0.4s, v0.4s, v29.4s
    36bc:	fadd	v0.4s, v0.4s, v3.4s
    36c0:	ldr	q3, [sp, #64]
    36c4:	fadd	v0.4s, v0.4s, v28.4s
    36c8:	fadd	v0.4s, v0.4s, v27.4s
    36cc:	fadd	v0.4s, v0.4s, v12.4s
    36d0:	fadd	v0.4s, v0.4s, v26.4s
    36d4:	fadd	v0.4s, v0.4s, v6.4s
    36d8:	fadd	v0.4s, v0.4s, v25.4s
    36dc:	fadd	v0.4s, v0.4s, v11.4s
    36e0:	fadd	v0.4s, v0.4s, v24.4s
    36e4:	fadd	v0.4s, v0.4s, v3.4s
    36e8:	fadd	v0.4s, v0.4s, v23.4s
    36ec:	fadd	v0.4s, v0.4s, v10.4s
    36f0:	ldp	d10, d11, [sp, #16]
    36f4:	fadd	v0.4s, v0.4s, v22.4s
    36f8:	fadd	v0.4s, v0.4s, v2.4s
    36fc:	fadd	v0.4s, v0.4s, v21.4s
    3700:	fadd	v0.4s, v0.4s, v9.4s
    3704:	fadd	v0.4s, v0.4s, v20.4s
    3708:	fadd	v0.4s, v0.4s, v5.4s
    370c:	fadd	v0.4s, v0.4s, v19.4s
    3710:	fadd	v0.4s, v0.4s, v8.4s
    3714:	fadd	v0.4s, v0.4s, v18.4s
    3718:	fadd	v0.4s, v0.4s, v1.4s
    371c:	fadd	v0.4s, v0.4s, v17.4s
    3720:	fadd	v0.4s, v0.4s, v31.4s
    3724:	fadd	v0.4s, v0.4s, v16.4s
    3728:	fadd	v0.4s, v0.4s, v4.4s
    372c:	fadd	v0.4s, v0.4s, v7.4s
    3730:	fadd	v0.4s, v0.4s, v30.4s
    3734:	fadd	v0.4s, v0.4s, v13.4s
    3738:	ldp	d12, d13, [sp, #32]
    373c:	fadd	v0.4s, v0.4s, v15.4s
    3740:	fadd	v0.4s, v0.4s, v14.4s
    3744:	ldp	d14, d15, [sp, #48]
    3748:	ldp	d8, d9, [sp], #128
    374c:	faddp	v0.4s, v0.4s, v0.4s
    3750:	faddp	v0.4s, v0.4s, v0.4s
    3754:	fmov	w0, s0
    3758:	ret
    375c:	movi	v14.8h, #0x0
    3760:	mov	v13.16b, v14.16b
    3764:	mov	v16.16b, v14.16b
    3768:	str	q14, [sp, #112]
    376c:	mov	v17.16b, v14.16b
    3770:	mov	v18.16b, v14.16b
    3774:	mov	v19.16b, v14.16b
    3778:	mov	v20.16b, v14.16b
    377c:	mov	v21.16b, v14.16b
    3780:	mov	v22.16b, v14.16b
    3784:	mov	v23.16b, v14.16b
    3788:	mov	v24.16b, v14.16b
    378c:	mov	v25.16b, v14.16b
    3790:	mov	v26.16b, v14.16b
    3794:	mov	v27.16b, v14.16b
    3798:	mov	v28.16b, v14.16b
    379c:	mov	v29.16b, v14.16b
    37a0:	mov	v30.16b, v14.16b
    37a4:	mov	v31.16b, v14.16b
    37a8:	mov	v8.16b, v14.16b
    37ac:	mov	v9.16b, v14.16b
    37b0:	mov	v10.16b, v14.16b
    37b4:	mov	v11.16b, v14.16b
    37b8:	mov	v12.16b, v14.16b
    37bc:	mov	v3.16b, v14.16b
    37c0:	mov	v4.16b, v14.16b
    37c4:	mov	v5.16b, v14.16b
    37c8:	mov	v6.16b, v14.16b
    37cc:	b	3558 <peak_fmla_f16_a28+0x1ac>

Disassembly of section .fini:
