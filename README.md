# ecDNA-WGS-circdna

[![CI](https://github.com/arjunbioinfo/ecDNA-WGS-circdna/actions/workflows/ci.yml/badge.svg)](https://github.com/arjunbioinfo/ecDNA-WGS-circdna/actions/workflows/ci.yml)

A reproducible wrapper around [**nf-core/circdna** v1.1.0](https://nf-co.re/circdna/1.1.0)
for detecting **extrachromosomal circular DNA (ecDNA)** and other circular DNA
from **whole-genome sequencing (WGS)**. It pins the pipeline version, keeps all
parameters in versioned `-params-file` YAMLs (one per detection branch), and
keeps licensed/large inputs (Mosek license, AmpliconArchitect data repo,
containers) **out of the repo**.

The wrapper does not reimplement anything — it launches the upstream
`nf-core/circdna` pipeline reproducibly.

## Detection branches

| Branch | Tool | Best for | On WGS |
| --- | --- | --- | --- |
| `ampliconarchitect` | AmpliconArchitect (AmpliconSuite) | **Amplified ecDNA** | ✅ validated WGS branch |
| `circle_map_realign` | Circle-Map Realign | eccDNA | ⚠️ works, tuned for Circle-seq/ATAC |
| `circle_map_repeats` | Circle-Map Repeats | repetitive eccDNA | ⚠️ works, tuned for Circle-seq/ATAC |
| `circexplorer2` | CIRCexplorer2 | circular junctions | ⚠️ works, tuned for Circle-seq/ATAC |

For **amplified ecDNA from WGS**, use `ampliconarchitect` — the branch the
pipeline documents as WGS-only. The other three are included for smaller
eccDNAs; on WGS they can yield more false positives, so treat their calls with
caution.

## Prerequisites

- [Nextflow](https://www.nextflow.io/) ≥ 22.10 and a container engine
  (Singularity/Apptainer recommended, or Docker).
- For the `ampliconarchitect` branch: the **AmpliconArchitect data repo**, a
  **Mosek license** (`mosek.lic`), and the pipeline **containers**. If you keep
  these in a local folder (e.g. `tsd_transfer`), point `env.sh` at them — see
  below. Get them via
  [AmpliconSuite-pipeline](https://github.com/AmpliconSuite/AmpliconSuite-pipeline).

## Quick start

```bash
# 1. one-time: tell the wrapper where your local resources live
cp env.sh.example env.sh
$EDITOR env.sh          # set AA_DATA_REPO, MOSEK_LICENSE_DIR, NXF_SINGULARITY_CACHEDIR

# 2. list your WGS samples (edit with real absolute paths)
$EDITOR assets/samplesheet_bam.csv     # sample,bam   (or use samplesheet_fastq.csv)

# 3. run a branch (amplified ecDNA from WGS)
./run.sh ampliconarchitect
#   ...or: make ampliconarchitect

# other branches:
./run.sh circle_map_realign
./run.sh circle_map_repeats
./run.sh circexplorer2
```

`run.sh` pins `-r 1.1.0`, loads `env.sh`, injects `--aa_data_repo` and
`--mosek_license_dir` from your environment (only for `ampliconarchitect`), and
launches with `-params-file params/<branch>.yaml -c nextflow.config`.

## Input

Edit `assets/samplesheet_bam.csv` (WGS aligned BAMs):

```csv
sample,bam
tumor_wgs_1,/abs/path/tumor_wgs_1.bam
```

Or start from FASTQ with `assets/samplesheet_fastq.csv` and set
`input_format: FASTQ` + `input: assets/samplesheet_fastq.csv` in the branch's
params file.

## Configuration

- **Parameters** live in `params/*.yaml` (genome, `circle_identifier`,
  `reference_build`, `aa_cngain`, resource caps, …). circdna requires
  parameters to be passed via `-params-file`, **not** `-c`.
- **Resources / containers** live in `nextflow.config`, passed with `-c`
  (executor, retries, Singularity settings only — no parameters).
- **Machine-specific paths** live in `env.sh` (git-ignored).

Default `genome`/`reference_build` is `GRCh38`; for GRCh37 set both to
`GRCh37` (and use a matching AA data repo build). For mouse use `mm10`.

## Reproducibility & data safety

- Pipeline version pinned to **1.1.0** in `run.sh` (`nextflow pull nf-core/circdna`
  to refresh the cache).
- All run settings are captured in the committed `params/*.yaml` — commit the
  params file alongside your results.
- `.gitignore` blocks the Mosek license, AA data repo, containers, BAM/FASTQ,
  and `work/`/`results/` so licensed or large data is never committed. **Keep
  patient/controlled WGS data and any licensed files out of this public repo.**

## Layout

```text
run.sh                     pinned launcher (./run.sh <branch>)
params/<branch>.yaml       parameters per detection branch (-params-file)
nextflow.config            executor/container/resource config (-c)
assets/samplesheet_*.csv   input templates (BAM / FASTQ)
env.sh.example             copy to env.sh; local paths to AA repo/Mosek/containers
ci/validate.py             lint params + samplesheets (run by CI)
Makefile                   make ampliconarchitect | validate | clean
```

## Credits & citation

This wrapper runs **nf-core/circdna**, originally written by Daniel Schreyer
(University of Glasgow). Please cite the pipeline
([doi:10.5281/zenodo.6685250](https://doi.org/10.5281/zenodo.6685250)) and the
underlying tools (AmpliconArchitect, Circle-Map, CIRCexplorer2). See the
[nf-core/circdna citations](https://github.com/nf-core/circdna/blob/1.1.0/CITATIONS.md).

## License

MIT — see `LICENSE`. (Applies to this wrapper only; nf-core/circdna and the
bundled tools carry their own licenses.)
