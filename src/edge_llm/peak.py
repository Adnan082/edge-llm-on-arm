"""Peak-throughput helpers: operations per instruction, C(t), and the disassembly check.

micro/peak.cpp reports instructions per second; this module turns them into operations per
second (CLAUDE.md §8: one multiply-accumulate = 2 operations). The constants below are the one
place those numbers live. No hardware calls: everything here runs in CI.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

PEAK_CLASSES = ("sdot", "smmla", "fmla_f16", "fmlal", "fma32")

# Operations per instruction at 128-bit vectors (§8):
#   SDOT      16 int8 products x 2          = 32
#   SMMLA     (2x8 times 8x2) = 32 MACs x 2 = 64
#   FP16 FMLA 8 half-precision MACs x 2     = 16
#   FMLALB or FMLALT: 4 widening MACs x 2   = 8 (each instruction does half of the elements)
#   F32 FMLA  4 single-precision MACs x 2   = 8 (the ceiling for attention, ADR-020)
OPS_PER_INSTRUCTION: dict[str, int] = {
    "sdot": 32,
    "smmla": 64,
    "fmla_f16": 16,
    "fmlal": 8,
    "fma32": 8,
}

# SVE instructions do more work per instruction at wider vectors; NEON ones never do.
SVE_CLASSES = ("fmlal",)

# Independent dependency chains per loop, all run at every thread count (ADR-022). C(t) is the
# best median over these, as B(t) is over the read variants: a peak test can only under-measure,
# and on the VM more chains raise the 1-thread peak of some classes, so no count is fixed in
# advance. 28 is the most that fit in registers next to the operands.
CHAIN_COUNTS = (8, 16, 28)

# What must be in each hot loop: (regex on "mnemonic operands", label). One iteration holds
# exactly `instr_per_iter` of them (checked in check_loop).
EXPECTED_IN_LOOP: dict[str, list[tuple[str, str]]] = {
    "sdot": [(r"^sdot\s", "sdot")],
    "smmla": [(r"^smmla\s", "smmla")],
    "fmla_f16": [(r"^fmla\s+v\d+\.8h", "fmla .8h")],
    "fma32": [(r"^fmla\s+v\d+\.4s", "fmla .4s")],
    # half of the chains use the bottom form, half the top form
    "fmlal": [(r"^fmlalb\s", "fmlalb"), (r"^fmlalt\s", "fmlalt")],
}
# anything that touches memory means the loop is not register-only
MEMORY_MNEMONIC_RE = re.compile(r"^(ld|st|prfm|ldnp|stnp|ldp|stp|ldr|str|ldur|stur)\w*\s")


def ops_per_instruction(instr_class: str, sve_vector_bits: int = 128) -> float:
    """Operations per instruction of a class; SVE classes scale with the vector length."""
    base = OPS_PER_INSTRUCTION[instr_class]
    if instr_class in SVE_CLASSES:
        return base * sve_vector_bits / 128
    return float(base)


def valid_chain_counts(disasm: dict) -> dict[str, set[int]]:
    """{class: chain counts whose loop passed the disassembly check} from a record's `disasm`."""
    return {
        cls: {int(c["accumulators"]) for c in d.get("checks", []) if c.get("ok") is True}
        for cls, d in disasm.items()
    }


def c_summary(points: Iterable, valid: dict[str, set[int]]) -> dict[str, dict[str, dict]]:
    """{class: {str(threads): {...}}}: C(t) and which chain count gave it (ADR-022).

    A point counts only if its loop passed the disassembly check (`valid`). C(t) is the best
    median over the counting chain counts; a tie goes to the smaller count. `by_accumulators`
    keeps every median, counting or not, as information. A class with no counting point at some
    thread count has no entry there.
    """
    medians: dict[str, dict[int, dict[int, float]]] = {}
    for p in points:
        medians.setdefault(p.instr_class, {}).setdefault(p.threads, {})[p.accumulators] = p.median
    out: dict[str, dict[str, dict]] = {}
    for cls in PEAK_CLASSES:
        for t, by_acc in sorted(medians.get(cls, {}).items()):
            counting = {a: m for a, m in by_acc.items() if a in valid.get(cls, set())}
            if not counting:
                continue
            best = min(counting, key=lambda a: (-counting[a], a))
            out.setdefault(cls, {})[str(t)] = {
                "accumulators": best,
                "median": counting[best],
                "by_accumulators": {str(a): by_acc[a] for a in sorted(by_acc)},
            }
    return out


