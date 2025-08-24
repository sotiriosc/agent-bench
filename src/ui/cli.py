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
    parser.add_argument("message")
    args = parser.parse_args()

    # Apply quiet BEFORE importing router so debug flags are respected
    if args.quiet:
        os.environ.pop("AGENT_DEBUG", None)

    msg = args.message

    if not args.use_tools:
        # No tool routing: simple echo (keeps CLI deterministic)
        print(msg)
        return

    # Lazy import after quiet handling
    from agent.runtime.router import run_with_tools

    out, used_tool, used_count = run_with_tools(msg, max_chain=max(1, args.chain))

    if used_tool:
        print(out)
        sys.exit(0)
    else:
        if args.tool_only:
            print("No tool matched", file=sys.stderr)
            sys.exit(2)
        print(out)  # fallback echo
        sys.exit(0)

if __name__ == "__main__":
    main()
