# ===== dot_smmla_a8: hot loop = the 21 instructions of the innermost conditional backward branch holding the expected instruction (smmla) =====
#   ldp q18, q16, [x0]
#   ldp q19, q20, [x2]
#   ldr q17, [x0, #32]
#   smmla v0.4s, v18.16b, v19.16b
#   smmla v7.4s, v16.16b, v20.16b
#   ldp q19, q20, [x2, #32]
#   ldp q18, q16, [x0, #48]
#   smmla v6.4s, v17.16b, v19.16b
#   smmla v5.4s, v18.16b, v20.16b
#   ldp q19, q20, [x2, #64]
#   ldp q17, q18, [x0, #80]
#   add x0, x0, #0x80
#   smmla v4.4s, v16.16b, v19.16b
#   ldur q16, [x0, #-16]
#   smmla v3.4s, v17.16b, v20.16b
#   ldp q19, q17, [x2, #96]
#   add x2, x2, #0x80
#   smmla v2.4s, v18.16b, v19.16b
#   smmla v1.4s, v16.16b, v17.16b
#   cmp x3, x0
#   b.ne 5400 <dot_smmla_a8+0x60>
# ===== whole function =====

/home/adnancheema917/edge-llm-on-arm/work/bin/dot_int8:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000053a0 <dot_smmla_a8>:
    53a0:	cmp	x3, #0x0
    53a4:	b.le	5480 <dot_smmla_a8+0xe0>
    53a8:	lsl	x9, x4, #1
    53ac:	add	x7, x2, x3, lsl #4
    53b0:	mov	x6, x2
    53b4:	sub	x8, x9, #0x1
    53b8:	mov	x5, x0
    53bc:	and	x8, x8, #0xffffffffffffff80
    53c0:	add	x8, x8, #0x80
    53c4:	cmp	x4, #0x0
    53c8:	b.le	5484 <dot_smmla_a8+0xe4>
    53cc:	movi	v1.4s, #0x0
    53d0:	mov	x2, x1
    53d4:	add	x3, x8, x5
    53d8:	mov	x0, x5
    53dc:	mov	v2.16b, v1.16b
    53e0:	mov	v3.16b, v1.16b
    53e4:	mov	v4.16b, v1.16b
    53e8:	mov	v5.16b, v1.16b
    53ec:	mov	v6.16b, v1.16b
    53f0:	mov	v7.16b, v1.16b
    53f4:	mov	v0.16b, v1.16b
    53f8:	nop
    53fc:	nop
    5400:	ldp	q18, q16, [x0]
    5404:	ldp	q19, q20, [x2]
    5408:	ldr	q17, [x0, #32]
    540c:	smmla	v0.4s, v18.16b, v19.16b
    5410:	smmla	v7.4s, v16.16b, v20.16b
    5414:	ldp	q19, q20, [x2, #32]
    5418:	ldp	q18, q16, [x0, #48]
    541c:	smmla	v6.4s, v17.16b, v19.16b
    5420:	smmla	v5.4s, v18.16b, v20.16b
    5424:	ldp	q19, q20, [x2, #64]
    5428:	ldp	q17, q18, [x0, #80]
    542c:	add	x0, x0, #0x80
    5430:	smmla	v4.4s, v16.16b, v19.16b
    5434:	ldur	q16, [x0, #-16]
    5438:	smmla	v3.4s, v17.16b, v20.16b
    543c:	ldp	q19, q17, [x2, #96]
    5440:	add	x2, x2, #0x80
    5444:	smmla	v2.4s, v18.16b, v19.16b
    5448:	smmla	v1.4s, v16.16b, v17.16b
    544c:	cmp	x3, x0
    5450:	b.ne	5400 <dot_smmla_a8+0x60>  // b.any
    5454:	add	v0.4s, v0.4s, v7.4s
    5458:	add	v0.4s, v0.4s, v6.4s
    545c:	add	v0.4s, v0.4s, v5.4s
    5460:	add	v0.4s, v0.4s, v4.4s
    5464:	add	v0.4s, v0.4s, v3.4s
    5468:	add	v0.4s, v0.4s, v2.4s
    546c:	add	v0.4s, v0.4s, v1.4s
    5470:	add	x5, x5, x9
    5474:	str	q0, [x6], #16
    5478:	cmp	x7, x6
    547c:	b.ne	53c4 <dot_smmla_a8+0x24>  // b.any
    5480:	ret
    5484:	movi	v0.4s, #0x0
    5488:	b	5470 <dot_smmla_a8+0xd0>

Disassembly of section .fini:
