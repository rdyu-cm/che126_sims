#!/usr/bin/env bash
# Jupyter Lab for scripts/view.ipynb (OVITO trajectory viewer) on this node, localhost only.
# From the laptop: ssh -N -L 8888:localhost:8888 rdyu-server, then open the printed URL.
# Environment (once): uv venv $ENV --python 3.12 && VIRTUAL_ENV=$ENV uv pip install ovito ipywidgets jupyterlab
set -euo pipefail
ENV=${OVITO_VIEWER_ENV:-${SEPSIM_INSTALL_DIR:-$HOME/projects/installations}/ovito-viewer}
cd "$(dirname "$0")"
exec "$ENV/bin/jupyter" lab --no-browser --ip 127.0.0.1 --port "${PORT:-8888}" view.ipynb
