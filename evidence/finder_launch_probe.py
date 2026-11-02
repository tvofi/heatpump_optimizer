import os, sys, time, tempfile, importlib.util
from pathlib import Path
seat = Path(sys.argv[1])
sys.path.insert(0, str(seat))
spec = importlib.util.spec_from_file_location("od", seat / "open_driver.py")
od = importlib.util.module_from_spec(spec); spec.loader.exec_module(od)
SHA = "1"*40
topics = ["z$(touch${IFS}INJECTED)", "r10-a;touch INJECTED", "r10-`touch INJECTED`", "r10-nl\ntouch INJECTED",
          "-x", "--help", "r10-q'uote\"d", "a/b", "r10-plain"]
bad = 0; n = 0
for sdname in ["state dir", "state$HOME dir", "st$(touch INJECTED)"]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        sd = tmp / sdname
        (sd / "open-driver").mkdir(parents=True)
        scratch = tmp / "scratch"; scratch.mkdir()
        opener = tmp / "open_pr.sh"
        opener.write_text('printf "%s|" "$@" > "$ARGS_OUT"; echo ran\n')
        w = od.World(str(scratch), sd)
        if hasattr(w, "opener"): w.opener = opener
        else: od.HERE = tmp
        for i, topic in enumerate(topics):
            argsf = tmp / f"args{i}.txt"; os.environ["ARGS_OUT"] = str(argsf)
            try:
                w.launch(topic, SHA, "T x", "G")
            except Exception as e:
                print(f"FAIL sd={sdname!r} topic={topic!r} launch raised {e!r}"); bad += 1; n += 1; continue
            rcf = sd / "open-driver" / f"{od.stem(topic) if hasattr(od,'stem') else topic}.rc"
            for _ in range(50):
                if rcf.exists() and rcf.read_text().strip(): break
                time.sleep(0.05)
            ok_rc = rcf.exists() and rcf.read_text().strip() == "0"
            ok_args = argsf.exists() and argsf.read_text() == f"{topic}|{SHA}|T x|G|"
            n += 1
            ok = ok_rc and ok_args
            bad += not ok
            print(f"{'ok  ' if ok else 'FAIL'} sd={sdname!r} topic={topic!r} rc_file_0={ok_rc} args_exact={ok_args}")
        inj = list(tmp.rglob("INJECTED")) + list(Path(scratch).glob("INJECTED"))
        n += 1; bad += bool(inj)
        print(f"{'FAIL' if inj else 'ok  '} sd={sdname!r} INJECTED created: {bool(inj)}")
    # run_pass reap of a slash topic: rc file read via stem
print(f"RESULT launch_probe checks={n} failed={bad}")
