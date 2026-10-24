// Clean fixture: one population per histogram, every canonical lookup through canon().
const bump = (hist, key, pr) => hist.set(key, (hist.get(key) ?? 0) + 1)
let INDEX = null
INDEX ??= policyKeyIndex()
function key(id) { return INDEX.has(canon(id)) ? INDEX.get(canon(id)) : id }
for (const w of words) bump(verdicts, w, 1)
