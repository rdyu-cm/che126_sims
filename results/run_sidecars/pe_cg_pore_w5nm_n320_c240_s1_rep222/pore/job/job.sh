#!/bin/bash
#SBATCH --job-name=pe_cg_pore_w5nm_n320_c240_s1_rep222-pore
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=2G
#SBATCH --time=3-00:00:00
#SBATCH --no-requeue
#SBATCH --gres=gpu:1
#SBATCH --nodelist=rdyu-rog
#SBATCH --output=/home/rdyu/projects/che126_sims/logs/%x-%j-%N.out
# sepsim 0.1.0 job: pore for pe_cg_pore_w5nm_n320_c240_s1_rep222 (pinned to rdyu-rog), kokkos, 1 rank(s) x 2 thread(s)
# Submit from rdyu-server in the project root (ssubmit syncs jobs/, not results/):
#   ~/projects/slurm-setup/bin/ssubmit /home/rdyu/projects/che126_sims jobs/pe_cg_pore_w5nm_n320_c240_s1_rep222/pore/job.sh
# Fetch outputs afterwards: ~/projects/slurm-setup/bin/scollect /home/rdyu/projects/che126_sims
# Inputs under results/ (earlier stages) exist only on the node that made them:
# keep a system's stages on one node (--node / -w).
set -euo pipefail
REPO=/home/rdyu/projects/che126_sims
JOB_DIR=/home/rdyu/projects/che126_sims/jobs/pe_cg_pore_w5nm_n320_c240_s1_rep222/pore
RUN_DIR=/home/rdyu/projects/che126_sims/results/runs/pe_cg_pore_w5nm_n320_c240_s1_rep222/pore
SEPSIM_SIF="${SEPSIM_SIF:-$HOME/projects/installations/lammps/stable_22Jul2025_update6/lammps-rocm6.4.4-gfx1030.sif}"
command -v uv >/dev/null || export PATH="$HOME/.local/bin:$PATH"

if [ ! -f "$SEPSIM_SIF" ] || [[ "$SEPSIM_SIF" =~ [[:space:]] ]]; then
    echo "error: LAMMPS image not found or path has spaces: $SEPSIM_SIF" >&2
    exit 1
fi
mkdir -p "$RUN_DIR"
cd "$RUN_DIR"
if [ -f run_manifest.json ] && grep -q '"status": "finished"' run_manifest.json; then
    echo "error: $RUN_DIR already holds a finished run; move it away to rerun" >&2
    exit 1
fi
cp "$JOB_DIR/in.pore" in.pore
if [ ! -f ../../../../systems/pe_cg_pore_w5nm_n320_c240_s1_rep222/data.lmp ]; then
    echo "error: input data ../../../../systems/pe_cg_pore_w5nm_n320_c240_s1_rep222/data.lmp (relative to $RUN_DIR) not found on $(hostname -s); run the earlier stage on this node (--node)" >&2
    exit 1
fi
export OMP_NUM_THREADS=2
# Slurm sets ROCR_VISIBLE_DEVICES=0 (the RX 6800S); gfx1032 runs as gfx1030 (D23)
export HSA_OVERRIDE_GFX_VERSION=10.3.0
echo "job ${SLURM_JOB_ID:-none} on $(hostname -s) in $RUN_DIR, started $(date -Is)"
exec uv run --frozen --project "$REPO" sepsim run in.pore \
    --lmp "apptainer exec --rocm $SEPSIM_SIF lmp -k on g 1 -sf kk -pk kokkos newton on neigh half" \
    --lmp-probe "apptainer exec --rocm $SEPSIM_SIF lmp"
