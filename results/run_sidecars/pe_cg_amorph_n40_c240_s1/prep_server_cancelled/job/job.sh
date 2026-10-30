#!/bin/bash
#SBATCH --job-name=pe_cg_amorph_n40_c240_s1-prep
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --mem=2G
#SBATCH --time=1-00:00:00
#SBATCH --no-requeue
#SBATCH --nodelist=rdyu-rog
#SBATCH --output=/home/rdyu/projects/che126_sims/logs/%x-%j-%N.out
# sepsim 0.1.0 job: prep for pe_cg_amorph_n40_c240_s1 (pinned to rdyu-rog), omp, 1 rank(s) x 6 thread(s)
# Submit from rdyu-server in the project root (ssubmit syncs jobs/, not results/):
#   ~/projects/slurm-setup/bin/ssubmit /home/rdyu/projects/che126_sims jobs/pe_cg_amorph_n40_c240_s1/prep/job.sh
# Fetch outputs afterwards: ~/projects/slurm-setup/bin/scollect /home/rdyu/projects/che126_sims
# Inputs under results/ (earlier stages) exist only on the node that made them:
# keep a system's stages on one node (--node / -w).
set -euo pipefail
REPO=/home/rdyu/projects/che126_sims
JOB_DIR=/home/rdyu/projects/che126_sims/jobs/pe_cg_amorph_n40_c240_s1/prep
RUN_DIR=/home/rdyu/projects/che126_sims/results/runs/pe_cg_amorph_n40_c240_s1/prep
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
cp "$JOB_DIR/in.prep" in.prep
if [ ! -f ../../../../systems/pe_cg_amorph_n40_c240_s1/data.lmp ]; then
    echo "error: input data ../../../../systems/pe_cg_amorph_n40_c240_s1/data.lmp (relative to $RUN_DIR) not found on $(hostname -s); run the earlier stage on this node (--node)" >&2
    exit 1
fi
export OMP_NUM_THREADS=6
echo "job ${SLURM_JOB_ID:-none} on $(hostname -s) in $RUN_DIR, started $(date -Is)"
exec uv run --frozen --project "$REPO" sepsim run in.prep \
    --lmp "apptainer exec $SEPSIM_SIF lmp -sf omp -pk omp 6" \
    --lmp-probe "apptainer exec $SEPSIM_SIF lmp"
