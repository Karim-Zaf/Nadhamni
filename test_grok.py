from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

grok_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=grok_key)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "who won football world cup 2001?"}]
)

print(response.choices[0].message.content)
