#!/usr/bin/env bash
# Independent check of the coverage figures. Runs the whole suite twice: once normally, and
# once on a copy of the RTL with a probe in front of each statement, then scores gcov
# against what the simulator itself reported. The checkout is not changed.
#
#   eval "$(regress/tools.sh env)"; regress/cover/oracle.sh [WORK_DIR]
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
WORK="${1:-$HOME/.cache/neorv32-regress/oracle}"
rm -rf "$WORK"
mkdir -p "$WORK/copy"

python3 "$REPO/regress/run.py" --build "$WORK/base" --report "$WORK/base-report"

python3 "$REPO/regress/cover/exec_lines.py" "$WORK/base/fixed" "$WORK/exec_lines.json"
for d in rtl sim sw regress; do
  cp -r "$REPO/$d" "$WORK/copy/"
done
python3 "$REPO/regress/cover/oracle_insert.py" "$WORK/exec_lines.json" "$WORK/copy/rtl/core"

# Signals must not change. The simulator output does, by the elaboration-time probes, so a
# nonzero exit here is expected: the failure list is checked below instead.
(cd "$WORK/copy" && python3 regress/run.py --build "$WORK/probe" --report "$WORK/probe-report") \
  > "$WORK/probe.log" 2>&1 || true
if grep -a -E '^ +signal |run length changed' "$WORK/probe.log"; then
  echo "ERROR: the probes changed a signal, so this comparison proves nothing" >&2
  exit 1
fi

cat "$WORK"/probe/run/*/hits.txt > "$WORK/all_hits.txt" || true
grep -a -h -o '@@HIT [^ ]*' "$WORK"/probe/run/*/stdout.txt >> "$WORK/all_hits.txt" || true
sed 's/^@@HIT //' "$WORK/all_hits.txt" | sort -u > "$WORK/copy/hits.txt"

grep -a -h -o '@@GEN [^ ]*' "$WORK"/probe/run/*/stdout.txt | sed 's/^@@GEN //' | sort -u > "$WORK/copy/gens.txt" || true

python3 "$REPO/regress/cover/score.py" "$WORK/base" "$WORK/base/fixed" "$WORK/copy"
