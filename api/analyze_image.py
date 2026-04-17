"""
Image Analysis API - Groq Vision for pool site analysis
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import random
import base64
from groq import Groq

# Groq API Keys
GROQ_KEYS = [
    os.getenv('GROQ_API_KEY_1'),
    os.getenv('GROQ_API_KEY_2')
]

ANALYSIS_PROMPT = """Analizează această imagine a grădinii/terenului pentru instalarea unei piscine.

Identifică și descrie:

1. **DIMENSIUNI TEREN:**
   - Suprafață totală disponibilă (estimare în m²)
   - Formă teren (dreptunghiular, L, neregulat)
   - Spațiu util pentru piscină

2. **CARACTERISTICI TEREN:**
   - Tip teren: plan, ușor înclinat, foarte înclinat
   - Calitate sol vizibilă

3. **OBSTACOLE:**
   - Copaci (număr, poziție, dimensiune)
   - Construcții existente
   - Garduri, alei

4. **ORIENTARE:**
   - Zone însorite vs umbrite
   - Orientare optimă pentru piscină

5. **RECOMANDĂRI:**
   - Dimensiune piscină optimă (ex: 8x4m, 10x5m)
   - Tip piscină recomandat (fibră, beton, polipropilenă)
   - Poziționare ideală
   - Echipamente necesare (pompă căldură, filtrare, etc)
   - Estimare costuri aproximative

Răspunde în limba română, clar și structurat."""

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            if 'image' not in data:
                self.send_json({"success": False, "error": "Imagine lipsă"}, 400)
                return
            
            # Image should be base64 encoded
            image_data = data['image']
            
            # Remove data:image/... prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Call Groq Vision
            api_key = random.choice([k for k in GROQ_KEYS if k])
            if not api_key:
                self.send_json({"success": False, "error": "API key not configured"}, 500)
                return
                
            client = Groq(api_key=api_key)
            
            response = client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": ANALYSIS_PROMPT
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            
            self.send_json({
                "success": True,
                "analysis": analysis
            })
            
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
