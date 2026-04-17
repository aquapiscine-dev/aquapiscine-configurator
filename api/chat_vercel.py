"""
Chat Support API - Vercel Serverless Function
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.utils import call_groq_text, sanitize_user_input, validate_conversation_id, format_price
from api.woocommerce import search_products, get_products_by_category

# In-memory storage (pentru demo - în producție folosește Redis/Database)
chat_conversations = {}

CHAT_SYSTEM_PROMPT = """Ești asistent vânzări AI pentru AquaPiscine.ro, magazin online de piscine și echipamente.

ROLUL TĂU:
- Răspunzi la întrebări despre produse
- Recomandări personalizate
- Ajuți clienții să găsească produsul potrivit

CONTACT:
- Telefon: 0772 286 246
- Email: contact@aquapiscine.ro

Răspunde în limba română, concis și util."""

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if 'message' not in data:
                self.send_error_response(400, "Mesaj lipsă")
                return
            
            user_message = sanitize_user_input(data['message'])
            conversation_id = validate_conversation_id(data.get('conversation_id'))
            
            # Initialize conversation
            if conversation_id not in chat_conversations:
                chat_conversations[conversation_id] = {"messages": []}
            
            conversation = chat_conversations[conversation_id]
            
            # Find relevant products
            relevant_products = self.find_relevant_products(user_message)
            
            # Build context
            products_context = self.build_products_context(relevant_products)
            
            # Add user message
            conversation['messages'].append({
                "role": "user",
                "content": user_message
            })
            
            # Build messages for Groq
            messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
            
            if products_context:
                messages.append({
                    "role": "system",
                    "content": f"PRODUSE RELEVANTE:\n{products_context}"
                })
            
            messages.extend(conversation['messages'])
            
            # Call Groq AI
            ai_response = call_groq_text(messages, max_tokens=1000)
            
            # Add AI response
            conversation['messages'].append({
                "role": "assistant",
                "content": ai_response
            })
            
            # Send response
            self.send_json_response({
                "success": True,
                "response": ai_response,
                "conversation_id": conversation_id,
                "products": relevant_products[:5]
            })
            
        except Exception as e:
            self.send_error_response(500, f"Eroare: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def find_relevant_products(self, query):
        """Find relevant products"""
        keywords_map = {
            'pompă': ['pompe-caldura'],
            'filtr': ['filtrare'],
            'led': ['iluminare'],
            'clor': ['tratare']
        }
        
        products = []
        for keyword, categories in keywords_map.items():
            if keyword in query.lower():
                for category in categories:
                    products.extend(get_products_by_category(category, per_page=3))
                break
        
        if not products:
            products = search_products(query, per_page=5)
        
        return products
    
    def build_products_context(self, products):
        """Build products context"""
        if not products:
            return ""
        
        lines = []
        for prod in products[:5]:
            line = f"- {prod['name']}: {format_price(prod['price'])}"
            if prod.get('stock_status') == 'instock':
                line += " ✅"
            lines.append(line)
        
        return "\n".join(lines)
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error = {"success": False, "error": message}
        self.wfile.write(json.dumps(error).encode('utf-8'))
