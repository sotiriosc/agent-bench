#!/usr/bin/env python3
import os, sys, shlex, subprocess, re

DATA = [
    {"msg": "23*17+88", "expect": "479"},
    {"msg": '{"tool":"calculator","args":{"expression":"6*7"}}', "expect": "42"},
    {"msg": "[[time]]", "match": r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}"},
    {"msg": "time(%Y-%m-%d)", "match": r"\d{4}-\d{2}-\d{2}"},
    {"msg": '{"tool":"clock","args":{"format":"%H:%M"}}', "match": r"\d{2}:\d{2}"},
    {"msg": "[[upper: hello world]]", "expect": "HELLO WORLD"},
    {"msg": "slug: Hello World!!", "expect": "hello-world"},
    {"msg": '{"tool":"stringy","args":{"op":"title","text":"from chaos, order"}}', "expect": "From Chaos, Order"},
    {"msg": "[[weather: Toronto]]", "contains": "Toronto"},
    {"msg": '{"tool":"uuid"}', "match": r"[0-9a-fA-F-]{36}"},
    {"msg": "[[echo: ping]]", "expect": "ping"},
]

def run(msg: str):
    py = shlex.quote(sys.executable)
    # Force tool path; fail if no tool matched; suppress debug
    cmd = f'{py} -m src.ui.cli --use-tools --tool-only --quiet {shlex.quote(msg)}'
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def main() -> int:
    ok = 0
    for i, case in enumerate(DATA, 1):
        code, out, err = run(case["msg"])
        passed = (code == 0 and not err)
        if "expect" in case:
            passed = passed and (out == case["expect"])
        if "contains" in case:
            passed = passed and (case["contains"] in out)
        if "match" in case:
            passed = passed and bool(re.fullmatch(case["match"], out))
        print(f"[{i:02d}] {'PASS' if passed else 'FAIL'} | {case['msg']} -> {out}")
        ok += int(passed)
    total = len(DATA)
    print(f"\nAccuracy: {ok}/{total}")
    return 0 if ok == total else 1

if __name__ == "__main__":
    raise SystemExit(main())
