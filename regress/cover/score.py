# Score raw gcov and the fixed .gcno against the oracle: what the simulator says really ran.
# usage: score.py RAW_DIR FIXED_DIR ORACLE_DIR
import glob
import json
import os
import re
import subprocess
import sys


def load(d):
    res = {}
    for g in sorted(glob.glob(d + '/*.gcda')):
        o = subprocess.run(['gcov', '--json-format', '--stdout', '-o', d, g], capture_output=True, text=True)
        for doc in o.stdout.splitlines():
            if not doc.strip():
                continue
            for f in json.loads(doc)['files']:
                if "rtl/core/" in f["file"]:
                    name = os.path.basename(f['file'])
                    for e in f['lines']:
                        key = (name, e['line_number'])
                        res[key] = res.get(key, 0) + e['count']
    return res


raw, fixed = load(sys.argv[1]), load(sys.argv[2])
oracle = sys.argv[3]
probed, source, kind = set(), {}, {}
for path in glob.glob(oracle + '/rtl/core/*.vhd'):
    name = os.path.basename(path)
    for n, text in enumerate(open(path, encoding='latin-1'), 1):
        if '@@HIT ' in text:
            key = (name, n)
            probed.add(key)
            source[key] = re.sub(r'(assert false report "@@HIT [^;]*; |hit_p\([^;]*; )', '', text).strip()
            kind[key] = ('elsif' if 'hit_f(' in text else
                         'concurrent' if 'assert false report' in text else
                         'inline when' if text.lstrip().lower().startswith('when') else
                         'sequential')
truth = set()
for text in open(oracle + '/hits.txt'):
    name, n = text.strip().rsplit(':', 1)
    truth.add((name, int(n)))
if not truth:
    raise SystemExit('oracle recorded no hits: its build or run failed, nothing can be scored')

print(f'statements probed: {len(probed)}, really ran: {len(truth & probed)}')
for label, data in (('raw gcov', raw), ('fixed', fixed)):
    hit = {k for k in probed if data.get(k, 0) > 0}
    false_hits = sorted(hit - truth)
    false_miss = sorted((probed - hit) & truth)
    print(f'{label:9}: says hit {len(hit)}, false hits {len(false_hits)}, false misses {len(false_miss)}')
    for group in ('sequential', 'inline when', 'elsif', 'concurrent'):
        keys = {k for k in probed if kind[k] == group}
        fh = len([k for k in false_hits if kind[k] == group])
        fm = len([k for k in false_miss if kind[k] == group])
        print(f'   {group:12} probed {len(keys):5}, ran {len(keys & truth):5}, false hits {fh:3}, false misses {fm:3}')
    if label == 'fixed':
        for title, group in (('FALSE HIT', false_hits), ('FALSE MISS', false_miss)):
            for k in group[:25]:
                print(f'  {title} {k[0]}:{k[1]}: {source[k][:78]}')

# generate branches that no test elaborated
wanted, seen = set(), set()
for path in glob.glob(oracle + '/rtl/core/*.vhd'):
    for text in open(path, encoding='latin-1'):
        wanted.update(re.findall(r'@@GEN (\S+?)"', text))
if os.path.exists(oracle + '/gens.txt'):
    seen = {x.strip() for x in open(oracle + '/gens.txt')}
missing = sorted(wanted - seen)
print(f'generate branches probed: {len(wanted)}, never elaborated: {len(missing)}')
for name in missing:
    print('  NOT ELABORATED', name)
