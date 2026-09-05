"""Subprocess entry for the #290 process-pool gate check."""
from __future__ import annotations

import asyncio
import os
import sys

sys.path[:0] = ["tests/hastub", "custom_components"]
os.environ["HPO_SOLVE_PROCESS"] = "1"

from heatpump_optimizer.solve_process import (  # noqa: E402
    async_run_solve_job,
    shutdown_solve_pool,
    worker_pid,
)


async def main() -> None:
    parent = os.getpid()
    child = await async_run_solve_job(None, worker_pid)
    shutdown_solve_pool()
    print(parent, child)


if __name__ == "__main__":
    asyncio.run(main())
