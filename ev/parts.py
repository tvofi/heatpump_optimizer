# parts.py <entities.py>: the reach check's file arms, each alone
import runpy, sys, io, contextlib
sys.argv = ["reach.py", sys.argv[1]]
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("$HOME/hpo-seats/r11/fix3729-r6/ev/reach.py")
print("files planted", sorted(g["ns"]["_r11_files_planted"]))
print("shipped planted", sorted(g["ns"]["_r11_shipped_planted"]()))
print("live files read", len(g["ns"]["_r11_files"]))
