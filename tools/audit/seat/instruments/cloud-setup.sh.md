# `cloud-setup.sh`

- `cloud-setup.sh` — the cloud seat environment's setup script (interpreter,
  CI-run pinning): it builds `venv-ci` and `venv-ha` under `/opt/hpo` and
  writes the toolchain profile. When: tvofi pastes it into Project settings; a
  seat cannot apply its own environment. A seat's Bash call inherits the
  agent's environment and reads neither the profile nor `BASH_ENV`, so the
  toolchain reaches it only through the environment's variables, which
  `--variables` prints and the setup run's last line names; `--check`, in a
  seat: `OK` (exit 0) only when all three hold, or `REFUSE` naming them (exit
  1). `--kernels <command> [<argument>...]` runs the command once per OpenBLAS
  kernel class of the script's `KERNELS` (SkylakeX, Haswell, Sandybridge,
  Nehalem), the pin lifted for it. When: before trusting a check that reads a
  solve, because the seat is pinned to one class and CI's runners load whichever
  their processor selects (#3602: two clauses green under the pin, red on
  `tests / fast (3.14)`). It prints `cloud-setup kernels: <class> exit <rc>` per
  class and one closing line naming the classes run, red and not run; a class
  OpenBLAS does not report loading here is not run, never green. Exit 0 every
  class run is green, 1 one is red, 2 none ran. The profile prepends `venv-ci/bin` only
  when absent, so a PATH a caller narrowed is left alone, and sets every other
  variable only where it is unset, so a `BASH_ENV` naming it changes no value a
  caller handed its child; `--self-test`: the profile, variables and check
  arms, and that every name the profile exports keeps a caller's value under
  `BASH_ENV`. Refusal: a missing checkout warns and
  exits 0, so a session still starts, without pins.
