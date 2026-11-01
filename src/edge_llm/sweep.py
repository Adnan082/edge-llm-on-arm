"""Names and enumeration of sweep points (ARCHITECTURE.md §3), read from configs/sweep.yaml.

    config_id = <model>_<quant>_<build>_t<threads>_<test>    small_Q4_0_kleidiai_t8_pp512
    pair_id   = <model>_<quant>_t<threads>_<test>            small_Q4_0_t8_pp512

`test` is `pp<N>` (prefill of N tokens), `tg<N>` (N generated tokens from an empty context) or
`tg<N>d<D>` (the same after a D-token context). No hardware calls: runs in CI.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

BUILDS = ("baseline", "kleidiai")

_TEST_RE = re.compile(r"^(?:pp(?P<pp>\d+)|tg(?P<tg>\d+)(?:d(?P<depth>\d+))?)$")
_CONFIG_RE = re.compile(
    r"^(?P<model>[a-z][a-z0-9]*)_(?P<quant>[A-Za-z0-9_]+?)_(?P<build>baseline|kleidiai)"
    r"_t(?P<threads>\d+)_(?P<test>pp\d+|tg\d+(?:d\d+)?)$"
)


@dataclass(frozen=True)
class Test:
    kind: str  # "pp" or "tg"
    tokens: int  # prompt tokens (pp) or generated tokens (tg)
    depth: int = 0  # context filled before a tg test

    @property
    def name(self) -> str:
        return f"{self.kind}{self.tokens}" + (f"d{self.depth}" if self.depth else "")

    @property
    def phase(self) -> str:
        return "prefill" if self.kind == "pp" else "decode"


def parse_test(name: str) -> Test:
    m = _TEST_RE.match(name)
    if not m:
        raise ValueError(f"not a test name: {name!r}")
    if m.group("pp"):
        return Test("pp", int(m.group("pp")))
    return Test("tg", int(m.group("tg")), int(m.group("depth") or 0))


@dataclass(frozen=True)
class Point:
    model: str
    quant: str
    build: str
    threads: int
    test: str

    @property
    def config_id(self) -> str:
        return config_id(self.model, self.quant, self.build, self.threads, self.test)

    @property
    def pair_id(self) -> str:
        return pair_id(self.model, self.quant, self.threads, self.test)


def config_id(model: str, quant: str, build: str, threads: int, test: str) -> str:
    return f"{model}_{quant}_{build}_t{threads}_{test}"


def pair_id(model: str, quant: str, threads: int, test: str) -> str:
    return f"{model}_{quant}_t{threads}_{test}"


def parse_config_id(text: str) -> Point:
    m = _CONFIG_RE.match(text)
    if not m:
        raise ValueError(f"not a config_id: {text!r}")
    parse_test(m.group("test"))
    return Point(
        m.group("model"),
        m.group("quant"),
        m.group("build"),
        int(m.group("threads")),
        m.group("test"),
    )


def build_order(pair_index: int) -> tuple[str, str]:
    """Which build runs first alternates from one pair to the next (CLAUDE.md §7.7)."""
    return BUILDS if pair_index % 2 == 0 else (BUILDS[1], BUILDS[0])


def cpu_mask(threads: int) -> str:
    """llama-bench --cpu-mask for cores 0..threads-1 (hex, bit i = core i)."""
    return hex((1 << threads) - 1)


def taskset_cpus(threads: int) -> str:
    return f"0-{threads - 1}"


@dataclass(frozen=True)
class Pair:
    """The two builds' runs of one (model, quant, threads, test): the unit the sweep walks."""

    index: int  # position in the set's pair list; decides which build goes first
    model: str
    quant: str
    threads: int
    test: str

    @property
    def pair_id(self) -> str:
        return pair_id(self.model, self.quant, self.threads, self.test)

    def points(self) -> list[Point]:
        """The two points in running order."""
        return [
            Point(self.model, self.quant, b, self.threads, self.test)
            for b in build_order(self.index)
        ]


def tests_for(cfg: dict, threads: int) -> list[str]:
    """Test names run at a thread count: every prefill length, decode, and decode at depth."""
    tests = [f"pp{p}" for p in cfg["prefill_prompt_lengths"]]
    tests.append(f"tg{cfg['decode_tokens']}")
    depth = cfg.get("decode_depth")
    if depth and threads in cfg["decode_depth_threads"]:
        tests.append(f"tg{cfg['decode_tokens']}d{depth}")
    return tests


def pairs(cfg: dict, set_name: str) -> list[Pair]:
    """All pairs of the `full` sweep or of the `pilot`, in running order."""
    if set_name == "full":
        specs = [
            (m, q, t, test)
            for m in cfg["models"]
            for q in cfg["quants"]
            for t in cfg["threads"]
            for test in tests_for(cfg, t)
        ]
    elif set_name == "pilot":
        pilot = cfg["pilot"]
        specs = [
            (m, q, t, test)
            for m in pilot["models"]
            for q in pilot["quants"]
            for t in pilot["threads"]
            for test in pilot["tests"]
        ]
        specs += [(p["model"], p["quant"], p["threads"], p["test"]) for p in pilot["extra_points"]]
    else:
        raise ValueError(f"unknown set {set_name!r}: use pilot or full")
    for m, q, t, test in specs:
        if m not in cfg["models"] or q not in cfg["quants"] or t not in cfg["threads"]:
            raise ValueError(
                f"{pair_id(m, q, t, test)} is not in the sweep's models/quants/threads"
            )
        parse_test(test)
    if len(set(specs)) != len(specs):
        raise ValueError("duplicate pairs in the sweep definition")
    return [Pair(i, *spec) for i, spec in enumerate(specs)]


def repetitions(cfg: dict, pair: Pair) -> int:
    """5 repetitions, or 3 for a pair listed in `slow_points`."""
    slow = {s["point"] for s in cfg.get("slow_points") or []}
    return cfg["slow_repetitions"] if pair.pair_id in slow else cfg["repetitions"]
