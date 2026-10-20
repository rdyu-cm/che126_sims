# Building LAMMPS (D23, AMD ROCm)

One binary for AMD GPUs: LAMMPS **`stable_22Jul2025_update6`** with MOLECULE, KSPACE, EXTRA-MOLECULE, CG-SPICA, KOKKOS (HIP), GPU (HIP, mixed precision) and OPENMP. The step-0 benchmark picks the accelerator per run type.

- Build script: [`scripts/build_lammps.sh`](../scripts/build_lammps.sh) (tag, commit check, cmake flags, doc links).
- Container: [`containers/lammps.def`](../containers/lammps.def) runs the same script in a pinned `rocm/dev-ubuntu-24.04` image.
- Build and run on the compute machines, not the dev machine (D16). One image serves both; see [Two machines, one image](#two-machines-one-image).

## The workstations
Two compute machines; the user's local machine only controls them.
- **rdyu-server:** Intel i7-1255U, no usable GPU. CPU runs only. Builds the image.
- **rdyu-rog** (ASUS ROG laptop): Ryzen 9 6900HS (16 threads), 14 GB RAM, Apptainer 1.4.5. CPU and GPU runs.
  - **dGPU:** Radeon RX 6800S, `gfx1032` (RDNA2), 8 GB. Use this one.
  - **iGPU:** Radeon 680M, `gfx1035`. Never use it; hide it (see [Selecting the GPU](#selecting-the-gpu)).

On rdyu-rog the host ROCm install is partial (no `/opt/rocm/.info/version`; `rocm-smi` can't load `libdrm_amdgpu`). **Use the Apptainer path.** The image carries the whole ROCm userspace; the host only provides the amdgpu kernel driver.

## Two machines, one image
Build the .sif once, on rdyu-server, and copy it to rdyu-rog (`$INST` as in [Path A](#path-a-recommended-apptainer)). HIP code compiles without a GPU. Keep `HOST_ARCH` unset (generic x86-64): a Kokkos host arch adds `-march` to the whole `lmp`, so e.g. a `ZEN3` image can die with SIGILL on the Intel server.
```
sudo apt-get install apptainer-suid               # rdyu-server, once (ppa:apptainer/ppa)
# /tmp on rdyu-server is a 7.5 GB tmpfs, too small to unpack the ROCm base image:
# put Apptainer's temp and cache on disk (after `sudo`, which clears the environment).
mkdir -p ~/projects/installations/apptainer/{tmp,cache}
sudo APPTAINER_TMPDIR=$HOME/projects/installations/apptainer/tmp \
     APPTAINER_CACHEDIR=$HOME/projects/installations/apptainer/cache \
  apptainer build --build-arg REPO="$PWD" --build-arg GPU_ARCH=gfx1030 \
  "$INST/lammps-rocm6.4.4-gfx1030.sif" containers/lammps.def
sudo chown $USER: "$INST/lammps-rocm6.4.4-gfx1030.sif"
scp "$INST/lammps-rocm6.4.4-gfx1030.sif" rdyu-rog:<same path>
```
- **rdyu-server (CPU):** smoke-test plain CPU here first (see [Smoke check](#smoke-check)). No `--rocm`, no GPU env vars:
  `apptainer exec <sif> mpirun -np N lmp -in deck` or `apptainer exec <sif> lmp -in deck -sf omp -pk omp N`.
- **rdyu-rog (GPU):** with `ROCR_VISIBLE_DEVICES` and `HSA_OVERRIDE_GFX_VERSION=10.3.0` exported ([Selecting the GPU](#selecting-the-gpu)):
  `apptainer exec --rocm <sif> lmp -in deck -sf gpu -pk gpu 1`.

## Where things go
Everything goes in `installations/`, a sibling of the repo (`<repo>/../installations`; git worktrees resolve to the main checkout's sibling). Override with `SEPSIM_INSTALL_DIR`.
```
installations/lammps/stable_22Jul2025_update6/
  src/                           LAMMPS checkout (shared)
  rocm6.4.4-gfx1030/build/       cmake build tree (native path)
  rocm6.4.4-gfx1030/install/bin/lmp
  rocm6.4.4-gfx1030/install/share/sepsim_build_info.txt   cmake line, commit, ROCm version
  lammps-rocm6.4.4-gfx1030.sif   Apptainer image
```
Nothing here is committed. `.gitignore` also blocks `*.sif` and `/installations/`.

## Choosing the GPU arch
`SEPSIM_GPU_ARCH` (script) / `GPU_ARCH` (image) is **required, with no default**. It sets both `Kokkos_ARCH_AMD_GFX*` and the GPU package's `HIP_ARCH`. Find the target:
```
rocminfo | grep -E '^\s+(Name|Marketing Name|Uuid|Device Type):'   # look for gfxNNNN
rocm-smi --showproductname                                         # if rocm-smi works
```
Accepted: `gfx908` (MI100), `gfx90a` (MI210/250), `gfx942` (MI300), `gfx1030` (RDNA2: W6800, V620), `gfx1100` (RDNA3: RX 7900, W7900). That is what both the bundled Kokkos 4.6.2 and ROCm 6.4 support.

**rdyu-rog: `gfx1030`.** The RX 6800S reports `gfx1032`. AMD's ROCm list has no RX 6000 cards; of RDNA2 it lists only the W6800 and V620 (`gfx1030`). Kokkos 4.6.2 has no `gfx1032` arch either. The usual workaround is to build for `gfx1030` and run with `HSA_OVERRIDE_GFX_VERSION=10.3.0`, so the runtime reports the card as `gfx1030`. This is an unofficial runtime override: it is in the ROCm source (libhsakmt `topology.c`), not in AMD's docs. If it fails, nothing on the AMD support list can fix it.

Other consumer cards: AMD supports only a few Radeon RX models (7900/7800/7700, 9070/9060). Kokkos 4.6.2 has no RDNA4 (`gfx120x`) or `gfx1101` arch, so those cards can't build KOKKOS with this tag.

## Precision: the GPU package is the main path
- RDNA2 FP64 is **1/16 of FP32**. The W6800 (`gfx1030`) is rated 17.8 TFLOPs FP32 and 1.11 TFLOPs FP64. CDNA Instinct cards run FP64 at full rate (MI210: 22.6/22.6).
- KOKKOS runs only in double precision. The GPU package is built with `GPU_PREC=mixed`.
- So on rdyu-rog, expect **GPU package (`-sf gpu`) to be the main path**, with KOKKOS-HIP (`-k on g 1 -sf kk`) as the comparison. The step-0 benchmark decides, per run type.

**8 GB VRAM** is a constraint for the ~87k-atom κ boxes (3× replicated AA). The step-0 benchmark checks that they fit.

## Selecting the GPU
With the override set globally, the 680M iGPU can also pose as `gfx1030`. Expose only the dGPU:
```
rocminfo | grep -E '^\s+(Name|Marketing Name|Uuid|Device Type):'
export ROCR_VISIBLE_DEVICES=GPU-<dGPU uuid>      # or its index among GPU agents (0-based)
export HSA_OVERRIDE_GFX_VERSION=10.3.0
```
`ROCR_VISIBLE_DEVICES` takes GPU indices or UUIDs and applies to everything on the ROCm runtime. AMD recommends it over `HIP_VISIBLE_DEVICES` on Linux. Inside the visible set, the dGPU is then HIP device 0. If the iGPU has no unique UUID, use the dGPU's index. Check with `rocminfo` under the same environment: only the RX 6800S should be listed. Apptainer passes host environment variables into the container, so set them on the host.

## Path A (recommended): Apptainer
Host requirements (GPU runs on rdyu-rog):
- Working amdgpu kernel driver, with `/dev/kfd` and `/dev/dri/renderD*` present.
- Your user in the `render` and `video` groups.
- Apptainer ≥ 1.2 (1.4.5 is installed).

Kernel-driver compatibility: AMD tests ROCm 6.4 userspace against amdgpu (DKMS) KMD 6.1 to 6.4, and from ROCm 6.4 on guarantees up to a year either way. A distro kernel's in-tree amdgpu isn't on that matrix but usually works. The smoke check is the test.

Build (the base image is ~5.5 GB compressed; on rdyu-server use `sudo apptainer build`, elsewhere `--fakeroot` if unprivileged builds aren't set up):
```
INST="${SEPSIM_INSTALL_DIR:-$(cd .. && pwd)/installations}/lammps/stable_22Jul2025_update6"
mkdir -p "$INST"
apptainer build --build-arg REPO="$PWD" --build-arg GPU_ARCH=gfx1030 \
  "$INST/lammps-rocm6.4.4-gfx1030.sif" containers/lammps.def
```
Build args:
- `GPU_ARCH` (required).
- `ROCM_VERSION` (base `rocm/dev-ubuntu-24.04:<ver>-complete`, default `6.4.4`; rename the .sif to match).
- `HOST_ARCH`: leave unset for the shared image (generic x86-64; see above).
- `JOBS`. The script defaults to about RAM GB / 2, since hipcc is memory-hungry.

GPU runs (rdyu-rog) use `--rocm`, which binds `/dev/kfd` and `/dev/dri` plus the host's basic ROCm libraries:
```
apptainer exec --rocm "$INST/lammps-rocm6.4.4-gfx1030.sif" lmp -in in.deck -sf gpu -pk gpu 1
```
If the partial host ROCm libraries cause loader errors under `--rocm`, run without it. Apptainer mounts the host `/dev` by default, so the GPU stays visible and the image's own ROCm is used. MPI runs inside the image: `apptainer exec --rocm <sif> mpirun -np 4 lmp ...`.

## Path B: native build
Needs a complete ROCm 6.x install (`rocm-dev`, plus hipFFT, rocFFT, hipCUB and rocThrust, i.e. `rocm-libs`), cmake ≥ 3.16, git, FFTW3 and an MPI library:
```
sudo apt-get install git cmake make g++ libfftw3-dev openmpi-bin libopenmpi-dev
SEPSIM_GPU_ARCH=gfx1030 scripts/build_lammps.sh --dry-run    # check paths and the cmake line
SEPSIM_GPU_ARCH=gfx1030 scripts/build_lammps.sh
```
Other knobs: `SEPSIM_ROCM_PATH` (default `$ROCM_PATH` or `/opt/rocm`), `SEPSIM_HOST_ARCH`, `SEPSIM_MPI=no`, `SEPSIM_JOBS`. `--help` lists them. The script refuses a source tree that is not at the pinned commit or has local edits.

## Pointing `sepsim run` at the binary
`sepsim run` takes `--lmp CMD` or `$SEPSIM_LMP` (default `lmp`). It records the output of `info configuration` (fed to `<probe> -nocite -log none` on stdin) in the manifest, where the probe is the first token of CMD named `lmp*`/`lammps*` (else the first token). `--lmp-probe` / `$SEPSIM_LMP_PROBE` override it, e.g. `"apptainer exec --rocm img.sif lmp"`. For the image, the simplest route is a wrapper whose name starts with `lmp`:
```
printf '#!/bin/sh\nexec apptainer exec --rocm %s lmp "$@"\n' "$INST/lammps-rocm6.4.4-gfx1030.sif" > "$INST/lmp-sif"
chmod +x "$INST/lmp-sif"
export SEPSIM_LMP="$INST/lmp-sif"                 # native: $INST/rocm<ver>-gfx1030/install/bin/lmp
sepsim run deck.in -- -sf gpu -pk gpu 1           # GPU package (main path)
sepsim run deck.in -- -k on g 1 -sf kk            # KOKKOS-HIP
```
Without a GPU-aware MPI, KOKKOS warns or segfaults with several ranks; add `-pk kokkos gpu/aware off`.

## Smoke check
On rdyu-server run only the plain-CPU line, prefixing `lmp` with `apptainer exec <sif>`. On rdyu-rog, with `ROCR_VISIBLE_DEVICES` and `HSA_OVERRIDE_GFX_VERSION` exported as above, prefix each `lmp` with `apptainer exec --rocm <sif>` for the image:
```
echo 'info configuration' | lmp | grep -A1 'Installed packages'   # CG-SPICA EXTRA-MOLECULE GPU KOKKOS KSPACE MOLECULE OPENMP
cat > in.smoke <<'EOF'
units lj
lattice fcc 0.8442
region box block 0 10 0 10 0 10
create_box 1 box
create_atoms 1 box
mass 1 1.0
velocity all create 1.44 87287
pair_style lj/cut 2.5
pair_coeff 1 1 1.0 1.0 2.5
fix 1 all nve
run 0
EOF
lmp -in in.smoke                              # plain CPU
lmp -in in.smoke -sf gpu -pk gpu 1            # GPU package; the log names the device
lmp -in in.smoke -k on g 1 -sf kk             # KOKKOS-HIP
```
`lmp -h` queries GPU devices and aborts (HIP error 100) on a host without a GPU, so use `info configuration` instead. All three should finish with `Total wall time` and matching initial energies (mixed precision differs in the last digits). The GPU-package log must name the RX 6800S, not the 680M. The deck smoke tests and the step-0 benchmark follow (see decisions.md, Verification).

## Sources (checked 2026-10-19)
- LAMMPS build options: https://docs.lammps.org/Build_extras.html (#gpu, #kokkos), https://docs.lammps.org/Build_settings.html, the tag's `cmake/presets/kokkos-hip.cmake`, and `cmake/Modules/Packages/{KOKKOS,GPU}.cmake`. KOKKOS is double precision only: https://docs.lammps.org/Speed_compare.html
- ROCm 6.4 GPU support list: https://rocm.docs.amd.com/projects/install-on-linux/en/docs-6.4.3/reference/system-requirements.html
- Kernel-driver compatibility: https://rocm.docs.amd.com/projects/install-on-linux/en/docs-6.4.3/reference/user-kernel-space-compat-matrix.html
- GPU isolation: https://rocm.docs.amd.com/en/docs-6.4.3/conceptual/gpu-isolation.html and https://rocm.docs.amd.com/en/latest/reference/environment-variables/index.html
- `HSA_OVERRIDE_GFX_VERSION`: https://github.com/ROCm/ROCR-Runtime/blob/rocm-6.4.4/libhsakmt/src/topology.c
- FP64 rates: https://www.amd.com/en/products/graphics/workstations/radeon-pro/w6800.html and https://www.amd.com/en/products/accelerators/instinct/mi200/mi210.html
- Apptainer `--rocm`: https://apptainer.org/docs/user/latest/gpu.html
