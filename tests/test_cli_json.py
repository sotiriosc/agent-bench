import subprocess, sys, shlex, json
PY_EXE = shlex.quote(sys.executable)

def run(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def test_json_tools_calc():
    code, out, err = run(f'{PY_EXE} -m src.ui.cli --use-tools --json "2+2"')
    assert code == 0
    data = json.loads(out)
    assert data["mode"] == "tools" and data["tool"] == "calculator" and data["text"] == "4"

def test_json_tool_only_no_match():
    code, out, err = run(f'{PY_EXE} -m src.ui.cli --use-tools --tool-only --json "no tool here"')
    assert code == 2
    data = json.loads(out)
    assert data["mode"] == "tools" and data["tool"] is None and data["rc"] == 2
