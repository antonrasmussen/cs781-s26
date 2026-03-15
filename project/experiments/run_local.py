#!/usr/bin/env python3
"""Run a single experiment from a resolved config (local harness).

TODO: Resolve config from CLI; call reliability_eval.experiments.run_single.run_single.
"""
import sys

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

def main():
    # Stub: not yet implemented
    from reliability_eval.experiments import run_single as rs
    print("run_single not yet implemented; config resolution TODO")
    return 1


if __name__ == "__main__":
    sys.exit(main())
