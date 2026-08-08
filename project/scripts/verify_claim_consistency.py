#!/usr/bin/env python3
"""Verify report tables/hypothesis text stay consistent with verification artifacts.

Checks (no GPU, no full predictions.jsonl required):
1. ``reports/verification_run_ids.txt`` matches ``artifacts/verification_runs/manifest.json``.
2. Each finalized run_id appears in ``reports/final_metrics.md`` with metrics matching
   ``artifacts/verification_runs/<run_id>/metrics.json`` (within float tolerance).
3. ``reports/run_ids_manifest.md`` references all finalized run IDs.
4. ``reports/hypothesis_tests.md`` retains required decision phrases for the
   current evidence boundaries (partial matrix / secondary unevaluated).

Writes a short log to ``reports/diagnostics/claim_consistency.md``.
Exit code 0 on success, 1 on any failure.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_HYPOTHESIS_PHRASES = [
    "10/15",
    "not evaluated",
    "descriptive only",
]

METRIC_KEYS = ("accuracy", "macro_f1", "ece")


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


def _parse_metrics_table(path: Path) -> dict[str, dict[str, float]]:
    """Parse markdown table keyed by run_id."""
    rows: dict[str, dict[str, float]] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return rows
    headers = [h.strip() for h in lines[0].strip("|").split("|")]
    for line in lines[2:]:
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        record = dict(zip(headers, cells))
        run_id = record.get("run_id", "")
        if not run_id:
            continue
        parsed: dict[str, float] = {}
        for key in METRIC_KEYS:
            parsed[key] = float(record[key])
        if "ace" in record and record["ace"]:
            parsed["ace"] = float(record["ace"])
        parsed["n_examples"] = float(record.get("n_examples", "0"))
        rows[run_id] = parsed
    return rows


def _approx_equal(a: float, b: float, tol: float = 1e-5) -> bool:
    return abs(a - b) <= tol


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        default=None,
        help="Project root (default: parent of scripts/)",
    )
    parser.add_argument(
        "--out",
        default="reports/diagnostics/claim_consistency.md",
        help="Diagnostics markdown output path (relative to project root)",
    )
    args = parser.parse_args()

    root = Path(args.project_root) if args.project_root else _project_root()
    failures: list[str] = []
    notes: list[str] = []

    ids_path = root / "reports" / "verification_run_ids.txt"
    manifest_path = root / "artifacts" / "verification_runs" / "manifest.json"
    metrics_md = root / "reports" / "final_metrics.md"
    hyp_md = root / "reports" / "hypothesis_tests.md"
    run_manifest_md = root / "reports" / "run_ids_manifest.md"

    for path in (ids_path, manifest_path, metrics_md, hyp_md, run_manifest_md):
        if not path.exists():
            failures.append(f"missing required file: {path.relative_to(root)}")

    if failures:
        _write_report(root / args.out, failures, notes)
        print("CLAIM_CONSISTENCY_FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1

    file_ids = _read_run_ids(ids_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_ids = [r["run_id"] for r in manifest.get("runs", [])]

    if sorted(file_ids) != sorted(manifest_ids):
        failures.append(
            "verification_run_ids.txt does not match artifacts/verification_runs/manifest.json "
            f"(file={len(file_ids)}, manifest={len(manifest_ids)})"
        )
    else:
        notes.append(f"run ID lists match ({len(file_ids)} runs)")

    if len(file_ids) != 10:
        failures.append(f"expected 10 finalized run IDs, found {len(file_ids)}")

    table = _parse_metrics_table(metrics_md)
    missing_in_table = sorted(set(file_ids) - set(table))
    if missing_in_table:
        failures.append(f"final_metrics.md missing run_ids: {missing_in_table}")

    extra_in_table = sorted(set(table) - set(file_ids))
    if extra_in_table:
        failures.append(f"final_metrics.md has unexpected run_ids: {extra_in_table}")

    for run_id in file_ids:
        metrics_path = root / "artifacts" / "verification_runs" / run_id / "metrics.json"
        if not metrics_path.exists():
            failures.append(f"missing metrics.json for {run_id}")
            continue
        artifact = json.loads(metrics_path.read_text(encoding="utf-8"))
        if run_id not in table:
            continue
        row = table[run_id]
        for key in METRIC_KEYS:
            if key not in artifact:
                failures.append(f"{run_id}: metrics.json missing {key}")
                continue
            if not _approx_equal(float(artifact[key]), float(row[key])):
                failures.append(
                    f"{run_id}: {key} mismatch table={row[key]} artifact={artifact[key]}"
                )
        if int(row.get("n_examples", 0)) != 2000:
            failures.append(f"{run_id}: expected n_examples=2000, got {row.get('n_examples')}")

    if not failures:
        notes.append("final_metrics.md matches verification metrics.json within 1e-5")

    manifest_text = run_manifest_md.read_text(encoding="utf-8")
    missing_refs = [rid for rid in file_ids if rid not in manifest_text]
    if missing_refs:
        failures.append(f"run_ids_manifest.md missing references: {missing_refs}")
    else:
        notes.append("run_ids_manifest.md references all finalized run IDs")

    hyp_text = hyp_md.read_text(encoding="utf-8")
    for phrase in REQUIRED_HYPOTHESIS_PHRASES:
        if phrase.lower() not in hyp_text.lower():
            failures.append(f"hypothesis_tests.md missing required phrase: {phrase!r}")
    if not re.search(r"0\.09846\d*", hyp_text):
        failures.append("hypothesis_tests.md missing primary point estimate ~0.098465")
    if not any(f.startswith("hypothesis_tests.md") for f in failures):
        notes.append("hypothesis_tests.md retains partial-matrix / unevaluated boundaries")

    out_path = root / args.out
    _write_report(out_path, failures, notes)

    if failures:
        print("CLAIM_CONSISTENCY_FAIL")
        for f in failures:
            print(f"  - {f}")
        print(f"wrote {out_path}")
        return 1

    print("CLAIM_CONSISTENCY_OK")
    print(f"wrote {out_path}")
    return 0


def _write_report(path: Path, failures: list[str], notes: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status = "FAIL" if failures else "PASS"
    lines = [
        "# Claim consistency check",
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
