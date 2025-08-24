# cli.py
import argparse

from ..agent.runtime.executor import Executor


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--use-tools", action="store_true", help="Route through tool executor")
    p.add_argument("message", help="User message / expression")  # positional instead of --message
    args = p.parse_args()

    ex = Executor(use_tools=args.use_tools)
    print(ex.run_tools(args.message) if args.use_tools else ex.run(args.message))


if __name__ == "__main__":
    main()
