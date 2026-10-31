import sys; sys.path.insert(0, sys.argv[1]); import roster_sync as RS
for i in range(2):
    rc = RS.main(["--checkout", sys.argv[2], "--pr-state", sys.argv[3], "--apply", "--roster-ref", "main", "--branch", "x"])
    print("RESULT pass", i, "rc", rc)
