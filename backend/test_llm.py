import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

resp = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "What's the key HIPAA rule?"}],
    max_tokens=50,
)

print(resp.choices[0].message.content)
