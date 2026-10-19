#!/usr/bin/env bash
# Build the pinned LAMMPS release for sepsim (decision D23, docs/decisions.md).
#
# One binary for AMD GPUs (ROCm/HIP) with MOLECULE, KSPACE, EXTRA-MOLECULE, CG-SPICA,
# KOKKOS (HIP), GPU (HIP, mixed precision) and OPENMP. Used natively and inside
# containers/lammps.def. How-to: docs/LAMMPS_BUILD.md.
#
# Parameters (environment variables):
#   SEPSIM_GPU_ARCH     AMD GPU LLVM target, REQUIRED, no default. One of
#                       gfx908 gfx90a gfx942 gfx1030 gfx1100. The RX 6800S workstation
#                       (gfx1032) uses gfx1030 + HSA_OVERRIDE_GFX_VERSION=10.3.0 at run time.
#   SEPSIM_ROCM_PATH    ROCm install root (selects the ROCm version). Default: $ROCM_PATH,
#                       else /opt/rocm.
#   SEPSIM_INSTALL_DIR  Root for everything this script creates. Default:
#                       <repo>/../installations, a sibling of the main checkout
#                       (git worktrees resolve to the same folder).
#   SEPSIM_HOST_ARCH    Optional Kokkos host arch ID; default: generic x86-64. Kokkos adds
#                       the matching -march to the whole binary, so leave it unset for a
#                       binary shared across CPUs.
#   SEPSIM_MPI          yes|no, build with MPI (default yes; needs an MPI library).
#   SEPSIM_JOBS         Parallel build jobs (default: min(nproc, RAM in GB / 2), since
#                       hipcc needs ~2 GB per job).
#
# Options: --dry-run   print the resolved paths and cmake command, then exit.
#          -h|--help   print this header.
#
# Layout under $SEPSIM_INSTALL_DIR:
#   lammps/<tag>/src                         source checkout (shared by all variants)
#   lammps/<tag>/rocm<ver>-<gfx>/build       cmake build tree
#   lammps/<tag>/rocm<ver>-<gfx>/install     install prefix; binary at install/bin/lmp
#   lammps/<tag>/rocm<ver>-<gfx>/install/share/sepsim_build_info.txt   build record
#
# Sources for every cmake option (checked against the docs and cmake files at this tag,
# 2026-10-19):
#   https://docs.lammps.org/Build_package.html        PKG_<NAME>=yes
#   https://docs.lammps.org/Build_basics.html         BUILD_MPI, BUILD_OMP, install
#   https://docs.lammps.org/Build_settings.html       FFT, FFT_KOKKOS (default KISS)
#   https://docs.lammps.org/Build_extras.html#gpu     GPU_API=hip, HIP_ARCH=gfx*, GPU_PREC,
#                                                     HIP_PLATFORM, CMAKE_CXX_COMPILER=hipcc
#   https://docs.lammps.org/Build_extras.html#kokkos  Kokkos_ENABLE_HIP, Kokkos_ARCH_<ID>
#   https://docs.lammps.org/Run_options.html          a KOKKOS binary runs plain/GPU/OPENMP
#                                                     styles when `-k on` is not given
#   https://github.com/lammps/lammps/blob/stable_22Jul2025_update6/cmake/presets/kokkos-hip.cmake
#   https://github.com/lammps/lammps/blob/stable_22Jul2025_update6/cmake/presets/hip.cmake
#   https://github.com/lammps/lammps/blob/stable_22Jul2025_update6/cmake/Modules/Packages/KOKKOS.cmake
#   https://github.com/lammps/lammps/blob/stable_22Jul2025_update6/cmake/Modules/Packages/GPU.cmake
#   https://github.com/lammps/lammps/blob/stable_22Jul2025_update6/lib/kokkos/cmake/kokkos_arch.cmake

set -euo pipefail

LAMMPS_TAG="stable_22Jul2025_update6"
# Commit the tag points to (git ls-remote ... refs/tags/stable_22Jul2025_update6^{}).
LAMMPS_COMMIT="9c5ab448c78a14fd534619622162ba418d6a1fb1"
LAMMPS_REPO="https://github.com/lammps/lammps.git"

PACKAGES=(MOLECULE KSPACE EXTRA-MOLECULE CG-SPICA KOKKOS GPU OPENMP)

die() {
  echo "build_lammps.sh: error: $*" >&2
  exit 1
}

DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h | --help)
      sed -n '2,/^set -euo/p' "$0" | sed '$d; s/^# \{0,1\}//'
      exit 0
      ;;
    *) die "unknown argument: $arg (try --help)" ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# The main checkout, also when run from a git worktree (so all worktrees share one
