#!/usr/bin/env python3
"""Run full config grid (e.g. 3 precisions x 2 tasks x 5 templates).

TODO: Load sweep YAML; expand_sweep; run_single for each; optional Flyte later.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

def main():
    print("Grid runner not yet implemented")
    return 1


if __name__ == "__main__":
    sys.exit(main())
