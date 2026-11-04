# ===== dot_smmla_a4: hot loop = the 13 instructions of the innermost conditional backward branch holding the expected instruction (smmla) =====
#   ldp q4, q5, [x0]
#   add x0, x0, #0x40
#   ldp q7, q16, [x2]
#   ldur q6, [x0, #-32]
#   smmla v0.4s, v4.16b, v7.16b
#   ldur q4, [x0, #-16]
#   smmla v3.4s, v5.16b, v16.16b
#   ldp q7, q5, [x2, #32]
#   add x2, x2, #0x40
#   smmla v2.4s, v6.16b, v7.16b
#   smmla v1.4s, v4.16b, v5.16b
#   cmp x3, x0
#   b.ne 5344 <dot_smmla_a4+0x54>
# ===== whole function =====

/home/adnancheema917/edge-llm-on-arm/work/bin/dot_int8:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

00000000000052f0 <dot_smmla_a4>:
    52f0:	cmp	x3, #0x0
    52f4:	b.le	5394 <dot_smmla_a4+0xa4>
    52f8:	lsl	x9, x4, #1
    52fc:	add	x7, x2, x3, lsl #4
    5300:	mov	x6, x2
    5304:	sub	x8, x9, #0x1
    5308:	mov	x5, x0
    530c:	and	x8, x8, #0xffffffffffffffc0
    5310:	add	x8, x8, #0x40
    5314:	nop
    5318:	nop
    531c:	nop
    5320:	cmp	x4, #0x0
    5324:	b.le	5398 <dot_smmla_a4+0xa8>
    5328:	movi	v1.4s, #0x0
    532c:	mov	x2, x1
    5330:	add	x3, x8, x5
    5334:	mov	x0, x5
    5338:	mov	v2.16b, v1.16b
    533c:	mov	v3.16b, v1.16b
    5340:	mov	v0.16b, v1.16b
    5344:	ldp	q4, q5, [x0]
    5348:	add	x0, x0, #0x40
    534c:	ldp	q7, q16, [x2]
    5350:	ldur	q6, [x0, #-32]
    5354:	smmla	v0.4s, v4.16b, v7.16b
    5358:	ldur	q4, [x0, #-16]
    535c:	smmla	v3.4s, v5.16b, v16.16b
    5360:	ldp	q7, q5, [x2, #32]
    5364:	add	x2, x2, #0x40
    5368:	smmla	v2.4s, v6.16b, v7.16b
    536c:	smmla	v1.4s, v4.16b, v5.16b
    5370:	cmp	x3, x0
    5374:	b.ne	5344 <dot_smmla_a4+0x54>  // b.any
    5378:	add	v0.4s, v0.4s, v3.4s
    537c:	add	v0.4s, v0.4s, v2.4s
    5380:	add	v0.4s, v0.4s, v1.4s
    5384:	add	x5, x5, x9
    5388:	str	q0, [x6], #16
    538c:	cmp	x7, x6
    5390:	b.ne	5320 <dot_smmla_a4+0x30>  // b.any
    5394:	ret
    5398:	movi	v0.4s, #0x0
    539c:	b	5384 <dot_smmla_a4+0x94>

Disassembly of section .fini:
