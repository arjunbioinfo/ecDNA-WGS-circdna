#!/usr/bin/env python3
"""
Lint/validate the circdna wrapper without running the pipeline.

Checks, for every params/*.yaml:
  - valid YAML
  - required keys present (input, outdir, genome, circle_identifier)
  - circle_identifier is one (or comma-list) of the supported branches
  - input_format in {FASTQ, BAM}
  - the referenced samplesheet exists (relative to repo root)
  - if 'ampliconarchitect' is used: reference_build present and valid
And for every assets/samplesheet_*.csv:
  - header matches the expected FASTQ or BAM schema
Exits non-zero on any problem (used by CI).
"""
from __future__ import annotations
import csv
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BRANCHES = {
    "circle_map_realign", "circle_map_repeats", "circle_finder",
    "circexplorer2", "ampliconarchitect", "unicycler",
}
AA_BUILDS = {"GRCh37", "GRCh38", "mm10"}
FORMATS = {"FASTQ", "BAM"}

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def check_params(path: Path) -> None:
    try:
        cfg = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        err(f"{path.name}: invalid YAML: {exc}")
        return
    if not isinstance(cfg, dict):
        err(f"{path.name}: top-level YAML must be a mapping")
        return

    for key in ("input", "outdir", "genome", "circle_identifier"):
        if key not in cfg:
            err(f"{path.name}: missing required key '{key}'")

    ci = str(cfg.get("circle_identifier", ""))
    ids = [s.strip() for s in ci.split(",") if s.strip()]
    if not ids:
        err(f"{path.name}: circle_identifier is empty")
    for i in ids:
        if i not in BRANCHES:
            err(f"{path.name}: unknown circle_identifier '{i}' "
                f"(allowed: {sorted(BRANCHES)})")

    fmt = str(cfg.get("input_format", "FASTQ"))
    if fmt not in FORMATS:
        err(f"{path.name}: input_format '{fmt}' must be one of {sorted(FORMATS)}")

    inp = cfg.get("input")
    if inp:
        if not (ROOT / inp).exists():
            err(f"{path.name}: input samplesheet '{inp}' not found")

    if "ampliconarchitect" in ids:
        rb = cfg.get("reference_build")
        if rb is None:
            err(f"{path.name}: ampliconarchitect requires 'reference_build'")
        elif rb not in AA_BUILDS:
            err(f"{path.name}: reference_build '{rb}' must be one of {sorted(AA_BUILDS)}")


def check_samplesheet(path: Path) -> None:
    with path.open(newline="") as fh:
        header = next(csv.reader(fh), [])
    header = [h.strip() for h in header]
    if header == ["sample", "bam"]:
        return
    if header == ["sample", "fastq_1", "fastq_2"]:
        return
    err(f"{path.name}: header {header} is neither "
        f"['sample','bam'] nor ['sample','fastq_1','fastq_2']")


def main() -> int:
    params = sorted((ROOT / "params").glob("*.yaml"))
    if not params:
        err("no params/*.yaml files found")
    for p in params:
        check_params(p)

    sheets = sorted((ROOT / "assets").glob("samplesheet*.csv"))
    if not sheets:
        err("no assets/samplesheet*.csv files found")
    for s in sheets:
        check_samplesheet(s)

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print("  -", e)
        return 1
    print(f"OK: {len(params)} params file(s) and {len(sheets)} samplesheet(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
