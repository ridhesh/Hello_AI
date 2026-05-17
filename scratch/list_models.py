import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tools.bootstrap

from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
print("Available Models:")
for model in client.models.list():
    supported_actions = getattr(model, 'supported_actions', None)
    supported_methods = getattr(model, 'supported_methods', None)
    if supported_actions and "generateContent" in supported_actions:
        print(f"- {model.name}")
    elif supported_methods and "generateContent" in supported_methods:
        print(f"- {model.name}")
