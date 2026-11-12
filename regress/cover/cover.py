"""Line coverage for regress/run.py. Optional: run.py uses it when this folder exists.

GHDL's GCC backend counts executed lines, gcno_fix.py corrects the line table, and gcov
reports. See README.md in this folder.
"""
import collections
import glob
import json
import multiprocessing
import os
import shutil
import subprocess

import gcno_fix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
WAIVERS = os.path.join(HERE, 'waivers.txt')
ANALYSE_FLAGS = ['-fprofile-arcs', '-ftest-coverage']
ELAB_FLAGS = ['-Wc,-fprofile-arcs', '-Wc,-ftest-coverage', '-Wc,-Wno-coverage-invalid-line-number',
              '-Wl,-lgcov']
COVER_GLOBS = ['rtl/core/*.vhd', 'rtl/system_integration/*.vhd', 'rtl/test_setups/*.vhd']
COVER_SKIP = {'neorv32_imem_image.vhd', 'neorv32_bootrom_image.vhd'}  # generated data
CANARY = {'name': 'canary', 'tb': 'canary_tb', 'args': [], 'stop': '1ms', 'prog': None, 'pflags': '',
          'march': None, 'mabi': None, 'expect': None, 'source': 'regress/cover/canary_tb.vhd'}


def gcov_unit(job):
    gcda, fixed = job
    unit = os.path.splitext(os.path.basename(gcda))[0]
    gcno, _ = gcno_fix.fix(open(gcda[:-5] + '.gcno', 'rb').read(), True)
    with open(os.path.join(fixed, unit + '.gcno'), 'wb') as f:
        f.write(gcno)
    shutil.copy(gcda, fixed)
    r = subprocess.run(['gcov', '--json-format', '--stdout', '-o', fixed, os.path.join(fixed, unit + '.gcda')],
                       capture_output=True, text=True, cwd=fixed)
    hits = {}
    for doc in r.stdout.splitlines():
        if doc.strip():
            for f in json.loads(doc)['files']:
                name = f['file'].replace('\\', '/')
                table = hits.setdefault(name, {})
                for e in f['lines']:
                    table[e['line_number']] = table.get(e['line_number'], 0) + e['count']
    return hits


def load_waivers():
    """file | occurrence | source text | reason. Occurrence counts identical lines of that file."""
    waivers = {}
    if os.path.exists(WAIVERS):
        for n, line in enumerate(open(WAIVERS, encoding='utf-8'), 1):
            line = line.rstrip('\n')
            if not line.strip() or line.startswith('#'):
                continue
            parts = line.split(' | ')
            if len(parts) != 4 or not parts[3].strip():
                raise SystemExit(f'{WAIVERS}:{n}: expected "file | occurrence | source text | reason"')
            waivers[(parts[0].strip(), int(parts[1]), parts[2].strip())] = parts[3].strip()
    return waivers


def coverage(build, jobs):
    fixed = os.path.join(build, 'fixed')
    shutil.rmtree(fixed, ignore_errors=True)
    os.makedirs(fixed)
    units = [g for g in glob.glob(os.path.join(build, '*.gcda'))
             if not os.path.basename(g).startswith(('tb_', 'e~'))]
    with multiprocessing.Pool(jobs) as pool:
        tables = pool.map(gcov_unit, [(g, fixed) for g in units])
    merged = {}
    for table in tables:
        for path, lines in table.items():
            dst = merged.setdefault(os.path.basename(path), {})
            for n, c in lines.items():
                dst[n] = dst.get(n, 0) + c
    return merged


def canary_check(merged):
    path = os.path.join(HERE, 'canary_tb.vhd')
    lines = merged.get('canary_tb.vhd', {})
    bad = []
    for n, text in enumerate(open(path), 1):
        if '-- UNREACHED' in text and lines.get(n, 0) != 0:
            bad.append(f'canary_tb.vhd:{n} reads {lines[n]} but never runs')
        if '-- REACHED' in text and lines.get(n, 0) == 0:
            bad.append(f'canary_tb.vhd:{n} reads 0 but does run')
    return bad


def coverage_report(merged, report):
    waivers = load_waivers()
    used, rows, uncovered, missed = set(), [], [], []
    for pattern in COVER_GLOBS:
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            name = os.path.basename(path)
            if name in COVER_SKIP:
                continue
            table = merged.get(name)
            src = open(path, encoding='latin-1').read().split('\n')
            if table is None:
                rows.append((name, 0, 0, 0))
                uncovered.append(f'{name}: never compiled into any test')
                continue
            hit = waived = 0
            seen = collections.Counter()
            occurrence = {}
            for i, text in enumerate(src, 1):
                seen[text.strip()] += 1
                occurrence[i] = seen[text.strip()]
            for n in sorted(table):
                if table[n] > 0:
                    hit += 1
                    continue
                text = src[n - 1].strip() if n <= len(src) else ''
                key = (name, occurrence.get(n, 0), text)
                if key in waivers:
                    used.add(key)
                    waived += 1
                else:
                    uncovered.append(f'{name}:{n}: {text}')
                    missed.append(f'{name} | {occurrence.get(n, 0)} | {text} | REASON')
            rows.append((name, len(table), hit, waived))
    stale = [f'{k[0]} | {k[1]} | {k[2]}' for k in waivers if k not in used]
    with open(os.path.join(report, 'waiver_candidates.txt'), 'w') as f:
        f.write('\n'.join(missed) + '\n')
    total = sum(r[1] for r in rows)
    hit = sum(r[2] for r in rows)
    waived = sum(r[3] for r in rows)
    out = [f'{"file":38} {"lines":>6} {"hit":>6} {"waived":>6} {"missed":>6} {"hit %":>6}']
    for name, lines, h, w in rows:
        pct = 100.0 * h / lines if lines else 0.0
        out.append(f'{name:38} {lines:6} {h:6} {w:6} {lines - h - w:6} {pct:6.1f}')
    pct = 100.0 * hit / total if total else 0.0
    out.append(f'{"TOTAL":38} {total:6} {hit:6} {waived:6} {total - hit - waived:6} {pct:6.2f}')
    with open(os.path.join(report, 'coverage.txt'), 'w') as f:
        f.write('\n'.join(out) + '\n')
    with open(os.path.join(report, 'uncovered.txt'), 'w') as f:
        f.write('\n'.join(uncovered) + '\n')
    return {'total': total, 'hit': hit, 'waived': waived, 'missed': total - hit - waived,
            'percent': round(pct, 2), 'stale': stale, 'uncovered': uncovered, 'table': out}
