from dotenv import load_dotenv
from openai import OpenAI

# Load .env once (puts OPENAI_API_KEY into the environment)
load_dotenv()

# Reuse a single client. It will read OPENAI_API_KEY from the environment.
_client = OpenAI()


def chat_once(prompt: str, model: str = "gpt-4.1-mini") -> str:
    """
    One-shot call to OpenAI Responses API.
    Returns plain text (rsp.output_text).
    """
    rsp = _client.responses.create(
        model=model,  # You can switch to "gpt-4o-mini" if you prefer
        input=prompt,
        temperature=0.2,
        max_output_tokens=300,
    )
    return rsp.output_text
