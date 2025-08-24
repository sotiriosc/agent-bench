from dotenv import load_dotenv
import os, sys

# Load .env → puts OPENAI_API_KEY into env
load_dotenv()
print("Key present:", bool(os.getenv("OPENAI_API_KEY")))

# Use the modern OpenAI SDK (Responses API)
try:
    import openai
    from openai import OpenAI
    print("openai version:", openai.__version__)
except Exception as e:
    print("OpenAI SDK not available:", e)
    sys.exit(1)

client = OpenAI()  # reads OPENAI_API_KEY from env

# Try a simple Responses API call
try:
    resp = client.responses.create(
        model="gpt-4.1-mini",  # if this errors, try "gpt-4o-mini"
        input="Say hello in one short sentence."
    )
    print("Model reply:", resp.output_text)
except Exception as e:
    print("API call failed:", e)
    # Helpful hint: sometimes pinning versions helps
    print('If this persists, run: pip install "openai>=1.40.0" "httpx>=0.27.0,<0.28.0" "httpcore>=1.0.5"')
    sys.exit(1)

