import os, subprocess, sys, shlex

PY_EXE = shlex.quote(sys.executable)

def run_cli(msg, use_tools=True, timeout=10):
    env = os.environ.copy()
    env.pop("AGENT_DEBUG", None)
    args = '--use-tools ' if use_tools else ''
    cmd = f'{PY_EXE} -m src.ui.cli {args}{shlex.quote(msg)}'
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env, timeout=timeout)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def test_stringy_upper_bracket_trigger():
    code, out, err = run_cli("[[upper: hello world]]")
    assert code == 0, err
    assert err == ""
    assert out == "HELLO WORLD"

def test_stringy_slug_colon_trigger():
    code, out, err = run_cli("slug: Hello World!!")
    assert code == 0, err
    assert err == ""
    assert out == "hello-world"

def test_stringy_json_title():
    code, out, err = run_cli('{"tool":"stringy","args":{"op":"title","text":"from chaos, order"}}')
    assert code == 0, err
    assert err == ""
    assert out == "From Chaos, Order"

