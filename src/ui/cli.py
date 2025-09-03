import argparse
import os
import sys
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--use-tools", action="store_true", help="Enable tool routing")
    parser.add_argument("--quiet", action="store_true", help="Suppress debug output from tools")
    parser.add_argument("--tool-only", dest="tool_only", action="store_true",
                        help="Exit nonzero if no tool matches")
    parser.add_argument("--chain", type=int, default=1,
                        help="Max tool passes (chaining). Default 1")
    parser.add_argument("--llm", action="store_true", help="Use LLM for fallback if no tool matches")
    parser.add_argument("--llm-only", action="store_true", help="Bypass tools and query the LLM directly")
    parser.add_argument("--json", action="store_true", help="Emit JSON with {mode, tool, passes, text, usage}")
    parser.add_argument("--base", help="OpenAI-compatible base URL (e.g., http://127.0.0.1:8000/v1)")
    parser.add_argument("--model", help="Model name (e.g., Qwen/Qwen2.5-7B-Instruct)")
    parser.add_argument("--ctx-file", help="Path to a context file to prepend for LLM paths")
    parser.add_argument("message")
    args = parser.parse_args()

    # Apply quiet BEFORE importing router/llm so debug flags are respected
    if args.quiet:
        os.environ.pop("AGENT_DEBUG", None)

    msg = args.message

    def emit(payload_text: str, mode: str, tool: str | None, passes: int = 0, usage: dict | None = None, rc: int = 0):
        if args.json:
            print(json.dumps({
                "mode": mode,           # "tools" or "llm" or "echo"
                "tool": tool,           # e.g., "calculator" or None
                "passes": passes,       # number of tool passes used
                "text": payload_text,   # final output string
                "usage": usage or {},   # LLM token usage if available
                "rc": rc,               # intended exit code
            }, ensure_ascii=False))
        else:
            print(payload_text)
        sys.exit(rc)

    # LLM-only path
    if args.llm_only:
        import os
        if args.base: os.environ["OPENAI_BASE"] = args.base
        if args.model: os.environ["OPENAI_MODEL"] = args.model
        from agent.runtime.llm_client import chat
        if args.ctx_file:
            try:
                ctx = Path(args.ctx_file).read_text(encoding="utf-8")
                msg = f"Context:\n{ctx}\n\nUser:\n{msg}"
            except Exception:
                pass
        text, usage = chat(msg)
        emit(text, mode="llm", tool=None, passes=0, usage=usage, rc=0)

    # Tools path
    if args.use_tools:
        from agent.runtime.router import run_with_tools
        out, used_tool, used_count = run_with_tools(msg, max_chain=max(1, args.chain))

        if used_tool:
            emit(out, mode="tools", tool=used_tool, passes=used_count, rc=0)

        # No tool matched
        if args.tool_only and not args.llm:
            if args.json:
                print(json.dumps({"mode":"tools","tool":None,"passes":0,"text":"","usage":{},"rc":2}))
            else:
                print("No tool matched", file=sys.stderr)
            sys.exit(2)

        if args.llm:
            import os
        if args.base: os.environ["OPENAI_BASE"] = args.base
        if args.model: os.environ["OPENAI_MODEL"] = args.model
        from agent.runtime.llm_client import chat
            text, usage = chat(msg)
            emit(text, mode="llm", tool=None, passes=0, usage=usage, rc=0)

        # fallback echo
        emit(out, mode="echo", tool=None, passes=0, rc=0)

    # No tools requested
    if args.llm:
        import os
        if args.base: os.environ["OPENAI_BASE"] = args.base
        if args.model: os.environ["OPENAI_MODEL"] = args.model
        from agent.runtime.llm_client import chat
        if args.ctx_file:
            try:
                ctx = Path(args.ctx_file).read_text(encoding="utf-8")
                msg = f"Context:\n{ctx}\n\nUser:\n{msg}"
            except Exception:
                pass
        text, usage = chat(msg)
        emit(text, mode="llm", tool=None, passes=0, usage=usage, rc=0)
    else:
        emit(msg, mode="echo", tool=None, passes=0, rc=0)

if __name__ == "__main__":
    main()
