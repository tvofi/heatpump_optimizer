import sys, subprocess
sys.path.insert(0, "tools/release")
import stamp
tags = [t for t in subprocess.run(["git","tag","--list"],capture_output=True,text=True).stdout.split() if stamp.TAG_RE.match(t)]
cur = open("VERSION").read().strip()
print("VERSION", cur, "ntags", len(tags))
base = stamp.bump_base(cur, tags)
print("bump_base", base)
print("next_version(base,patch)", stamp.next_version(base,"patch",None,None))
print("next_version(VERSION,patch) [old rule]", stamp.next_version(cur,"patch",None,None))
print("last_stamped_tag", stamp.last_stamped_tag(tags, stamp.tag_version))
top = max(stamp.version_tuple(t) for t in tags); print("old last_tag (newest tag)", "v"+".".join(map(str,top)))
mism=[t for t in tags if (stamp.tag_version(t) or "").strip()!=t[1:]]
print("tags whose tree VERSION != name:", sorted(mism, key=stamp.version_tuple))
lt = stamp.last_stamped_tag(tags, stamp.tag_version)
import inspect
print("window_log_args sig", inspect.signature(stamp.window_log_args))
# The state the finding was filed in: tags up to v7.1.2, VERSION 7.1.1 (main before the v7.1.3 stamp).
pre = [t for t in tags if stamp.version_tuple(t) <= (7, 1, 2)]
b2 = stamp.bump_base("7.1.1", pre)
print("PRE-STAMP STATE: tags<=v7.1.2", len(pre), "bump_base", b2, "next", stamp.next_version(b2, "patch", None, None), "old rule next", stamp.next_version("7.1.1", "patch", None, None), "v7.1.2 exists", "v7.1.2" in pre)
print("PRE-STAMP last_stamped_tag", stamp.last_stamped_tag(pre, stamp.tag_version), "old newest", "v"+".".join(map(str, max(stamp.version_tuple(t) for t in pre))))
print("rule4 window args", stamp.window_log_args(stamp.last_stamped_tag(pre, stamp.tag_version), "HEAD") if True else "")
