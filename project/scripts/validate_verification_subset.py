#!/usr/bin/env python3
"""Validate schema completeness of ``artifacts/verification_runs/``.

For each run listed in ``manifest.json`` / ``reports/verification_run_ids.txt``,
require:
- ``metadata.json`` with ``inference_mode == real_inference`` and ``n_examples == 2000``
- ``metrics.json`` with accuracy/macro_f1/ece
- ``resolved_config.yaml``
- ``predictions_sample.jsonl`` with ``prediction_rows_copied`` (or at least 1) rows

Writes ``reports/diagnostics/verification_subset_check.md``.
Exit 0 on success, 1 on failure.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_FILES = (
    "metadata.json",
    "metrics.json",
    "resolved_config.yaml",
    "predictions_sample.jsonl",
)


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _read_run_ids(path: Path) -> list[str]:
    out: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out


def _count_jsonl(path: Path) -> int:
    n = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
    return n


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=None)
    parser.add_argument(
        "--out",
        default="reports/diagnostics/verification_subset_check.md",
    )
    args = parser.parse_args()
    root = Path(args.project_root) if args.project_root else _project_root()

    failures: list[str] = []
    notes: list[str] = []

    ids_path = root / "reports" / "verification_run_ids.txt"
    dest = root / "artifacts" / "verification_runs"
    manifest_path = dest / "manifest.json"

    if not ids_path.exists():
        failures.append(f"missing {ids_path.relative_to(root)}")
    if not manifest_path.exists():
        failures.append(f"missing {manifest_path.relative_to(root)}")

    if failures:
        _write(root / args.out, failures, notes)
        print("VERIFICATION_SUBSET_FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1

    run_ids = _read_run_ids(ids_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    by_id = {r["run_id"]: r for r in manifest.get("runs", [])}

    for run_id in run_ids:
        run_dir = dest / run_id
        if not run_dir.is_dir():
            failures.append(f"missing run directory: {run_dir.relative_to(root)}")
            continue
        for name in REQUIRED_FILES:
            if not (run_dir / name).exists():
                failures.append(f"{run_id}: missing {name}")

        meta_path = run_dir / "metadata.json"
        metrics_path = run_dir / "metrics.json"
        preds_path = run_dir / "predictions_sample.jsonl"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if meta.get("inference_mode") != "real_inference":
                failures.append(
                    f"{run_id}: expected inference_mode=real_inference, got {meta.get('inference_mode')!r}"
                )
            if int(meta.get("n_examples", 0)) != 2000:
                failures.append(
                    f"{run_id}: expected metadata n_examples=2000, got {meta.get('n_examples')}"
                )
        if metrics_path.exists():
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            for key in ("accuracy", "macro_f1", "ece"):
                if key not in metrics:
                    failures.append(f"{run_id}: metrics.json missing {key}")
        if preds_path.exists():
            nrows = _count_jsonl(preds_path)
            expected = int(by_id.get(run_id, {}).get("prediction_rows_copied", 200))
            if nrows <= 0:
                failures.append(f"{run_id}: predictions_sample.jsonl is empty")
            elif nrows != expected:
                failures.append(
                    f"{run_id}: prediction sample rows={nrows}, manifest expected={expected}"
                )

    if not failures:
        notes.append(f"validated {len(run_ids)} verification run directories")
        notes.append("required files + real_inference + n_examples=2000 OK")

    out_path = root / args.out
    _write(out_path, failures, notes)
    if failures:
        print("VERIFICATION_SUBSET_FAIL")
        for f in failures:
            print(f"  - {f}")
        print(f"wrote {out_path}")
        return 1
    print("VERIFICATION_SUBSET_OK")
    print(f"wrote {out_path}")
    return 0


def _write(path: Path, failures: list[str], notes: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status = "FAIL" if failures else "PASS"
    lines = [
        "# Verification subset schema check",
        "",
        f"Status: **{status}**",
        "",
        "## Notes",
        "",
    ]
    if notes:
        lines.extend(f"- {n}" for n in notes)
    else:
        lines.append("- (none)")
    lines.extend(["", "## Failures", ""])
    if failures:
        lines.extend(f"- {f}" for f in failures)
    else:
        lines.append("- None")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
