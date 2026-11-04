# ===== dot_sdot_a8: hot loop = the 21 instructions of the innermost conditional backward branch holding the expected instruction (sdot v-form) =====
#   ldp q18, q16, [x0]
#   ldp q19, q20, [x2]
#   ldr q17, [x0, #32]
#   sdot v0.4s, v18.16b, v19.16b
#   sdot v7.4s, v16.16b, v20.16b
#   ldp q19, q20, [x2, #32]
#   ldp q18, q16, [x0, #48]
#   sdot v6.4s, v17.16b, v19.16b
#   sdot v5.4s, v18.16b, v20.16b
#   ldp q19, q20, [x2, #64]
#   ldp q17, q18, [x0, #80]
#   add x0, x0, #0x80
#   sdot v4.4s, v16.16b, v19.16b
#   ldur q16, [x0, #-16]
#   sdot v3.4s, v17.16b, v20.16b
#   ldp q19, q17, [x2, #96]
#   add x2, x2, #0x80
#   sdot v2.4s, v18.16b, v19.16b
#   sdot v1.4s, v16.16b, v17.16b
#   cmp x3, x0
#   b.ne 5260 <dot_sdot_a8+0x5c>
# ===== whole function =====

/home/adnancheema917/edge-llm-on-arm/work/bin/dot_int8:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000005204 <dot_sdot_a8>:
    5204:	cmp	x3, #0x0
    5208:	b.le	52e4 <dot_sdot_a8+0xe0>
    520c:	sub	x8, x4, #0x1
    5210:	add	x7, x2, x3, lsl #2
    5214:	mov	x6, x2
    5218:	and	x8, x8, #0xffffffffffffff80
    521c:	mov	x5, x0
    5220:	add	x8, x8, #0x80
    5224:	cmp	x4, #0x0
    5228:	b.le	52e8 <dot_sdot_a8+0xe4>
    522c:	movi	v1.4s, #0x0
    5230:	mov	x2, x1
    5234:	add	x3, x8, x5
    5238:	mov	x0, x5
    523c:	mov	v2.16b, v1.16b
    5240:	mov	v3.16b, v1.16b
    5244:	mov	v4.16b, v1.16b
    5248:	mov	v5.16b, v1.16b
    524c:	mov	v6.16b, v1.16b
    5250:	mov	v7.16b, v1.16b
    5254:	mov	v0.16b, v1.16b
    5258:	nop
    525c:	nop
    5260:	ldp	q18, q16, [x0]
    5264:	ldp	q19, q20, [x2]
    5268:	ldr	q17, [x0, #32]
    526c:	sdot	v0.4s, v18.16b, v19.16b
    5270:	sdot	v7.4s, v16.16b, v20.16b
    5274:	ldp	q19, q20, [x2, #32]
    5278:	ldp	q18, q16, [x0, #48]
    527c:	sdot	v6.4s, v17.16b, v19.16b
    5280:	sdot	v5.4s, v18.16b, v20.16b
    5284:	ldp	q19, q20, [x2, #64]
    5288:	ldp	q17, q18, [x0, #80]
    528c:	add	x0, x0, #0x80
    5290:	sdot	v4.4s, v16.16b, v19.16b
    5294:	ldur	q16, [x0, #-16]
    5298:	sdot	v3.4s, v17.16b, v20.16b
    529c:	ldp	q19, q17, [x2, #96]
    52a0:	add	x2, x2, #0x80
    52a4:	sdot	v2.4s, v18.16b, v19.16b
    52a8:	sdot	v1.4s, v16.16b, v17.16b
    52ac:	cmp	x3, x0
    52b0:	b.ne	5260 <dot_sdot_a8+0x5c>  // b.any
    52b4:	add	v0.4s, v0.4s, v7.4s
    52b8:	add	v0.4s, v0.4s, v6.4s
    52bc:	add	v0.4s, v0.4s, v5.4s
    52c0:	add	v0.4s, v0.4s, v4.4s
    52c4:	add	v0.4s, v0.4s, v3.4s
    52c8:	add	v0.4s, v0.4s, v2.4s
    52cc:	add	v0.4s, v0.4s, v1.4s
    52d0:	addv	s0, v0.4s
    52d4:	add	x5, x5, x4
    52d8:	str	s0, [x6], #4
    52dc:	cmp	x7, x6
    52e0:	b.ne	5224 <dot_sdot_a8+0x20>  // b.any
    52e4:	ret
    52e8:	fmov	s0, wzr
    52ec:	b	52d4 <dot_sdot_a8+0xd0>

Disassembly of section .fini:
