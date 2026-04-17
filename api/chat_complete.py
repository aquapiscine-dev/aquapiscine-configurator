"""
Chat Support API - Complete Standalone Version
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import random
from groq import Groq

# Groq API Keys
GROQ_KEYS = [
    os.getenv('GROQ_API_KEY_1'),
    os.getenv('GROQ_API_KEY_2')
]

SYSTEM_PROMPT = """Ești asistent vânzări AI pentru AquaPiscine.ro.

Răspunzi la întrebări despre piscine și echipamente.
Ești prietenos, profesionist și util.

Contact:
- Telefon: 0772 286 246
- Email: contact@aquapiscine.ro

Răspunde în limba română, concis."""

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            if 'message' not in data:
                self.send_json({"success": False, "error": "Mesaj lipsă"}, 400)
                return
            
            user_message = data['message'].strip()
            
            # Call Groq AI
            client = Groq(api_key=random.choice(GROQ_KEYS))
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            self.send_json({
                "success": True,
                "response": ai_response,
                "conversation_id": data.get('conversation_id', 'new')
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
