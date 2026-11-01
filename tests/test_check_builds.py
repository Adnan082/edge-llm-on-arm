"""bench/check_builds.py: parsing llama.cpp log output."""

from bench import check_builds as cb

LOG = """\
load_tensors: offloading 0 repeating layers to GPU
load_tensors:   CPU_Mapped model buffer size =   182.34 MiB
load_tensors:  CPU_KLEIDIAI model buffer size =   215.09 MiB
load_tensors:    CPU_REPACK model buffer size =    12.00 MiB
load_tensors:    CPU_REPACK model buffer size =     0.50 MiB
kleidiai: no compatible q4 kernels found for CPU features mask 3
some unrelated line
"""

SYSTEM = (
    "main: llama threadpool init\n"
    "system_info: n_threads = 8 (n_threads_batch = 8) / 8 | CPU : NEON = 1 | ARM_FMA = 1 | "
    "FP16_VA = 1 | MATMUL_INT8 = 1 | DOTPROD = 1 | SVE = 1 | SVE_CNT = 16 | OPENMP = 1 | "
    "REPACK = 1 | KLEIDIAI = 1 | \n"
)


def test_parse_buffers_by_type_and_summed_when_repeated():
    b = cb.parse_buffers(LOG)
    assert b == {"CPU_Mapped": 182.34, "CPU_KLEIDIAI": 215.09, "CPU_REPACK": 12.5}


def test_parse_system_info_line_and_features():
    line, feats = cb.parse_system_info(SYSTEM)
    assert line.startswith("system_info: n_threads = 8")
    assert feats["KLEIDIAI"] == "1" and feats["SVE_CNT"] == "16" and feats["REPACK"] == "1"
    assert feats["MATMUL_INT8"] == "1"


def test_kleidiai_flag_absent_in_a_baseline_line():
    baseline = SYSTEM.replace("KLEIDIAI = 1 | ", "")
    _, feats = cb.parse_system_info(baseline)
    assert "KLEIDIAI" not in feats and feats["REPACK"] == "1"


def test_no_system_info_line():
    assert cb.parse_system_info("nothing here") == (None, {})


def test_notable_lines_pick_kleidiai_and_repack_messages():
    lines = cb.notable_lines(LOG)
    assert any("kleidiai: no compatible" in ln for ln in lines)
    assert not any("unrelated" in ln for ln in lines)


def test_memory_vs_file():
    table = {"totals": {"W_all": 100 * 1024 * 1024}, "tied_embeddings": True}
    m = cb.memory_vs_file({"CPU_Mapped": 40.0, "CPU_REPACK": 70.5}, table)
    assert m == {
        "file_tensor_mib": 100.0,
        "memory_mib": 110.5,
        "delta_mib": 10.5,
        "tied_embeddings": True,
    }