def c_of_t(summary: dict[str, dict[str, dict]]) -> dict[str, dict[int, float]]:
    """{class: {threads: C(t) in ops/s}} from `c_summary` (or a record's `c_of_t` field)."""
    return {cls: {int(t): v["median"] for t, v in by_t.items()} for cls, by_t in summary.items()}


# --- disassembly check ----------------------------------------------------------------------

INSN_RE = re.compile(r"^\s*([0-9a-f]+):\s+(\S.*)$")
_BRANCH_TARGET_RE = re.compile(r"\b([0-9a-f]{3,})\s+<")


def parse_instructions(objdump_text: str) -> list[tuple[int, str]]:
    """(address, "mnemonic operands") for each line of `objdump -d --no-show-raw-insn`."""
    out = []
    for line in objdump_text.splitlines():
        m = INSN_RE.match(line)
        if m:
            out.append(
                (int(m.group(1), 16), re.sub(r"\s+", " ", m.group(2).split("//")[0]).strip())
            )
    return out


CONDITIONAL_BRANCHES = ("cbz", "cbnz", "tbz", "tbnz")


def _is_conditional_branch(text: str) -> bool:
    mnemonic = text.split(" ", 1)[0]
    return mnemonic.startswith("b.") or mnemonic in CONDITIONAL_BRANCHES


def expected_pattern(instr_class: str) -> str:
    """One regex that matches any instruction a loop of this class must contain."""
    return "|".join(f"(?:{pattern})" for pattern, _ in EXPECTED_IN_LOOP[instr_class])


def hot_loop(insns: Sequence[tuple[int, str]], contains: str | None = None) -> list[str]:
    """The instructions of a loop: from the target of a conditional backward branch to it.

    The one place loops are found (peak and bandwidth both use it). A loop ends in a conditional
    backward branch (b.<cond>, cbz, cbnz, tbz, tbnz). An unconditional `b` that jumps backward is
    not a loop: GCC uses one for the zero-iteration path that returns to the code after the loop.

    A function can have several loops. With `contains` (a regex), loops holding a matching
    instruction are preferred; among the candidates the innermost (shortest) wins. If no loop
    matches, the innermost loop is still returned, so the caller can report what it holds.
    An empty list means the function has no conditional backward branch at all.
    """
    spans = []
    for addr, text in insns:
        if not _is_conditional_branch(text):
            continue
        m = _BRANCH_TARGET_RE.search(text)
        if m and int(m.group(1), 16) < addr:
            spans.append((int(m.group(1), 16), addr))
    if not spans:
        return []

    def body(span: tuple[int, int]) -> list[str]:
        return [t for a, t in insns if span[0] <= a <= span[1]]

    pool = spans
    if contains:
        matching = [sp for sp in spans if any(re.search(contains, t) for t in body(sp))]
        pool = matching or spans
    return body(min(pool, key=lambda sp: (sp[1] - sp[0], -sp[1])))


def check_loop(
    instr_class: str, loop: Sequence[str], accumulators: int, instr_per_iter: int
) -> dict:
    """Does the hot loop hold the expected instruction, the count the program assumed, no memory?"""
    counts: dict[str, int] = {}
    for pattern, label in EXPECTED_IN_LOOP[instr_class]:
        counts[label] = sum(1 for t in loop if re.match(pattern, t))
    in_loop = sum(counts.values())
    memory_ops = [t for t in loop if MEMORY_MNEMONIC_RE.match(t)]
    if instr_class == "fmlal":
        shape_ok = counts["fmlalb"] == counts["fmlalt"] == accumulators // 2
    else:
        shape_ok = True
    return {
        "accumulators": accumulators,
        "loop_instructions": len(loop),
        "counts": counts,
        "expected_per_iteration": instr_per_iter,
        "memory_instructions": memory_ops,
        "ok": bool(loop) and in_loop == instr_per_iter and shape_ok and not memory_ops,
    }
