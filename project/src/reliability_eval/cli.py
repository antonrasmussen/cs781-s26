"""CLI entrypoint for the reliability evaluation harness."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _project_root() -> Path:
    """Infer project root from package location."""
    return Path(__file__).resolve().parents[2]


def _cmd_run(args: argparse.Namespace) -> int:
    """Run single experiment."""
    from reliability_eval.config.resolve import resolve_config
    from reliability_eval.experiments.run_single import run_single

    project_root = _project_root()
    config = resolve_config(
        project_root,
        sweep_id=args.sweep,
        dataset_id=args.dataset,
        model_id=args.model,
        precision_id=args.precision,
        template_id=args.template,
        calibration_id=args.calibration,
        execution_profile=args.profile,
        sample_size=args.sample_size,
    )
    run_id = run_single(config=config)
    print(run_id)
    return 0


def _cmd_sweep(args: argparse.Namespace) -> int:
    """Run sweep grid."""
    from reliability_eval.experiments.run_grid import expand_sweep
    from reliability_eval.experiments.run_single import run_single

    project_root = _project_root()
    configs = expand_sweep(
        project_root,
        args.sweep,
        execution_profile=args.profile,
        sample_size=args.sample_size,
    )

    if args.dry_run:
        print(f"Would run {len(configs)} configs")
        for i, cfg in enumerate(configs):
            print(f"  {i+1}: {cfg.get('precision', {}).get('precision')} / {cfg.get('template_id')}")
        return 0

    for config in configs:
        run_id = run_single(config=config)
        print(run_id)
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    """Aggregate runs into report. Stub."""
    print("report: not yet implemented")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="reliability-eval",
        description="Reliability of quantized biomedical LLMs: calibration and prompt stability.",
    )
    parser.add_argument("--help-commands", action="store_true", help="Show subcommands")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # run
    run_parser = subparsers.add_parser("run", help="Run single experiment")
    run_parser.add_argument("--sweep", default="mvp_pubmed")
    run_parser.add_argument("--dataset", default="pubmed_rct")
    run_parser.add_argument("--model", default="biomistral_7b")
    run_parser.add_argument("--precision", default="fp16")
    run_parser.add_argument("--template", default="pubmed_t1")
    run_parser.add_argument("--calibration", default="none")
    run_parser.add_argument(
        "--profile",
        default="local",
        choices=["local", "local_real", "flyte_sandbox", "odu"],
    )
    run_parser.add_argument("--sample-size", type=int, default=None)
    run_parser.set_defaults(func=_cmd_run)

    # sweep
    sweep_parser = subparsers.add_parser("sweep", help="Run sweep grid")
    sweep_parser.add_argument("--sweep", default="mvp_pubmed")
    sweep_parser.add_argument(
        "--profile",
        default="local",
        choices=["local", "local_real", "flyte_sandbox", "odu"],
    )
    sweep_parser.add_argument("--sample-size", type=int, default=None)
    sweep_parser.add_argument("--dry-run", action="store_true")
    sweep_parser.set_defaults(func=_cmd_sweep)

    # report
    report_parser = subparsers.add_parser("report", help="Aggregate runs into report")
    report_parser.set_defaults(func=_cmd_report)

    args = parser.parse_args()

    if args.help_commands:
        print("Commands: run, sweep, report")
        return 0

    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
