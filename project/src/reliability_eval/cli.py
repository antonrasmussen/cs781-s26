"""CLI entrypoint for the reliability evaluation harness.

TODO: Implement subcommands (run, sweep, report) and config resolution.
"""
import argparse


def main() -> int:
    """Entrypoint. TODO: Wire to run_single / run_grid / report."""
    parser = argparse.ArgumentParser(
        prog="reliability-eval",
        description="Reliability of quantized biomedical LLMs: calibration and prompt stability.",
    )
    parser.add_argument("--help-commands", action="store_true", help="Show planned commands")
    args = parser.parse_args()
    if args.help_commands:
        print("Planned: run, sweep, report (not yet implemented)")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
