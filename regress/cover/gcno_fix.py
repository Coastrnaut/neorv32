#!/usr/bin/env python3
"""Remove misleading line entries from a GCC 13 .gcno file written by ghdl-gcc.

GHDL emits a source location only at the start of a statement, and GCC tags blocks from
those locations. Raw gcov therefore reports statements that never ran as hit:

  1. Function entry code carries the final statement of the PREVIOUS function. The
     function records that same line as its start_line.
  2. Code after a statement carries that statement's line, for example the increment
     and exit test of a for loop carry the last statement of the loop body.
  3. An empty jump block carries a stale line as well, apparently from its destination
     label. So the jump of "next when c;" or "exit when c;" carries the last statement
     of the loop body even though it skips that statement.

Case arms also start with a label that carries the previous arm's last line. That is
case 2 again.

For each function, a line is kept only on the first block that really starts it. An
entry is dropped when it is on the function's start_line, when an earlier block already
has the line, or when the block is an empty jump. A jump carries only that line and has
one successor, which is not the next block. It is empty if its successor carries the
line too, or if the next block carries the line and is the other arm of the same branch.
That last condition matters: the final block of a multi-block case arm looks like a jump,
and the next arm's label carries its line, but those two are not arms of one branch.

Keep "an earlier block already has the line". A function returning a string has one
shared cleanup block, which carries the line of the FIRST return and runs for every
return, so looser rules claim that line as hit. The price is one known under-report:
the arms of a long conditional assignment all carry its first line, so that line reads
as not hit if the first arm never ran. That is safe, because a real gap sits on the next
lines in that case, and it is the only false miss seen.

Entries are removed per function, so a real hit from another function's block is never
lost. gcov still does all the counting. Checksums and stamps are left alone, so the
.gcda still matches.

usage: gcno_fix.py [--no-elab] IN.gcno OUT.gcno
  --no-elab  also drop every line of the *_ELAB functions (elaboration-time code)
"""
import collections
import struct
import sys

TAG_FUNCTION = 0x01000000
TAG_ARCS = 0x01430000
TAG_LINES = 0x01450000
ARC_FAKE = 2
MAGIC = 0x67636e6f  # 'gcno'
VERSION = 0x4233332a  # 'B33*', GCC 13.3


class Reader:
    def __init__(self, data, pos=0):
        self.data, self.pos = data, pos

    def u32(self):
        value = struct.unpack_from('<I', self.data, self.pos)[0]
        self.pos += 4
        return value

    def string(self):
        size = self.u32()  # in bytes, includes the NUL, no padding (GCC 13)
        if size == 0:
            return None
        text = self.data[self.pos:self.pos + size]
        self.pos += size
        return text.rstrip(b'\0')


def write_string(text):
    if text is None:
        return struct.pack('<I', 0)
    raw = text + b'\0'
    return struct.pack('<I', len(raw)) + raw


def parse_lines(data, base, size):
    """Return (block, [(file, line), ...]) for one LINES record."""
    q = Reader(data, base)
    block = q.u32()
    entries, current = [], None
    while True:
        line = q.u32()
        if line:
            entries.append((current, line))
            continue
        name = q.string()
        if name is None:
            break
        current = name
    if q.pos != base + size:
        raise SystemExit('LINES record does not end where its length says')
    return block, entries


def build_lines(block, entries):
    body = bytearray(struct.pack('<I', block))
    current = None
    for name, line in entries:
        if name != current:
            body += struct.pack('<I', 0) + write_string(name)
            current = name
        body += struct.pack('<I', line)
    body += struct.pack('<I', 0) + write_string(None)
    return body


def keep_entries(func):
    """Decide which line entries of one function survive."""
    lines, successors = func['lines'], func['successors']
    tagged = collections.defaultdict(set)
    for block, entries in lines.items():
        for key in entries:
            tagged[key].add(block)
    preds = collections.defaultdict(set)
    for block, out in successors.items():
        for dest in out:
            preds[dest].add(block)
    seen, kept = set(), {}
    for block in sorted(lines):
        out = successors.get(block, [])
        jump = len(out) == 1 and out[0] != block + 1 and len(lines[block]) == 1
        sibling = jump and bool(preds[block] & preds[block + 1])
        kept[block] = []
        for key in lines[block]:
            if func['elab'] or key in seen:
                continue
            if key == (func['source'], func['start_line']):
                continue
            if jump and (out[0] in tagged[key] or (sibling and block + 1 in tagged[key])):
                continue
            seen.add(key)
            kept[block].append(key)
    return kept


def fix(data, drop_elab=False):
    r = Reader(data)
    if r.u32() != MAGIC or r.u32() != VERSION:
        raise SystemExit('not a GCC 13.3 .gcno file')
    r.u32()      # stamp
    r.u32()      # checksum
    r.string()   # compile directory
    r.u32()      # supports unexecuted blocks
    header = data[:r.pos]

    records, funcs, func = [], [], None
    while r.pos < len(data):  # GCC 13 writes no end tag
        tag = r.u32()
        size = r.u32()
        base = r.pos
        rec = {'tag': tag, 'raw': data[base - 8:base + size], 'func': func}
        if tag == TAG_FUNCTION:
            f = Reader(data, base)
            f.u32()
            f.u32()
            f.u32()  # ident and checksums
            name = f.string()
            f.u32()  # artificial
            source = f.string()
            func = {'source': source, 'start_line': f.u32(), 'lines': {}, 'successors': {},
                    'elab': drop_elab and name.endswith(b'_ELAB')}
            funcs.append(func)
            rec['func'] = func
        elif tag == TAG_ARCS:
            a = Reader(data, base)
            block = a.u32()
            while a.pos < base + size:
                dest, flags = a.u32(), a.u32()
                if not flags & ARC_FAKE:
                    func['successors'].setdefault(block, []).append(dest)
        elif tag == TAG_LINES:
            block, entries = parse_lines(data, base, size)
            func['lines'].setdefault(block, []).extend(entries)
            rec['block'] = block
        records.append(rec)
        r.pos = base + size

    for func in funcs:
        func['kept'] = keep_entries(func)

    out, dropped = bytearray(header), 0
    for rec in records:
        if rec['tag'] != TAG_LINES:
            out += rec['raw']
            continue
        func, block = rec['func'], rec['block']
        dropped += len(func['lines'][block]) - len(func['kept'][block])
        body = build_lines(block, func['kept'][block])
        out += struct.pack('<II', rec['tag'], len(body)) + body
    return out, dropped


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--no-elab']
    result, count = fix(open(args[0], 'rb').read(), '--no-elab' in sys.argv)
    open(args[1], 'wb').write(result)
    print(f'{args[0]}: dropped {count} line entries')
