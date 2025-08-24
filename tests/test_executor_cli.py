import subprocess, sys, shlex

PY_EXE = sys.executable

def run_cli(msg, use_tools=True):
    cmd = f'{shlex.quote(PY_EXE)} -m src.ui.cli {"--use-tools " if use_tools else ""}{shlex.quote(msg)}'
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def test_cli_plain_expr():
    code, out, err = run_cli("23*17+88")
    assert code == 0
    assert out.endswith("479")

def test_cli_natural_language():
    code, out, err = run_cli("What is 23*17 + 88?")
    assert code == 0 and out.endswith("479")

def test_cli_triggers_all():
    for msg in ("[[calc: 23*17+88]]", "calc(23*17+88)", "CALCULATE: 23*17+88"):
        code, out, err = run_cli(msg)
        assert code == 0 and out.endswith("479")

def test_cli_no_tools_fallback():
    code, out, err = run_cli("Give me one sentence about this project.", use_tools=False)
    assert code == 0
    assert "agent benchmark framework" in out
