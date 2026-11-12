# list the lines gcov knows outside elaboration code, per rtl/core file, as JSON
import glob
import json
import os
import subprocess
import sys

d = sys.argv[1]
res = {}
for g in sorted(glob.glob(d + '/*.gcda')):
    o = subprocess.run(['gcov', '--json-format', '--stdout', '-o', d, g], capture_output=True, text=True)
    for doc in o.stdout.splitlines():
        if not doc.strip():
            continue
        for f in json.loads(doc)['files']:
            if 'rtl/core/' in f['file']:
                s = res.setdefault(os.path.basename(f['file']), set())
                s.update(e['line_number'] for e in f['lines'])
json.dump({k: sorted(v) for k, v in res.items()}, open(sys.argv[2], 'w'))
print(sum(len(v) for v in res.values()), 'lines in', len(res), 'files')
