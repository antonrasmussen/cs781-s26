#!/usr/bin/env python3
"""Watch matrix progress and automatically retry failed cells."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import yaml

from reliability_eval.config.resolve import resolve_config
from reliability_eval.experiments.run_single import run_single


def _read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _target_cells(precisions: list[str], templates: list[str]) -> list[tuple[str, str]]:
    return [(p, t) for p in precisions for t in templates]


def _completed_cells(artifact_root: Path, sample_size: int, experiment_name: str) -> dict[tuple[str, str], str]:
    done: dict[tuple[str, str], str] = {}
    if not artifact_root.exists():
        return done
    for run_dir in sorted([p for p in artifact_root.iterdir() if p.is_dir()]):
        cfg_path = run_dir / "resolved_config.yaml"
        meta_path = run_dir / "metadata.json"
        metrics_path = run_dir / "metrics.json"
        if not (cfg_path.exists() and meta_path.exists() and metrics_path.exists()):
            continue
        cfg = _read_yaml(cfg_path)
        if cfg.get("experiment_name") != experiment_name:
            continue
        if int(cfg.get("sample_size", 0)) != int(sample_size):
            continue
        meta = _read_json(meta_path)
        if meta.get("inference_mode") != "real_inference":
            continue
        key = (cfg.get("precision", {}).get("precision", "unknown"), cfg.get("template_id", "unknown"))
        done[key] = run_dir.name
    return done


def _load_state(path: Path) -> dict:
    if not path.exists():
        return {"attempts": {}, "last_error": {}}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_state(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _cell_key(precision: str, template: str) -> str:
    return f"{precision}::{template}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Retry-safe matrix watcher runner.")
    parser.add_argument("--sample-size", type=int, default=2000)
    parser.add_argument("--precisions", default="fp16,int4", help="Comma-separated precision IDs")
    parser.add_argument(
        "--templates",
        default="pubmed_t1,pubmed_t2,pubmed_t3,pubmed_t4,pubmed_t5",
        help="Comma-separated template IDs",
    )
    parser.add_argument("--execution-profile", default="local_real")
    parser.add_argument("--sweep-id", default="final_pubmed")
    parser.add_argument("--dataset-id", default="pubmed_rct")
    parser.add_argument("--model-id", default="biomistral_7b")
    parser.add_argument("--calibration-id", default="none")
    parser.add_argument("--experiment-name", default="final_pubmed_reliability")
    parser.add_argument("--artifact-root", default="artifacts/runs")
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--retry-backoff-sec", type=int, default=120)
    parser.add_argument("--poll-sec", type=int, default=20)
    parser.add_argument("--state-file", default="artifacts/runs/watch_state.json")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    artifact_root = Path(args.artifact_root)
    state_path = Path(args.state_file)
    state = _load_state(state_path)
    precisions = [x.strip() for x in args.precisions.split(",") if x.strip()]
    templates = [x.strip() for x in args.templates.split(",") if x.strip()]
    targets = _target_cells(precisions, templates)

    while True:
        done = _completed_cells(
            artifact_root=artifact_root,
            sample_size=args.sample_size,
            experiment_name=args.experiment_name,
        )
        missing = [cell for cell in targets if cell not in done]
        print(f"[watcher] done={len(done)}/{len(targets)} missing={len(missing)}")
        if not missing:
            print("[watcher] target matrix complete")
            return 0

        progressed = False
        for precision, template in missing:
            key = _cell_key(precision, template)
            tries = int(state["attempts"].get(key, 0))
            if tries >= args.max_retries:
                print(f"[watcher] skip {key} (retries exhausted: {tries})")
                continue

            print(f"[watcher] run {key} attempt {tries + 1}/{args.max_retries}")
            cfg = resolve_config(
                project_root,
                sweep_id=args.sweep_id,
                dataset_id=args.dataset_id,
                model_id=args.model_id,
                precision_id=precision,
                template_id=template,
                calibration_id=args.calibration_id,
                execution_profile=args.execution_profile,
                sample_size=args.sample_size,
                experiment_name=args.experiment_name,
            )
            try:
                run_id = run_single(cfg)
                print(f"[watcher] success {key} -> {run_id}")
                state["attempts"][key] = tries + 1
                state["last_error"].pop(key, None)
                _save_state(state_path, state)
                progressed = True
            except Exception as e:  # noqa: BLE001
                state["attempts"][key] = tries + 1
                state["last_error"][key] = str(e)
                _save_state(state_path, state)
                print(f"[watcher] failed {key}: {e}")
                print(f"[watcher] backoff {args.retry_backoff_sec}s")
                time.sleep(args.retry_backoff_sec)

        if args.once:
            return 0

        if not progressed:
            print(f"[watcher] no progress this cycle; sleeping {args.poll_sec}s")
            time.sleep(args.poll_sec)


if __name__ == "__main__":
    raise SystemExit(main())
