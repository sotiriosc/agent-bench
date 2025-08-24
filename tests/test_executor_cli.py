# tests/test_executor_cli.py
import os, subprocess, sys, shlex

PY_EXE = shlex.quote(sys.executable)

def run_cli(msg, use_tools=True, timeout=10):
    # Keep output deterministic in CI
    env = os.environ.copy()
    env.pop("AGENT_DEBUG", None)  # silence debug logs if you used them
    # If your CLI reads model or API configs from env, consider setting harmless defaults here

    args = f'--use-tools ' if use_tools else ''
    cmd = f'{PY_EXE} -m src.ui.cli {args}{shlex.quote(msg)}'
    p = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, env=env, timeout=timeout
    )
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def test_cli_tool_plain_expr():
    code, out, err = run_cli("23*17+88")
    assert code == 0, err
    assert err == ""
    assert out.endswith("479")

def test_cli_tool_json():
    code, out, err = run_cli('{"tool":"calculator","args":{"expression":"6*7"}}')
    assert code == 0, err
    assert err == ""
    assert out.endswith("42")

def test_cli_tool_trigger_format():
    code, out, err = run_cli("[[calc: 12/3 + 7*4 - 2]]")
    assert code == 0, err
    assert err == ""
    assert out.endswith("30")

def test_cli_plain_chat_no_tools():
    code, out, err = run_cli("Give me one sentence about this project.", use_tools=False)
    assert code == 0, err
    assert err == ""
    assert len(out) > 0

def test_cli_router_fallback_when_tools_enabled():
    # Proves run_tools() falls back to normal run() when no tool matches
    code, out, err = run_cli("Tell me what this project does in one short sentence.", use_tools=True)
    assert code == 0, err
    assert err == ""
    assert len(out) > 0
    # (Optional) Assert it's not just a number; i.e., we didn't accidentally hit calculator
    assert not out.isdigit()

