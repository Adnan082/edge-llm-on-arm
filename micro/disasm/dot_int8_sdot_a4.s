# ===== dot_sdot_a4: hot loop = the 13 instructions of the innermost conditional backward branch holding the expected instruction (sdot v-form) =====
#   ldp q4, q5, [x0]
#   add x0, x0, #0x40
#   ldp q7, q16, [x2]
#   ldur q6, [x0, #-32]
#   sdot v0.4s, v4.16b, v7.16b
#   sdot v3.4s, v5.16b, v16.16b
#   ldur q4, [x0, #-16]
#   ldp q7, q5, [x2, #32]
#   add x2, x2, #0x40
#   sdot v2.4s, v6.16b, v7.16b
#   sdot v1.4s, v4.16b, v5.16b
#   cmp x3, x0
#   b.ne 51a4 <dot_sdot_a4+0x44>
# ===== whole function =====

/home/adnancheema917/edge-llm-on-arm/work/bin/dot_int8:     file format elf64-littleaarch64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000005160 <dot_sdot_a4>:
    5160:	cmp	x3, #0x0
    5164:	b.le	51f8 <dot_sdot_a4+0x98>
    5168:	sub	x8, x4, #0x1
    516c:	add	x7, x2, x3, lsl #2
    5170:	mov	x6, x2
    5174:	and	x8, x8, #0xffffffffffffffc0
    5178:	mov	x5, x0
    517c:	add	x8, x8, #0x40
    5180:	cmp	x4, #0x0
    5184:	b.le	51fc <dot_sdot_a4+0x9c>
    5188:	movi	v1.4s, #0x0
    518c:	mov	x2, x1
    5190:	add	x3, x8, x5
    5194:	mov	x0, x5
    5198:	mov	v2.16b, v1.16b
    519c:	mov	v3.16b, v1.16b
    51a0:	mov	v0.16b, v1.16b
    51a4:	ldp	q4, q5, [x0]
    51a8:	add	x0, x0, #0x40
    51ac:	ldp	q7, q16, [x2]
    51b0:	ldur	q6, [x0, #-32]
    51b4:	sdot	v0.4s, v4.16b, v7.16b
    51b8:	sdot	v3.4s, v5.16b, v16.16b
    51bc:	ldur	q4, [x0, #-16]
    51c0:	ldp	q7, q5, [x2, #32]
    51c4:	add	x2, x2, #0x40
    51c8:	sdot	v2.4s, v6.16b, v7.16b
    51cc:	sdot	v1.4s, v4.16b, v5.16b
    51d0:	cmp	x3, x0
    51d4:	b.ne	51a4 <dot_sdot_a4+0x44>  // b.any
    51d8:	add	v0.4s, v0.4s, v3.4s
    51dc:	add	v0.4s, v0.4s, v2.4s
    51e0:	add	v0.4s, v0.4s, v1.4s
    51e4:	addv	s0, v0.4s
    51e8:	add	x5, x5, x4
    51ec:	str	s0, [x6], #4
    51f0:	cmp	x7, x6
    51f4:	b.ne	5180 <dot_sdot_a4+0x20>  // b.any
    51f8:	ret
    51fc:	fmov	s0, wzr
    5200:	b	51e8 <dot_sdot_a4+0x88>

Disassembly of section .fini:
