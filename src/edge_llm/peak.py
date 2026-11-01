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

# Independent dependency chains per loop: the roofline uses BASE_ACCUMULATORS; the two others are
# the ladder that shows the base is neither latency-bound (28 must not beat it) nor trivially so
# (8 should be slower). 28 is the most that fit in registers next to the operands.
BASE_ACCUMULATORS = 16
LADDER_ACCUMULATORS = (8, 16, 28)
ACC_TOLERANCE = 0.03  # more chains may raise the peak by at most 3 %

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


def c_of_t(points: Iterable) -> dict[str, dict[int, float]]:
    """{class: {threads: median ops/s}} from the base-accumulator points of a peak record."""
    out: dict[str, dict[int, float]] = {}
    for p in points:
        if p.accumulators == BASE_ACCUMULATORS:
            out.setdefault(p.instr_class, {})[p.threads] = p.median
    return out


def ladder_summary(points: Iterable) -> list[dict]:
    """Per class, the 1-thread median at each accumulator count and whether 28 beats 16.

    The check passes if the largest ladder count raises the base result by at most ACC_TOLERANCE.
    """
    by_class: dict[str, dict[int, float]] = {}
    for p in points:
        if p.threads == 1:
            by_class.setdefault(p.instr_class, {})[p.accumulators] = p.median
    out = []
    for cls in PEAK_CLASSES:
        med = by_class.get(cls)
        if not med:
            continue
        top = max(LADDER_ACCUMULATORS)
        if BASE_ACCUMULATORS not in med or top not in med:
            raise ValueError(f"{cls}: need 1-thread results at {BASE_ACCUMULATORS} and {top}")
        ratio = med[top] / med[BASE_ACCUMULATORS]
        out.append(
            {
                "instr_class": cls,
                "median_ops_per_s_by_accumulators": {str(k): med[k] for k in sorted(med)},
                f"ratio_{top}_over_{BASE_ACCUMULATORS}": ratio,
                "tolerance": ACC_TOLERANCE,
                "pass": ratio <= 1.0 + ACC_TOLERANCE,
            }
        )
    return out


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


def hot_loop(insns: Sequence[tuple[int, str]]) -> list[str]:
    """Instructions from the target of the last backward branch to that branch, inclusive."""
    for idx in range(len(insns) - 1, -1, -1):
        addr, text = insns[idx]
        mnemonic = text.split(" ", 1)[0]
        if not (mnemonic.startswith("b.") or mnemonic in ("b", "cbnz", "cbz", "tbnz", "tbz")):
            continue
        m = _BRANCH_TARGET_RE.search(text)
        if not m:
            continue
        target = int(m.group(1), 16)
        if target < addr:
            return [t for a, t in insns if target <= a <= addr]
    return []


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
