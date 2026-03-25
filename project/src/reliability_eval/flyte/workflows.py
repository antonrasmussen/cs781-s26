"""Flyte workflow: sweep over config matrix. Thin wrapper over run_single."""

from __future__ import annotations

try:
    from flytekit import workflow
except ImportError:
    workflow = None  # type: ignore

from reliability_eval.flyte.tasks import run_single_task


def _run_single_workflow_impl(config: dict, run_id: str) -> str:
    """Plain Python implementation; no Flyte dependency."""
    from reliability_eval.experiments.run_single import run_single
    return run_single(config=config, run_id=run_id)


if workflow is not None:

    @workflow
    def run_single_workflow(config: dict, run_id: str) -> str:
        """Flyte workflow: run one config. Delegates to run_single_task."""
        return run_single_task(config=config, run_id=run_id)

    @workflow
    def sweep_workflow(config: dict, run_id: str) -> str:
        """Flyte workflow: run one config from sweep. For full sweep use run_grid."""
        return run_single_task(config=config, run_id=run_id)

else:

    def run_single_workflow(config: dict, run_id: str) -> str:
        """Flyte workflow: run one config. Delegates to run_single."""
        return _run_single_workflow_impl(config=config, run_id=run_id)

    def sweep_workflow(config: dict, run_id: str) -> str:
        """Flyte workflow: run one config from sweep."""
        return _run_single_workflow_impl(config=config, run_id=run_id)