# installations/ folder); falls back to the script's parent outside a git repo.
GIT_COMMON="$(cd "$SCRIPT_DIR" && git rev-parse --git-common-dir 2> /dev/null || true)"
if [[ -n "$GIT_COMMON" ]] && GIT_COMMON="$(cd "$SCRIPT_DIR" && cd "$GIT_COMMON" && pwd)" \
  && [[ "$(basename "$GIT_COMMON")" == .git ]]; then
  REPO_DIR="$(dirname "$GIT_COMMON")"
else
  REPO_DIR="$(dirname "$SCRIPT_DIR")"
fi
INSTALL_ROOT="${SEPSIM_INSTALL_DIR:-$(dirname "$REPO_DIR")/installations}"

# --- GPU arch: LLVM target -> Kokkos arch ID ------------------------------------------
# Only targets both the bundled Kokkos 4.6.2 (lib/kokkos/cmake/kokkos_arch.cmake) and
# ROCm 6.4 (install-on-linux .../reference/system-requirements.html) support.
GPU_ARCH="${SEPSIM_GPU_ARCH:-}"
[[ -n "$GPU_ARCH" ]] || die "set SEPSIM_GPU_ARCH (e.g. gfx1030 for the RX 6800S; see docs/LAMMPS_BUILD.md)"
case "$GPU_ARCH" in
  gfx908) KOKKOS_GPU_ARCH=AMD_GFX908 ;;
  gfx90a) KOKKOS_GPU_ARCH=AMD_GFX90A ;;
  gfx942) KOKKOS_GPU_ARCH=AMD_GFX942 ;;
  gfx1030) KOKKOS_GPU_ARCH=AMD_GFX1030 ;;
  gfx1100) KOKKOS_GPU_ARCH=AMD_GFX1100 ;;
  gfx103[1-6]) die "$GPU_ARCH has no Kokkos arch or official ROCm support; build gfx1030 and run with HSA_OVERRIDE_GFX_VERSION=10.3.0" ;;
  *) die "unsupported SEPSIM_GPU_ARCH='$GPU_ARCH' (one of gfx908 gfx90a gfx942 gfx1030 gfx1100)" ;;
esac

# --- ROCm -----------------------------------------------------------------------------
ROCM="${SEPSIM_ROCM_PATH:-${ROCM_PATH:-/opt/rocm}}"
ROCM_VERSION="unknown"
if [[ -r "$ROCM/.info/version" ]]; then
  ROCM_VERSION="$(sed 's/-.*//' "$ROCM/.info/version")"
elif [[ -x "$ROCM/bin/hipcc" ]]; then
  ROCM_VERSION="hip$("$ROCM/bin/hipcc" --version 2> /dev/null \
    | sed -n 's/^HIP version: \([0-9]*\.[0-9]*\).*/\1/p')"
fi
if [[ "$DRY_RUN" -eq 0 && ! -x "$ROCM/bin/hipcc" ]]; then
  die "no hipcc at $ROCM/bin/hipcc; set SEPSIM_ROCM_PATH to a ROCm install root"
fi

VARIANT="rocm${ROCM_VERSION}-${GPU_ARCH}"
TAG_DIR="$INSTALL_ROOT/lammps/$LAMMPS_TAG"
SRC_DIR="$TAG_DIR/src"
BUILD_DIR="$TAG_DIR/$VARIANT/build"
PREFIX="$TAG_DIR/$VARIANT/install"

if [[ -n "${SEPSIM_JOBS:-}" ]]; then
  JOBS="$SEPSIM_JOBS"
else
  JOBS="$(nproc 2> /dev/null || echo 4)"
  MEM_GB="$(awk '/^MemTotal:/ {print int($2 / 1048576)}' /proc/meminfo 2> /dev/null || echo 0)"
  if ((MEM_GB / 2 >= 1 && MEM_GB / 2 < JOBS)); then JOBS=$((MEM_GB / 2)); fi
fi

MPI="${SEPSIM_MPI:-yes}"
[[ "$MPI" == yes || "$MPI" == no ]] || die "SEPSIM_MPI must be yes or no"

CMAKE_ARGS=(
  -S "$SRC_DIR/cmake" -B "$BUILD_DIR"
  -D CMAKE_BUILD_TYPE=Release
  -D CMAKE_INSTALL_PREFIX="$PREFIX"
  -D BUILD_MPI="$MPI"
  -D BUILD_OMP=yes
)
for pkg in "${PACKAGES[@]}"; do
  CMAKE_ARGS+=(-D "PKG_${pkg}=yes")
