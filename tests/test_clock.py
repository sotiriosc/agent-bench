import os, re, subprocess, sys, shlex

PY_EXE = shlex.quote(sys.executable)

def run_cli(msg, use_tools=True, timeout=10):
    env = os.environ.copy()
    env.pop("AGENT_DEBUG", None)  # keep output clean
    args = '--use-tools ' if use_tools else ''
    cmd = f'{PY_EXE} -m src.ui.cli {args}{shlex.quote(msg)}'
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env, timeout=timeout)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def test_clock_default_brackets():
    code, out, err = run_cli("[[time]]")
    assert code == 0, err
    assert err == ""
    # default like: 2025-08-24 17:55:21
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", out)

def test_clock_strftime_date_only():
    code, out, err = run_cli("time(%Y-%m-%d)")
    assert code == 0, err
    assert err == ""
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", out)

def test_clock_json_time_only():
    code, out, err = run_cli('{"tool":"clock","args":{"format":"%H:%M"}}')
    assert code == 0, err
    assert err == ""
    assert re.fullmatch(r"\d{2}:\d{2}", out)

