import subprocess, sys, shlex
PY_EXE = shlex.quote(sys.executable)

def run(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def test_tool_only_success():
    code, out, err = run(f'{PY_EXE} -m src.ui.cli --use-tools --tool-only "[[echo: hi]]"')
    assert code == 0 and out == "hi" and not err

def test_tool_only_failure():
    code, out, err = run(f'{PY_EXE} -m src.ui.cli --use-tools --tool-only "just chatting"')
    assert code == 2 and "No tool matched" in err

def test_quiet_suppresses_debug():
    env = "AGENT_DEBUG=1"
    code, out, err = run(f'{env} {PY_EXE} -m src.ui.cli --use-tools --quiet "[[calc: 2+2]]"')
    assert code == 0 and out == "4" and "[DEBUG" not in (out + err)
