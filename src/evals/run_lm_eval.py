import argparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task", type=str, default="gsm8k_toy")
    args = p.parse_args()

    if args.task == "gsm8k_toy":
        print("TASK: gsm8k_toy -> Q: 23*17")
        print("GT: 391")
        print('Try: python -m src.ui.cli "What is 23*17? Use the calculator."')
    else:
        print(f"Unknown task: {args.task}")

if __name__ == "__main__":
    main()
