import re, os, subprocess, sys, shlex, json

PY = shlex.quote(sys.executable)

def run_cli(msg, chain=1):
    cmd = f'{PY} -m src.ui.cli --use-tools --chain {chain} {shlex.quote(msg)}'
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def test_autodiscover_basic():
    # Expect existing tools to be discovered (stringy)
    c, o, e = run_cli("slug: Auto Discover!!")
    assert c == 0 and e == ""
    assert o == "auto-discover"

def test_autodiscover_json():
    c, o, e = run_cli('{"tool":"stringy","args":{"op":"upper","text":"auto"}}')
    assert c == 0 and e == ""
    assert o == "AUTO"

def test_chain_echo_to_upper():
    # First echo returns a string that is itself an upper trigger
    c, o, e = run_cli('[[echo: [[upper: hi]] ]]', chain=3)
    assert c == 0 and e == ""
    assert o == "HI"
