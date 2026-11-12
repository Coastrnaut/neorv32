#!/usr/bin/env python3
"""Prove that the regression reports behaviour changes.

Each mutation below is one small RTL edit. It is applied to a private copy of the repository,
never to the checkout, and the relevant tests run against the committed baselines. A mutation
counts as caught when the run fails and names a test. The last two entries only edit comments
and must NOT be flagged.

usage: regress/cover/mutate.py [--work DIR] [--only TEXT]
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

NOSOC = r'^(?!soc)'
SHORT = r'^soc_(min|e|rvc|large)$'
CHECK = r'^soc_processor_check$'

# name, file, old text, new text, tests to run, expected result
MUTATIONS = [
    ('uart: one bit less per frame', 'neorv32_uart.vhd', 'tx.bitcnt  <= "1010";', 'tx.bitcnt  <= "1001";', NOSOC, 'fail'),
    ('gpio: rising edge is falling edge', 'neorv32_gpio.vhd',
     'when "11"   => irq_trig(i) <= port_in(i) and (not port_in2(i));',
     'when "11"   => irq_trig(i) <= (not port_in(i)) and port_in2(i);', NOSOC, 'fail'),
    ('wdt: wrong reset cause', 'neorv32_wdt.vhd', 'reset_cause <= "10";', 'reset_cause <= "11";', NOSOC, 'fail'),
    ('pwm: polarity ignored', 'neorv32_pwm.vhd', 'pol_i   => polarity(i),', "pol_i   => '0',", NOSOC, 'fail'),
    ('dma: byte swap inverted', 'neorv32_dma.vhd', "if (engine.bswap = '0') then", "if (engine.bswap = '1') then", NOSOC, 'fail'),
    ('fifo: never full flag', 'neorv32_prim.vhd', 'free_o  <= not full;', "free_o  <= '1';", NOSOC, 'fail'),
    ('muldiv: high word shifted', 'neorv32_cpu_alu_muldiv.vhd', 'res_o <= mul_res(63 downto 32);', 'res_o <= mul_res(62 downto 31);', NOSOC, 'fail'),
    ('shifter: arithmetic is logical', 'neorv32_cpu_alu_shifter.vhd',
     'sgn    <= rs1_i(31) and ctrl_i.ir_funct12(10);', "sgn    <= '0';", NOSOC, 'fail'),
    ('fpu: multiplier underflow flag lost', 'neorv32_cpu_alu_fpu.vhd',
     "multiplier.flags(fp_exc_uf_c) <= '1';", "multiplier.flags(fp_exc_uf_c) <= '0';", NOSOC, 'fail'),
    ('crypto: sha256 rotate amount', 'neorv32_cpu_alu_crypto.vhd', 'ror_f(rs1,  7)', 'ror_f(rs1,  8)', NOSOC, 'fail'),
    ('pmp: lock bit inverted', 'neorv32_cpu_pmp.vhd', "(pmpcfg(i)(cfg_l_c) = '0') then -- unlocked write access",
     "(pmpcfg(i)(cfg_l_c) = '1') then -- unlocked write access", NOSOC, 'fail'),
    ('cache: never hits', 'neorv32_cache.vhd', "hit <= '1' when", "hit <= '0' when", NOSOC, 'fail'),
    ('control: mepc keeps its value on a trap', 'neorv32_cpu_control.vhd',
     "csr.mepc         <= epc(31 downto 1) & '0';", 'csr.mepc         <= csr.mepc;', SHORT, 'fail'),
    ('control: mepc write ignores bit 2', 'neorv32_cpu_control.vhd',
     "csr.mepc <= csr_wdata(31 downto 1) & '0';", "csr.mepc <= csr_wdata(31 downto 3) & \"000\";", CHECK, 'fail'),
    ('comment only, must not be flagged', 'neorv32_gpio.vhd', '-- input sampling --', '-- input sampling, reworded --', NOSOC, 'pass'),
    ('new comment line, must not be flagged', 'neorv32_cpu_alu.vhd', '  -- ALU Core ---',
     '  -- moves all later lines down\n  -- ALU Core ---', NOSOC, 'pass'),
]


def run(cmd, cwd, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, errors='replace')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', default=os.path.expanduser('~/.cache/neorv32-regress/mutate'))
    ap.add_argument('--only', help='run only mutations whose name contains this text')
    args = ap.parse_args()

    copy = os.path.join(args.work, 'repo')
    shutil.rmtree(copy, ignore_errors=True)
    os.makedirs(copy)
    for name in ('rtl', 'sim', 'sw', 'regress'):
        shutil.copytree(os.path.join(ROOT, name), os.path.join(copy, name))

    rows = []
    for name, fname, old, new, pattern, expect in MUTATIONS:
        if args.only and args.only not in name:
            continue
        path = os.path.join(copy, 'rtl', 'core', fname)
        original = open(path, encoding='latin-1', newline='').read()
        if old not in original:
            rows.append((name, 'NOT APPLIED', 'text not found'))
            print(f'{name}: NOT APPLIED, text not found', flush=True)
            continue
        with open(path, 'w', encoding='latin-1', newline='') as f:
            f.write(original.replace(old, new, 1))
        r = run([sys.executable, 'regress/run.py', '--filter', pattern, '--build', os.path.join(args.work, 'build')], copy)
        with open(path, 'w', encoding='latin-1', newline='') as f:
            f.write(original)
        lines = [x for x in r.stdout.splitlines() if x.startswith('FAIL') or x.startswith('    ')]
        built = 'built ' in r.stdout
        got = 'fail' if r.returncode else 'pass'
        if not built:
            verdict = 'NOT RUN: build failed'
        elif got == expect:
            verdict = 'caught' if expect == 'fail' else 'not flagged, as expected'
        else:
            verdict = 'MISSED' if expect == 'fail' else 'FALSE ALARM'
        first = lines[:4]
        rows.append((name, verdict, ' / '.join(x.strip() for x in first)))
        print(f'{name}: {verdict}', flush=True)
        for x in first:
            print(f'    {x.strip()}', flush=True)

    caught = sum(1 for r in rows if r[1] == 'caught')
    wanted = sum(1 for m in MUTATIONS if m[5] == 'fail' and (not args.only or args.only in m[0]))
    print(f'\ncaught {caught} of {wanted} behaviour mutations')
    for r in rows:
        if r[1] not in ('caught', 'not flagged, as expected'):
            print(f'PROBLEM {r[0]}: {r[1]} {r[2]}')
    return 0 if all(r[1] in ('caught', 'not flagged, as expected') for r in rows) else 1


if __name__ == '__main__':
    sys.exit(main())
