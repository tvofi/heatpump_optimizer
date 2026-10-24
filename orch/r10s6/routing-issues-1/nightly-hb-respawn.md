R10-NIGHTLY-PYSPY-RETRY (#2605) cut py-spy at 5 s, but real Home Assistant's py-spy hang is per process, so a retry on the same process rescued 0 of 2 and the stable lane's false-red rate stays about 6.7 %. Respawn the process under test, or grade the lane so a py-spy hang is not a red.

Roster group: `R10-NIGHTLY-HB-RESPAWN`. Part of #201.
