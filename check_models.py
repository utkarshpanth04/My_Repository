import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    models = genai.list_models()
    for model in models:
        print(model.name)
except Exception as e:
    print(f"❌ Error listing models: {str(e)}")
