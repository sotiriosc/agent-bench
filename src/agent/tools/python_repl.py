def run(code: str) -> str:
    local_vars = {}
    try:
        exec(code, {"__builtins__": {}}, local_vars)
        return str(local_vars)
    except Exception as e:
        return f"ERROR: {e}"
