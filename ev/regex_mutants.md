Head 1c27fd6329462169e2d9a9f934edcc18596d13be. probe.py execs tests/entities.py's text from `_D308_NUM = (` up to `_D308_CARRIED = _D308_COUNT_RE` and runs the planted corpus (copied from the check) plus reviewer probes. Each mutant is a scratch copy of entities.py; the tree was not modified.

head: planted missed: []
Ma_numdigits ("one" -> "zzqq"): planted missed: []   (SURVIVES: no planted wording relies on a bare "one"; "twenty-one" still matches through "twenty")
Mb_nowords ({0,3} -> {0,0}): planted missed: ['the lane reaches all 124 production files', '190 script pairs', '190 of the 561 script pairs', 'Eighteen of the pairs', 'twenty-one shared production files']   KILLED
Mc_nountil (until alternative removed): planted missed: ['96 until R9 F2.2', 'eleven until']   KILLED
Md_nocase (IGNORECASE -> 0): planted missed: ['Eighteen of the pairs', 'EIGHTEEN PAIRS']   KILLED
Me_digitsonly (spelled-out numbers removed): planted missed: ['Eighteen of the pairs', 'EIGHTEEN PAIRS', 'twenty-one shared production files', 'eleven until']   KILLED

Reviewer probes at head (not in the corpus):
'18 at exactly 1.00': not refused
'among 435 comparable pairs': REFUSED
'192 of 561 pairs': REFUSED
'a/b (41)': not refused
'one hundred and twenty-five production files': REFUSED
'125 production modules': not refused
'the lane reaches all 125 production-module files': REFUSED
'124 of them': not refused
'thirty-four scripts': not refused
'(34 choose 2)': not refused
