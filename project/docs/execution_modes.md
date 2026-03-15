# Execution Modes

The same codebase supports three execution modes. All use the same plain-Python pipeline (`run_single`) and shared artifact contract.

## 1. Local (non-Flyte)

Run experiments directly on your machine. No Flyte, Kubernetes, or remote control plane.

```bash
# Single run
python experiments/run_mvp.py --sample-size 8 --template-id pubmed_t1
python experiments/run_local.py --sweep mvp_pubmed --sample-size 8

# Grid sweep
python experiments/run_grid.py --sweep mvp_pubmed --dry-run   # preview
python experiments/run_grid.py --sweep mvp_pubmed --sample-size 4

# Via CLI
PYTHONPATH=src python -m reliability_eval.cli run --sample-size 8
PYTHONPATH=src python -m reliability_eval.cli sweep --dry-run
```

Set `RELIABILITY_ARTIFACT_ROOT` to override artifact output directory.

## 2. Local Flyte Sandbox

Use Flyte for workflow structure and reproducibility. Runs locally via `flytectl sandbox`; no GKE or remote cluster.

```bash
# Start sandbox (one-time)
flytectl sandbox start

# Run workflow (requires: pip install -e ".[flyte]")
pyflyte run src/reliability_eval/flyte/workflows.py run_single_workflow \
  --config '<resolved_config_dict>' --run_id <run_id>
```

Flyte tasks are thin wrappers: they only call `run_single()`. No business logic in tasks.

## 3. ODU Compute (Burst Execution)

ODU is treated as **plain remote compute**. Run the same scripts/CLI on ODU nodes when heavier runs are needed. No Flyte control plane on ODU.

### How it works

1. Use the `odu` execution profile for hardware settings (e.g. larger batch size).
2. Run the same entrypoints (run_mvp, run_local, run_grid, or CLI) on the ODU environment.
3. Optionally set `RELIABILITY_ARTIFACT_ROOT` to a shared storage path if artifacts should be written to network storage.

### Example

```bash
# On ODU login node or job script
export RELIABILITY_ARTIFACT_ROOT=/path/to/shared/artifacts  # if using shared storage

python experiments/run_grid.py --sweep mvp_pubmed --profile odu
# or
PYTHONPATH=src python -m reliability_eval.cli sweep --sweep mvp_pubmed --profile odu
```

The `odu` profile (`configs/execution/odu.yaml`) sets `inference_mode: real` and larger batch size. The same `run_single` pipeline executes; only config and environment differ.

### Design principle

ODU is **not** a Flyte remote deployment. It is a compute target where you run the same Python code. No Kubernetes, no cluster registration, no remote Flyte backend required.
