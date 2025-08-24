import sys
from ..agent.runtime.executor import Executor

def main():
    if len(sys.argv) < 2:
        print('Usage: python -m src.ui.cli "your question"')
        raise SystemExit(1)
    query = sys.argv[1]
    ex = Executor()
    print(ex.run(query))

if __name__ == "__main__":
    main()
