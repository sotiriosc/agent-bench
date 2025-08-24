import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--use-tools", action="store_true", help="enable tool routing")
    parser.add_argument("--quiet", action="store_true", help="suppress AGENT_DEBUG prints")
    parser.add_argument("--tool-only", action="store_true", help="exit with error if no tool matches")
    parser.add_argument("message")
    args = parser.parse_args()

    # Apply quiet BEFORE importing Executor/router so their DEBUG checks see it
    if args.quiet:
        os.environ.pop("AGENT_DEBUG", None)

    # Lazy import now that env is set the way we want
    from agent.runtime.executor import Executor

    msg = args.message
    ex = Executor()

    if args.use_tools:
        out, used_tool = ex.run_with_tools(msg)
        if used_tool:
            print(out)
            sys.exit(0)
        if args.tool_only:
            print("No tool matched", file=sys.stderr)
            sys.exit(2)
        print(out)
        sys.exit(0)

    # Plain chat
    print(ex.run(msg))

if __name__ == "__main__":
    main()
