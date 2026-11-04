import re,subprocess,sys,tempfile,pathlib
src=pathlib.Path("tests/run.sh").read_text()
pat=re.search(r"^SUMMARY_LINE=.*$",src,re.M); fn=re.search(r"^ended_before_summary\(\) \{.*?^\}",src,re.M|re.S)
with tempfile.TemporaryDirectory() as t:
    c=pathlib.Path(t,"c");f=pathlib.Path(t,"f")
    c.write_text("sampling...\nTraceback (most recent call last):\nOSError\n");f.write_text("  FAIL x\n\n2 of 9 ENTITY CHECKS FAILED\n")
    out=[subprocess.run(["bash","-e","-c",f'{pat.group(0)}\n{fn.group(0)}\nended_before_summary "$1"',"x",str(l)]).returncode for l in (c,f)]
print("pin", "ok" if out==[0,1] else "FAIL", out)
