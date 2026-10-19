#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y minizinc python3 python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
minizinc --version
minizinc --solvers
python --version
echo
echo "Setup complete. HiGHS needs extra steps: see BACKEND_SETUP.md."
echo "Next: make generate && make run && make analyze && make plot && make check"
