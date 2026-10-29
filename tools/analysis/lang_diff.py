# Usage: lang_diff.py <old en_us.json> <new en_us.json>
import json,sys,re
old=json.load(open(sys.argv[1])); new=json.load(open(sys.argv[2]))
def keys(d,pat): return {k for k in d if re.match(pat,k)}
for label,pat in [('fruits',r'item\.mineminenomi\.\w*_no_mi\w*$'),('entities',r'entity\.mineminenomi\.\w+$'),('abilities',r'ability\.mineminenomi\.\w+$'),('items (all)',r'item\.mineminenomi\.\w+$'),('challenges',r'challenge\.mineminenomi\.[\w.]+$')]:
    o=keys(old,pat); n=keys(new,pat)
    print(f"== {label}: old={len(o)} new={len(n)} added={len(n-o)} removed={len(o-n)}")
    if label in ('fruits','entities','challenges'):
        print('  added:',sorted(new[k] for k in n-o)[:80])
        print('  removed:',sorted(old[k] for k in o-n)[:40])
