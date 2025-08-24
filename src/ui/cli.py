import argparse
import os
import sys

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
    parser.add_argument("message")
    args = parser.parse_args()

    # Apply quiet BEFORE importing router so debug flags are respected
    if args.quiet:
        os.environ.pop("AGENT_DEBUG", None)

    msg = args.message

    # LLM-only path
    if args.llm_only:
        from agent.runtime.llm_client import chat
        text, _usage = chat(msg)
        print(text)
        sys.exit(0)

    # Tools path
    if args.use_tools:
        from agent.runtime.router import run_with_tools
        out, used_tool, used_count = run_with_tools(msg, max_chain=max(1, args.chain))

        if used_tool:
            print(out)
            sys.exit(0)

        # No tool matched
        if args.tool_only and not args.llm:
            print("No tool matched", file=sys.stderr)
            sys.exit(2)

        if args.llm:
            from agent.runtime.llm_client import chat
            text, _usage = chat(msg)
            print(text)
            sys.exit(0)

        # fallback echo
        print(out)
        sys.exit(0)

    # No tools requested
    if args.llm:
        from agent.runtime.llm_client import chat
        text, _usage = chat(msg)
        print(text)
    else:
        print(msg)

if __name__ == "__main__":
    main()
