import subprocess, sys, shlex
PY_EXE = shlex.quote(sys.executable)

def run(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def test_chain_two_passes():
    code, out, err = run(f'{PY_EXE} -m src.ui.cli --use-tools --chain 2 "echo: [[upper: hi]]"')
    assert code == 0 and out == "HI"

def test_chain_single_pass_default():
    code, out, err = run(f'{PY_EXE} -m src.ui.cli --use-tools "echo: [[upper: hi]]"')
    assert code == 0 and out == "[[upper: hi]]"
