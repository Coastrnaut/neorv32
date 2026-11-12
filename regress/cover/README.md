# Line coverage and proof of detection

This folder is optional. If it exists, `regress/run.py` also measures which RTL lines the tests ran, and a
full run fails if a line is neither run nor waived.

## How coverage is measured

GHDL's GCC backend counts executed lines and `gcov` reports them. Do not trust raw `gcov` on this design:
it marks statements as run that never ran, and it counts elaboration code. `gcno_fix.py` removes those
entries before `gcov` reads them. It refuses any `.gcno` format except the one it was proven on.

Two checks guard the correction:

- **`canary_tb.vhd`** runs with every regression. Each of its `-- UNREACHED` lines must read 0 and each
  `-- REACHED` line must read above 0, or the run fails.
- **`oracle.sh`** is run by hand after a change to these tools or to the GHDL version. It puts a probe in
  front of each statement of a copy of the RTL, so the simulator itself reports what ran, and compares
  that with `gcov`. It also reports generate branches that no test elaborated.

## Waivers

A line that cannot be reached goes in `waivers.txt` as `file | occurrence | source text | reason`.
Occurrence numbers the identical lines of that file. A waiver matches the source text, so moving a line
keeps its waiver and changing the line does not. A waiver that matches nothing fails the run. The report
file `waiver_candidates.txt` lists unreached lines in this format.

## Proof that changes are detected

`mutate.py` applies small RTL edits to a private copy of the repository, one at a time, and checks that the
regression reports each one. It also applies comment-only edits, which must not be reported.

```bash
eval "$(bash regress/tools.sh env)"
python3 regress/cover/mutate.py
bash regress/cover/oracle.sh
```
