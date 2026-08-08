# Environment and dependency pinning

Guidance for reproducing the evaluation pipeline and for locking future manuscript runs.

## Install (from `project/`)

CPU / docs / tests:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
export PYTHONPATH=src
```

CUDA inference:

```bash
pip install -e ".[gpu,dev]"
```

Dependencies are declared in [`pyproject.toml`](../pyproject.toml). [`requirements.txt`](../requirements.txt) points there (no duplicate pin list).

## Hugging Face revisions (pinned for future runs)

| Asset | ID | Pinned revision |
|-------|----|-----------------|
| Dataset | `armanc/pubmed-rct20k` | `091aec1e2384a20b2b36eb96177755ca13dd0b42` |
| Model | `BioMistral/BioMistral-7B` | `9a11e1ffa817c211cbb52ee1fb312dc6b61b40a5` |

Configured in:

- [`configs/datasets/pubmed_rct.yaml`](../configs/datasets/pubmed_rct.yaml)
- [`configs/models/biomistral_7b.yaml`](../configs/models/biomistral_7b.yaml)

**Historical note:** Finalized n=2000 runs (2026-04-27/28) recorded `hf_revision: main` / `revision: main` in `resolved_config.yaml`. The BioMistral `main` tip SHA above was last modified 2024-02-21 and is expected to match those runs. The PubMed dataset tip SHA was captured 2026-05-07; treat exact dataset byte identity for historical runs as tied to `main` at download time (`data/provenance/pubmed_rct_download.json`, 2026-04-25).

## Recommended environment lock (operator)

After a successful CUDA install that can load BioMistral INT8/INT4:

```bash
pip freeze > requirements-lock.txt
python -c "import torch, transformers, bitsandbytes, datasets; \
print('torch', torch.__version__, 'cuda', torch.version.cuda); \
print('transformers', transformers.__version__); \
print('bitsandbytes', bitsandbytes.__version__); \
print('datasets', datasets.__version__)"
```

Commit or archive `requirements-lock.txt` alongside a short note with:

- GPU model and VRAM
- NVIDIA driver version
- CUDA toolkit / torch CUDA build string

A lockfile is **not** yet checked in (version ranges only in `pyproject.toml`). Exact numeric replication of quantized runs may depend on that CUDA stack; see blocked INT8/INT4 cells in `docs/evidence_registry.md`.

## Hardware expectations

- Real inference: Linux CUDA host, preferably ≥16 GB VRAM for BioMistral-7B FP16.
- CPU-only: tests, claim-consistency checks, and documentation rebuilds only.

## Integrity commands (no GPU)

```bash
pytest tests/ -q
python scripts/verify_claim_consistency.py
python scripts/validate_verification_subset.py
```
