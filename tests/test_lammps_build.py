"""Static consistency checks for the LAMMPS build packaging (D23, AMD ROCm). Nothing is built."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_lammps.sh"
DEF = ROOT / "containers" / "lammps.def"
DOC = ROOT / "docs" / "LAMMPS_BUILD.md"
REQUIRED_PACKAGES = [
    "MOLECULE",
    "KSPACE",
    "EXTRA-MOLECULE",
    "CG-SPICA",
    "RIGID",
    "EXTRA-DUMP",
    "KOKKOS",
    "GPU",
    "OPENMP",
]
PINNED_TAG = "stable_22Jul2025_update6"
BASH = shutil.which("bash")
needs_bash = pytest.mark.skipif(BASH is None, reason="bash not available")


def d23_tag() -> str:
    """The pinned tag as written in the D23 row of docs/decisions.md."""
    row = next(
        ln
        for ln in (ROOT / "docs" / "decisions.md").read_text().splitlines()
        if ln.startswith("| D23 |")
    )
    match = re.search(r"\*\*`(stable_[^`]+)`\*\*", row)
    assert match, "D23 row lost its bold tag"
    return match.group(1)


def dry_run(tmp_path: Path, arch: str | None) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "SEPSIM_GPU_ARCH"}
    env["SEPSIM_INSTALL_DIR"] = str(tmp_path / "inst")
    if arch is not None:
        env["SEPSIM_GPU_ARCH"] = arch
    return subprocess.run(
        [BASH, str(SCRIPT), "--dry-run"],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def test_d23_tag_is_the_expected_release():
    assert d23_tag() == PINNED_TAG


def test_script_pins_d23_tag_and_commit():
    text = SCRIPT.read_text()
    assert f'LAMMPS_TAG="{d23_tag()}"' in text
    assert re.search(r'^LAMMPS_COMMIT="[0-9a-f]{40}"$', text, re.MULTILINE)
    assert "set -euo pipefail" in text


def test_script_lists_every_required_package():
    match = re.search(r"^PACKAGES=\(([^)]*)\)", SCRIPT.read_text(), re.MULTILINE)
    assert match
    assert sorted(match.group(1).split()) == sorted(REQUIRED_PACKAGES)


def test_no_cuda_code_path():
    for path in (SCRIPT, DEF):
        assert not re.search(r"cuda|nvcc|CUFFT|--nv\b", path.read_text(), re.IGNORECASE), path


@needs_bash
def test_script_bash_syntax():
    proc = subprocess.run([BASH, "-n", str(SCRIPT)], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr


@needs_bash
def test_dry_run_cmake_line(tmp_path):
    proc = dry_run(tmp_path, "gfx1030")
    assert proc.returncode == 0, proc.stderr
    cmake = next(ln for ln in proc.stdout.splitlines() if ln.startswith("cmake command"))
    for pkg in REQUIRED_PACKAGES:
        assert f"-D PKG_{pkg}=yes" in cmake
    for flag in (
        "Kokkos_ENABLE_HIP=yes",
        "Kokkos_ARCH_AMD_GFX1030=yes",
        "Kokkos_ENABLE_HIP_MULTIPLE_KERNEL_INSTANTIATIONS=yes",
        "GPU_API=hip",
        "HIP_PLATFORM=amd",
        "HIP_ARCH=gfx1030",
        "GPU_PREC=mixed",
        "FFT_KOKKOS=HIPFFT",
        "BUILD_OMP=yes",
        "/bin/hipcc",
    ):
        assert flag in cmake
    assert f"source         : {tmp_path / 'inst' / 'lammps' / PINNED_TAG / 'src'}" in proc.stdout


@needs_bash
def test_arch_is_required(tmp_path):
    proc = dry_run(tmp_path, None)
    assert proc.returncode != 0
    assert "set SEPSIM_GPU_ARCH" in proc.stderr


@needs_bash
@pytest.mark.parametrize("arch", ["gfx1032", "gfx1035", "gfx1201", "sm_89"])
def test_unsupported_arch_rejected(tmp_path, arch):
    proc = dry_run(tmp_path, arch)
    assert proc.returncode != 0
    assert arch in proc.stderr


def test_def_uses_build_script_and_pinned_rocm_image():
    text = DEF.read_text()
    assert re.search(r"^Bootstrap: docker$", text, re.MULTILINE)
    assert re.search(
        r"^From: rocm/dev-ubuntu-24\.04:\{\{ ROCM_VERSION \}\}-complete$", text, re.MULTILINE
    )
    assert re.search(r"^\s+ROCM_VERSION=\d+\.\d+\.\d+$", text, re.MULTILINE)
    assert re.search(r"^\s+GPU_ARCH=unset$", text, re.MULTILINE)  # no default arch
    files = text.split("\n%files", 1)[1].split("\n%post", 1)[0]
    assert "/scripts/build_lammps.sh /opt/sepsim/build_lammps.sh" in files
    post = text.split("\n%post", 1)[1].split("\n%environment", 1)[0]
    assert "bash /opt/sepsim/build_lammps.sh" in post
    assert "SEPSIM_GPU_ARCH=" in post


def test_def_host_arch_defaults_to_generic():
    # The shared image runs on Intel and AMD CPUs, so no Kokkos host arch (-march) by
    # default. "none" stands in for empty because template variables need a value.
    text = DEF.read_text()
    args = text.split("\n%arguments", 1)[1].split("\n%files", 1)[0]
    assert re.search(r"^\s+HOST_ARCH=none$", args, re.MULTILINE)
    post = text.split("\n%post", 1)[1].split("\n%environment", 1)[0]
    assert 'if [ "{{ HOST_ARCH }}" != none ]; then export SEPSIM_HOST_ARCH=' in post


def test_def_template_variables_all_have_defaults():
    # Apptainer fails on a template variable with no value, and on unused build args.
    text = DEF.read_text()
    used = set(re.findall(r"\{\{\s*(\w+)\s*\}\}", text))
    args = text.split("\n%arguments", 1)[1].split("\n%files", 1)[0]
    defined = set(re.findall(r"^\s+(\w+)=", args, re.MULTILINE))
    assert used == defined


def test_doc_covers_paths_and_gpu_selection():
    text = DOC.read_text()
    for needle in (
        d23_tag(),
        "scripts/build_lammps.sh",
        "containers/lammps.def",
        "apptainer exec --rocm",
        "SEPSIM_LMP",
        "HSA_OVERRIDE_GFX_VERSION=10.3.0",
        "ROCR_VISIBLE_DEVICES",
        "rocminfo",
    ):
        assert needle in text, needle


def test_build_outputs_are_gitignored():
    ignore = (ROOT / ".gitignore").read_text().splitlines()
    assert "*.sif" in ignore
    assert "/installations/" in ignore


@pytest.mark.skipif(shutil.which("shellcheck") is None, reason="shellcheck not installed")
def test_shellcheck():
    proc = subprocess.run(["shellcheck", str(SCRIPT)], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stdout


def test_def_environment_finds_rocm_libomp():
    # lmp links ROCm's LLVM libomp.so; without this path the binary does not start.
    env = DEF.read_text().split("\n%environment", 1)[1].split("\n%runscript", 1)[0]
    assert "export LD_LIBRARY_PATH=/opt/rocm/lib/llvm/lib" in env
