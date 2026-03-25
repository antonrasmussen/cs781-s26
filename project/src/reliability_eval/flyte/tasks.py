"""Flyte tasks wrapping run_single and aggregate. Thin wrappers only."""

from __future__ import annotations

try:
    from flytekit import task
except ImportError:
    task = None  # type: ignore


def _run_single_impl(config: dict, run_id: str) -> str:
    """Plain Python implementation; no Flyte dependency."""
    from reliability_eval.experiments.run_single import run_single
    return run_single(config=config, run_id=run_id)


if task is not None:

    @task
    def run_single_task(config: dict, run_id: str) -> str:
        """Flyte task: run one config. Delegates to run_single."""
        return _run_single_impl(config=config, run_id=run_id)

else:

    def run_single_task(config: dict, run_id: str) -> str:
        """Flyte task: run one config. Delegates to run_single."""
        return _run_single_impl(config=config, run_id=run_id)
