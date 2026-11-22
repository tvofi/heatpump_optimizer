_shared: out-of-tree generator (probe_template.py, spec.py, gen_probes.py), the should-fail map (sf.py) and the results writer (write_result.py) the box ran from $HOME/scratch; they generate and record every probe_<key>.py
autoresult.sh: loop that runs write_result.py per gated key and checkpoints
