# Ground truth for coverage. In a COPY of the RTL, put a probe in front of each statement that
# gcov lists, on the same line, so line numbers do not change. Running that copy records which
# statements really ran, with no assumptions about GCC. A probe writes "@@HIT file:line" to
# hits.txt the first time it runs, so that a whole suite stays fast.
#   sequential statement   hit_p(id, "@@HIT file:line"); <statement>
#   when x => statement    when x => hit_p(...); <statement>
#   elsif (cond) then      elsif hit_f(id, "@@HIT file:line") and (cond) then
#   concurrent assignment  assert false report "@@HIT file:line" severity note; <statement>
# A concurrent assert runs once if its generate branch is elaborated. Every concurrent
# assignment also runs once at start-up, so the two have the same meaning.
# neorv32_package.vhd gets no probes: its functions size ports, so they have to stay pure.
# usage: oracle_insert.py EXEC_LINES.json SRC_DIR
import collections
import json
import os
import re
import sys

exec_lines = json.load(open(sys.argv[1]))  # {"neorv32_x.vhd": [line, ...]}
src_dir = sys.argv[2]

NOT_START = re.compile(r'^\s*(when|elsif|else|end|begin|\(|\)|or\b|and\b|xor\b|not\b|&)', re.I)
ENDS_STMT = re.compile(r'(;|\bthen|\belse|\bbegin|\bloop|=>|\bis|\bgenerate)$', re.I)
OPEN_SUB = re.compile(r'^\s*(pure\s+|impure\s+)?(function|procedure)\b', re.I)
DECL = ('function', 'procedure', 'variable', 'constant', 'type', 'signal', 'attribute')
INLINE_WHEN = re.compile(r'^(\s*when\b.*?=>\s*)(\S.*)$', re.I)
ELSIF = re.compile(r'^(\s*elsif\s+)(.*?)(\s+then\b.*)$', re.I)

done = collections.Counter()
next_id = 0
for name, wanted in sorted(exec_lines.items()):
    path = os.path.join(src_dir, name)
    if name == 'neorv32_package.vhd' or not os.path.exists(path):
        continue
    lines = open(path, encoding='latin-1').read().split('\n')
    wanted = set(wanted)
    depth = []        # stack of 'decl' or 'body'
    pending = False   # inside a subprogram header, looking for "is" or ";"
    prev = ''
    for i, raw in enumerate(lines):
        n = i + 1
        code = re.sub(r'--.*$', '', raw).strip()
        low = code.lower()
        if not code:
            continue
        tag = f'@@HIT {name}:{n}'
        next_id += 1
        report = f'hit_p({next_id}, "{tag}"); '
        in_body = bool(depth) and depth[-1] == 'body'
        if n in wanted and ENDS_STMT.search(prev):
            indent = raw[:len(raw) - len(raw.lstrip())]
            if in_body and not NOT_START.match(code) and not low.startswith(DECL):
                lines[i] = indent + report + raw.lstrip()
                done['sequential'] += 1
            elif in_body and low.startswith('when') and not code.endswith('=>'):
                m = INLINE_WHEN.match(raw)
                if m:
                    lines[i] = m.group(1) + report + m.group(2)
                    done['inline when'] += 1
            elif in_body and low.startswith('elsif'):
                m = ELSIF.match(raw)
                if m:
                    lines[i] = f'{m.group(1)}hit_f({next_id}, "{tag}") and ({m.group(2)}){m.group(3)}'
                    done['elsif'] += 1
            elif not depth and '<=' in code and not low.startswith(DECL):
                lines[i] = f'{indent}assert false report "{tag}" severity note; {raw.lstrip()}'
                done['concurrent'] += 1
        if re.match(r'^end\s+(process|function|procedure)\b', low) or (low == 'end;' and depth):
            if depth:
                depth.pop()
        elif re.search(r'\bprocess\b', low) and not low.startswith('end'):
            depth.append('decl')
        elif OPEN_SUB.match(code) or pending:
            if re.search(r'\bis\s*$', low):
                depth.append('decl')
                pending = False
            elif code.endswith(';'):
                pending = False
            else:
                pending = True
        elif low == 'begin' and depth and depth[-1] == 'decl':
            depth[-1] = 'body'
        prev = code
    # a generate branch holding only an instantiation has no gcov line of its own, so report it
    for i, raw in enumerate(lines):
        code = re.sub(r'--.*$', '', raw).rstrip()
        if re.search(r'\bgenerate$', code, re.I) and not re.match(r'^\s*end\b', code, re.I):
            rest = next((re.sub(r'--.*$', '', x).strip().lower() for x in lines[i + 1:]
                         if re.sub(r'--.*$', '', x).strip()), '')
            if not re.match(r'^(signal|constant|type|subtype|component|attribute|shared|file|function|procedure|begin)\b', rest):
                lines[i] = f'{code} assert false report "@@GEN {name}:{i + 1}" severity note;'
                done['generate'] += 1
    # the import goes on an existing line, and local functions may now write to the hit table
    for i, raw in enumerate(lines):
        if re.match(r'^\s*entity\s+\w+\s+is\b', raw, re.I):
            lines[i] = 'library neorv32; use neorv32.neorv32_package.all; ' + raw
        elif name != 'neorv32_package.vhd' and re.match(r'^\s*(pure\s+)?function\b', raw, re.I):
            lines[i] = re.sub(r'^(\s*)(pure\s+)?function', r'\1impure function', raw, flags=re.I)
    open(path, 'w', encoding='latin-1').write('\n'.join(lines))

# the helpers go into the package, on existing lines
path = os.path.join(src_dir, 'neorv32_package.vhd')
lines = open(path, encoding='latin-1').read().split('\n')
for i, raw in enumerate(lines):
    if raw.strip().lower() == 'package neorv32_package is':
        lines[i] = raw + (' impure function hit_f(i : natural; s : string) return boolean;'
                          ' procedure hit_p(i : natural; s : string);')
    elif raw.strip().lower() == 'package body neorv32_package is':
        lines[i] = raw + (' type hit_t is protected procedure mark(i : natural; s : string); end protected;'
                          ' type hit_t is protected body'
                          ' file f : std.textio.text open write_mode is "hits.txt";'
                          ' variable seen : bit_vector(0 to 20000) := (others => \'0\');'
                          ' procedure mark(i : natural; s : string) is variable l : std.textio.line; begin'
                          ' if seen(i) = \'0\' then seen(i) := \'1\'; std.textio.write(l, s);'
                          ' std.textio.writeline(f, l); end if; end procedure;'
                          ' end protected body;'
                          ' shared variable hits : hit_t;'
                          ' procedure hit_p(i : natural; s : string) is begin hits.mark(i, s); end procedure;'
                          ' impure function hit_f(i : natural; s : string) return boolean is begin'
                          ' hits.mark(i, s); return true; end function;')
open(path, 'w', encoding='latin-1').write('\n'.join(lines))
print('probes inserted:', dict(done), 'total', sum(done.values()))
