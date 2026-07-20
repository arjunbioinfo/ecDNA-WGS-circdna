#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Reproducible launcher for nf-core/circdna 1.1.0 (ecDNA / circular DNA from WGS)
#
# Usage:
#   ./run.sh <branch> [extra nextflow args...]
#     branch = ampliconarchitect | circle_map_realign | circle_map_repeats | circexplorer2
#
# Reads local paths (AA data repo, Mosek license, container cache) from env.sh
# (git-ignored). Copy env.sh.example -> env.sh and edit first.
# -----------------------------------------------------------------------------
set -euo pipefail

REV="1.1.0"   # pinned pipeline version for reproducibility

BRANCH="${1:-}"
if [[ -z "$BRANCH" ]]; then
  echo "usage: ./run.sh <ampliconarchitect|circle_map_realign|circle_map_repeats|circexplorer2> [nextflow args]" >&2
  exit 2
fi
shift || true

PARAMS="params/${BRANCH}.yaml"
[[ -f "$PARAMS" ]] || { echo "error: no params file '$PARAMS'" >&2; exit 1; }

# Load machine-specific environment if present
if [[ -f env.sh ]]; then
  # shellcheck disable=SC1091
  source env.sh
fi

PROFILE="${PROFILE:-singularity}"

EXTRA=()
if [[ "$BRANCH" == "ampliconarchitect" ]]; then
  : "${AA_DATA_REPO:?set AA_DATA_REPO in env.sh (path to the AmpliconArchitect data repo)}"
  : "${MOSEK_LICENSE_DIR:?set MOSEK_LICENSE_DIR in env.sh (dir containing mosek.lic)}"
  EXTRA+=(--aa_data_repo "$AA_DATA_REPO" --mosek_license_dir "$MOSEK_LICENSE_DIR")
fi

set -x
nextflow run nf-core/circdna -r "$REV" \
  -profile "$PROFILE" \
  -params-file "$PARAMS" \
  -c nextflow.config \
  "${EXTRA[@]}" "$@"
