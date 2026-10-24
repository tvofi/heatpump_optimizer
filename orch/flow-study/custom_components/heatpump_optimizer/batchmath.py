"""Batched reductions whose rows are numpy's own scalar summation order.

One primitive, shared by the solver's batch twins (``optimizer.py``'s cost
terms since R9 F2.2 and ``tariff.py``'s capacity term since R9 F2.5): a row
of the batched reduction must be the scalar ``np.sum`` of that row's
freshly built 1-D array to the bit, on every numpy backend. A reduction
numpy schedules itself -- ``np.sum(m, axis=1)`` over a batch, or over a row
VIEW of one -- treats stride and alignment as inputs and picks its path by
backend (#948: bit-identical on the arm64 seat that wrote it, re-planned
19 of 51 stress scenarios on CI's x86_64, at the production width only).
So the order is reproduced here as explicit column arithmetic instead:
every addition is one elementwise ``+`` across the batch's column, an exact
IEEE operation whatever the memory order around it (fixer.md step 15).
"""
from __future__ import annotations

import numpy as np

#: numpy's unrolled pairwise block: under this width a fresh 1-D sum is
#: eight interleaved partials combined in a fixed tree, above it halving.
#: The value is numpy's own (``PW_BLOCKSIZE`` in ``loops_utils.h``); the
#: replication below is what pins it, at the widths either side of it.
PAIRWISE_BLOCK = 128


def row_sums(rows: np.ndarray) -> np.ndarray:
    """``np.sum`` of each row of a [B, n] array, one pass for the whole batch.

    numpy sums a fresh 1-D array pairwise: under ``PAIRWISE_BLOCK`` elements
    as eight interleaved partial sums combined in a fixed tree, above it by
    halving. This runs exactly that order of additions, but each addition is
    one elementwise ``+`` across the batch's column, so row ``b`` is the
    scalar ``np.sum`` of ``rows[b]`` to the bit while the interpreter works
    once per column block rather than once per row. Only elementwise ufuncs
    touch the values, and they are exact IEEE operations on every numpy
    backend, whatever the memory order or alignment of ``rows`` -- which is
    what ``fixer.md`` step 15 asks of a batch: elementwise end to end. The
    scalar twins call this on a one-row batch, so their agreement with the
    batch is by construction, not by measurement (R9 D9-s1-01, RC-sw1;
    tariff's peak twin since R9 F2.5, RC-rca1).
    """
    n = rows.shape[1]
    if n > PAIRWISE_BLOCK:
        half = n // 2
        half -= half % 8
        halves: np.ndarray = row_sums(rows[:, :half]) + row_sums(rows[:, half:])
        return halves
    if n < 8:
        total = np.full(rows.shape[0], -0.0)
        for j in range(n):
            total = total + rows[:, j]
        summed: np.ndarray = 0.0 + total
        return summed
    partial = rows[:, :8].copy()
    stop = n - n % 8
    for j in range(8, stop, 8):
        partial += rows[:, j:j + 8]
    total = (
        (partial[:, 0] + partial[:, 1]) + (partial[:, 2] + partial[:, 3])
    ) + ((partial[:, 4] + partial[:, 5]) + (partial[:, 6] + partial[:, 7]))
    for j in range(stop, n):
        total = total + rows[:, j]
    result: np.ndarray = 0.0 + total
    return result
