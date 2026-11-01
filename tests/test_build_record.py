"""bench/build_record.py: cache comparison, compile-flag extraction, KleidiAI pin parsing."""

from pathlib import Path

from bench import build_record as br

BASE = "/home/u/edge/work/build-baseline"
KAI = "/home/u/edge/work/build-kleidiai"


def cache(build_dir, kleidiai, extra=""):
    return (
        "// comment\n"
        "CMAKE_BUILD_TYPE:STRING=Release\n"
        f"CMAKE_CACHEFILE_DIR:INTERNAL={build_dir}\n"
        f"llama.cpp_BINARY_DIR:STATIC={build_dir}\n"
        f"GGML_CPU_KLEIDIAI:BOOL={'ON' if kleidiai else 'OFF'}\n"
        "GGML_NATIVE:BOOL=ON\n"
        + (f"FETCHCONTENT_SOURCE_DIR_KLEIDIAI:PATH={build_dir}/_deps/x\n" if kleidiai else "")
        + (f"kleidiai_BINARY_DIR:STATIC={build_dir}/_deps/k\n" if kleidiai else "")
        + extra
    )


def test_parse_cache_skips_comments():
    c = br.parse_cache(cache(BASE, False))
    assert c["GGML_NATIVE"] == "ON" and "// comment" not in c


def test_only_kleidiai_and_paths_may_differ():
    d = br.diff_caches(cache(BASE, False), cache(KAI, True), BASE, KAI)
    assert d["unexpected_keys"] == []
    assert "GGML_CPU_KLEIDIAI" in d["kleidiai_keys"]
    assert "FETCHCONTENT_SOURCE_DIR_KLEIDIAI" in d["kleidiai_keys"]  # present in one build only
    # the build folder itself differs but is normalised away, so it is not even listed
    assert "CMAKE_CACHEFILE_DIR" not in d["path_keys"] + d["unexpected_keys"]


def test_a_real_difference_is_unexpected():
    a = cache(BASE, False, "GGML_OPENMP:BOOL=ON\n")
    b = cache(KAI, True, "GGML_OPENMP:BOOL=OFF\n")
    d = br.diff_caches(a, b, BASE, KAI)
    assert len(d["unexpected_keys"]) == 1 and "GGML_OPENMP" in d["unexpected_keys"][0]


def test_allow_list_moves_a_key_out_of_unexpected():
    a = cache(BASE, False, "GGML_CCACHE:BOOL=ON\n")
    b = cache(KAI, True, "GGML_CCACHE:BOOL=OFF\n")
    d = br.diff_caches(a, b, BASE, KAI, allow=("GGML_CCACHE",))
    assert d["unexpected_keys"] == [] and d["allowed_by_user"] == ["GGML_CCACHE"]


def test_path_keys_that_differ_after_normalising_are_allowed_as_paths():
    a = cache(BASE, False, "ZLIB_INCLUDE_DIR:PATH=/usr/include\n")
    b = cache(KAI, True, "ZLIB_INCLUDE_DIR:PATH=/opt/z/include\n")
    d = br.diff_caches(a, b, BASE, KAI)
    assert d["path_keys"] == ["ZLIB_INCLUDE_DIR"] and d["unexpected_keys"] == []


ROOT = "/home/u/edge/work/llama.cpp"
ENTRIES = [
    {
        "directory": "/b",
        "file": f"{ROOT}/ggml/src/ggml-cpu/ggml-cpu.c",
        "command": "/usr/bin/cc -DGGML_USE_OPENMP -I/x -O3 -DNDEBUG -mcpu=neoverse-v2+sve2 "
        f"-fopenmp -std=gnu11 -o a.o -c {ROOT}/ggml/src/ggml-cpu/ggml-cpu.c",
    },
    {
        "directory": "/b",
        "file": f"{ROOT}/ggml/src/ggml-cpu/kleidiai/kernels.cpp",
        "arguments": ["/usr/bin/c++", "-O3", "-mcpu=native", "-I/y", "-c", "kernels.cpp"],
    },
    {
        "directory": "/b",
        "file": "/home/u/edge/work/build-kleidiai/_deps/kleidiai-src/kai/a_i8mm.c",
        "command": "/usr/bin/cc -O3 -march=armv8.2-a+i8mm -c a_i8mm.c",
    },
    {
        "directory": "/b",
        "file": "/home/u/edge/work/build-kleidiai/_deps/kleidiai-src/kai/b_i8mm.c",
        "command": "/usr/bin/cc -O3 -march=armv8.2-a+i8mm -c b_i8mm.c",
    },
    {
        "directory": "/b",
        "file": "/home/u/edge/work/build-kleidiai/_deps/kleidiai-src/kai/c_dot.c",
        "command": "/usr/bin/cc -O3 -march=armv8.2-a+dotprod -c c_dot.c",
    },
    {"directory": "/b", "file": f"{ROOT}/src/llama.cpp", "command": "/usr/bin/c++ -O2 -c x.cpp"},
]


def test_compile_flags_keep_codegen_flags_and_drop_include_paths():
    out = br.compile_flags(ENTRIES, Path(ROOT))
    cpu = out["ggml_cpu"]
    assert set(cpu) == {"ggml/src/ggml-cpu/ggml-cpu.c", "ggml/src/ggml-cpu/kleidiai/kernels.cpp"}
    flags = cpu["ggml/src/ggml-cpu/ggml-cpu.c"]["flags"]
    assert "-mcpu=neoverse-v2+sve2" in flags and "-O3" in flags and "-fopenmp" in flags
    assert not any(f.startswith("-I") for f in flags)
    assert cpu["ggml/src/ggml-cpu/kleidiai/kernels.cpp"]["flags"] == ["-O3", "-mcpu=native"]


def test_kleidiai_library_files_are_grouped_by_identical_flags():
    groups = br.compile_flags(ENTRIES, Path(ROOT))["kleidiai_library"]
    by_flags = {tuple(g["flags"]): g for g in groups}
    i8 = by_flags[("-O3", "-march=armv8.2-a+i8mm")]
    assert i8["n_files"] == 2 and i8["files"] == ["a_i8mm.c", "b_i8mm.c"]
    assert by_flags[("-O3", "-march=armv8.2-a+dotprod")]["files"] == ["c_dot.c"]


CMAKE_SNIPPET = """
        set(KLEIDIAI_COMMIT_TAG "v1.32.0")
        set(KLEIDIAI_DOWNLOAD_URL "https://github.com/ARM-software/kleidiai/releases/download/${KLEIDIAI_COMMIT_TAG}/kleidiai-${KLEIDIAI_COMMIT_TAG}-src.tar.gz")
        set(KLEIDIAI_RELEASE_ARCHIVE_MD5  "05f1953428ffe8e8c7f585dc6d508887")
"""


def test_kleidiai_pin_is_read_from_cmake_text():
    info = br.kleidiai_from_cmake(CMAKE_SNIPPET)
    assert info["tag"] == "v1.32.0"
    assert info["url"].endswith("/v1.32.0/kleidiai-v1.32.0-src.tar.gz")
    assert info["md5"] == "05f1953428ffe8e8c7f585dc6d508887"
