import os

from dotenv import load_dotenv

# Read the .env file (on your laptop). In Docker or AWS, the values come
# from the real environment, and load_dotenv does nothing harmful.
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Only these models are allowed. Check the Groq website for current names.
ALLOWED_MODEL_NAMES = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]