done
CMAKE_ARGS+=(
  # hipcc compiles all of LAMMPS (Build_extras.html#gpu HIP examples; presets/hip.cmake).
  # The name must stay "hipcc": cmake/CMakeLists.txt keys its hipcc workarounds on it.
  -D CMAKE_CXX_COMPILER="$ROCM/bin/hipcc"
  -D ROCM_PATH="$ROCM"
  -D CMAKE_PREFIX_PATH="$ROCM"
  # KOKKOS with HIP, as in presets/kokkos-hip.cmake. That preset keeps Kokkos' OpenMP
  # backend OFF ("not compatible with the second pass of hipcc"), so the Kokkos host
  # backend is Serial; BUILD_OMP still gives the OPENMP package its threads.
  -D Kokkos_ENABLE_SERIAL=yes
  -D Kokkos_ENABLE_OPENMP=no
  -D Kokkos_ENABLE_HIP=yes
  -D "Kokkos_ARCH_${KOKKOS_GPU_ARCH}=yes"
  -D Kokkos_ENABLE_HIP_MULTIPLE_KERNEL_INSTANTIATIONS=yes
  -D CMAKE_CXX_FLAGS=-munsafe-fp-atomics
  # KOKKOS PPPM on the GPU: the HIP backend accepts only KISS or HIPFFT (KOKKOS.cmake),
  # and the default is KISS, so request hipFFT (rocFFT underneath) explicitly.
  -D FFT_KOKKOS=HIPFFT
  # Host FFT for plain/OPENMP PPPM and for pppm/gpu (the GPU package does its FFTs on
  # the host). FFTW3 must be installed (libfftw3-dev); cmake fails if it is not found.
  -D FFT=FFTW3
  # GPU package on HIP for AMD, mixed precision (the expected main path on RDNA, whose
  # FP64 rate is a small fraction of FP32; see docs/LAMMPS_BUILD.md).
  -D GPU_API=hip
  -D HIP_PLATFORM=amd
  -D HIP_ARCH="$GPU_ARCH"
  -D GPU_PREC=mixed
)
if [[ -n "${SEPSIM_HOST_ARCH:-}" ]]; then
  CMAKE_ARGS+=(-D "Kokkos_ARCH_${SEPSIM_HOST_ARCH}=yes")
fi

cat << EOF
LAMMPS tag     : $LAMMPS_TAG ($LAMMPS_COMMIT)
GPU            : $GPU_ARCH -> Kokkos_ARCH_$KOKKOS_GPU_ARCH, HIP_ARCH=$GPU_ARCH
ROCm           : $ROCM (version $ROCM_VERSION)
install root   : $INSTALL_ROOT
source         : $SRC_DIR
build          : $BUILD_DIR
prefix         : $PREFIX
jobs           : $JOBS
EOF
echo "cmake command  : cmake ${CMAKE_ARGS[*]}"
if [[ "$DRY_RUN" -eq 1 ]]; then
  exit 0
fi

command -v git > /dev/null || die "git not found"
command -v cmake > /dev/null || die "cmake (>= 3.16) not found"

# --- Source: shallow clone of the tag, verified against the pinned commit -----------
mkdir -p "$TAG_DIR"
if [[ ! -d "$SRC_DIR/.git" ]]; then
  git -c advice.detachedHead=false clone --depth 1 --branch "$LAMMPS_TAG" "$LAMMPS_REPO" "$SRC_DIR"
fi
HEAD_COMMIT="$(git -C "$SRC_DIR" rev-parse HEAD)"
[[ "$HEAD_COMMIT" == "$LAMMPS_COMMIT" ]] \
  || die "$SRC_DIR is at $HEAD_COMMIT, expected $LAMMPS_COMMIT ($LAMMPS_TAG); remove it to re-clone"
[[ -z "$(git -C "$SRC_DIR" status --porcelain)" ]] \
  || die "$SRC_DIR has local modifications; remove it to re-clone"

# --- Configure, build, install ------------------------------------------------------
export PATH="$ROCM/bin:$PATH"
export ROCM_PATH="$ROCM"
export HIP_PLATFORM=amd
cmake "${CMAKE_ARGS[@]}"
cmake --build "$BUILD_DIR" --parallel "$JOBS"
cmake --install "$BUILD_DIR"

INFO="$PREFIX/share/sepsim_build_info.txt"
mkdir -p "$(dirname "$INFO")"
{
  echo "tag: $LAMMPS_TAG"
  echo "commit: $LAMMPS_COMMIT"
  echo "built: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "rocm: $ROCM_VERSION ($ROCM)"
  echo "gpu_arch: $GPU_ARCH"
  echo "cmake: cmake ${CMAKE_ARGS[*]}"
} > "$INFO"

echo
echo "Installed: $PREFIX/bin/lmp"
echo "Smoke check: $PREFIX/bin/lmp -h | sed -n '/Installed packages:/,/^$/p'"
