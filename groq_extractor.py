import os
import base64
import json
import re
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class GroqInvoiceExtractor:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.prompt = """Extract all key-value pairs from this invoice image. Return JSON with...
        """

    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def get_image_mime_type(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower().strip(".")
        return {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'webp': 'image/webp'}.get(ext, 'image/jpeg')

    def extract(self, image_path: str) -> Dict[str, Any]:
        try:
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{self.get_image_mime_type(image_path)};base64,{self.encode_image(image_path)}"}}
                    ]
                }],
                "temperature": 0.1,
                "max_tokens": 4000
            }
            response = requests.post(self.groq_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return self._parse_response(response.json()["choices"][0]["message"]["content"])
            return {}
        except:
            return {}

    def _parse_response(self, content: str) -> Dict[str, Any]:
        try:
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL) or re.search(r"(\{.*\})", content, re.DOTALL)
            return json.loads(match.group(1)) if match else {}
        except:
            return {}
