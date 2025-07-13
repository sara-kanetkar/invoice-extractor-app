import base64
import json
import re
import requests
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiInvoiceExtractor:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_api_key}"
        self.extraction_prompt = """
        Extract all the key-value pairs from this invoice image.
        Format the result as:
        {
          "Field Name": {"value": "field value", "confidence": 95}
        }
        """

    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def get_image_mime_type(self, image_path: str) -> str:
        ext = image_path.lower().split('.')[-1]
        return {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'webp': 'image/webp'
        }.get(ext, 'image/png')

    def extract(self, image_path: str) -> Dict[str, Any]:
        try:
            encoded = self.encode_image(image_path)
            mime = self.get_image_mime_type(image_path)
            json_data = {
                "contents": [{
                    "parts": [
                        {"text": self.extraction_prompt},
                        {"inline_data": {"mime_type": mime, "data": encoded}}
                    ]
                }]
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.gemini_url, headers=headers, json=json_data, timeout=30)
            if response.status_code == 200:
                content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                return self._parse_json_response(content)
            return {}
        except:
            return {}

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        try:
            content = content.strip()
            if content.startswith("```"):
                content = "\n".join(content.splitlines()[1:-1])
            match = re.search(r"(\{.*\})", content, re.DOTALL)
            return json.loads(match.group(1)) if match else {}
        except:
            return {}

# ✅ THIS GOES OUTSIDE THE CLASS
def extract_text_and_fields(image_path):
    extractor = GeminiInvoiceExtractor()
    return extractor.extract(image_path)
