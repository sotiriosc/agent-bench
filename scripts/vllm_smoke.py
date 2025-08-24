from vllm import LLM, SamplingParams

def main():
    model = "Qwen/Qwen2.5-7B-Instruct"  # fits nicely on a 4090
    llm = LLM(
        model=model,
        dtype="float16",
        tensor_parallel_size=1,
        gpu_memory_utilization=0.90,
        max_model_len=4096,
    )
    outs = llm.generate(
        ["Write one short sentence about GPUs and speed."],
        SamplingParams(max_tokens=32, temperature=0)
    )
    print(outs[0].outputs[0].text.strip())

if __name__ == "__main__":
    main()
