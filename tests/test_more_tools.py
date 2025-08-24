import subprocess, sys, shlex, re
PY_EXE = shlex.quote(sys.executable)

def run_cli(msg, use_tools=True):
    cmd = f'{PY_EXE} -m src.ui.cli {"--use-tools " if use_tools else ""}{shlex.quote(msg)}'
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def test_weather_trigger():
    code, out, err = run_cli("[[weather: Toronto]]")
    assert code == 0 and "Toronto" in out

def test_weather_json():
    code, out, err = run_cli('{"tool":"weather","args":{"city":"Athens"}}')
    assert code == 0 and "Athens" in out

def test_uuid_trigger():
    code, out, err = run_cli("[[uuid]]")
    assert code == 0 and re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", out, re.I)

def test_echo_trigger():
    code, out, err = run_cli("[[echo: hello YOU]]")
    assert code == 0 and out == "hello YOU"

def test_echo_json():
    code, out, err = run_cli('{"tool":"echo","args":{"text":"stay aligned"}}')
    assert code == 0 and out == "stay aligned"
