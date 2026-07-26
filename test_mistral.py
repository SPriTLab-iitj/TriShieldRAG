import os
from dotenv import load_dotenv
load_dotenv()   # ← this reads .env file

from mistralai import Mistral

api_key = os.getenv("MISTRAL_API_KEY")
print(f"Key loaded: {api_key[:8]}...")   # show first 8 chars to confirm

client = Mistral(api_key=api_key)

context = """[Doc 1] Tesla, Inc.
Tesla Motors was founded in 2003 by Martin Eberhard and Marc Tarpenning."""

prompt = (
    "Answer using ONLY the context. One short sentence.\n\n"
    f"Context:\n{context}\n\n"
    f"Question: Who founded Tesla Motors?\n\nAnswer:"
)

response = client.chat.complete(
    model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
    messages=[{"role": "user", "content": prompt}],
    temperature=0.0,
    max_tokens=64,
)

print(f"Mistral says: {response.choices[0].message.content.strip()}")
