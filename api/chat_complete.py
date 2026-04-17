"""
Chat Support API with WooCommerce Integration
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import random
import requests
from requests.auth import HTTPBasicAuth
from groq import Groq

# Groq API Keys
GROQ_KEYS = [
    os.getenv('GROQ_API_KEY_1'),
    os.getenv('GROQ_API_KEY_2')
]

# WooCommerce Config
WP_URL = os.getenv('WP_URL', 'https://aquapiscine.ro')
WP_CONSUMER_KEY = os.getenv('WP_CONSUMER_KEY')
WP_CONSUMER_SECRET = os.getenv('WP_CONSUMER_SECRET')

SYSTEM_PROMPT = """Ești asistent vânzări AI pentru AquaPiscine.ro.

Răspunzi la întrebări despre piscine și echipamente.
Când vorbești despre produse, MENȚIONEAZĂ produsele din catalogul furnizat.

Contact:
- Telefon: 0772 286 246
- Email: contact@aquapiscine.ro

Răspunde în limba română, profesionist și util."""

def search_woocommerce_products(query, per_page=5):
    """Search products in WooCommerce"""
    try:
        url = f"{WP_URL}/wp-json/wc/v3/products"
        params = {
            'search': query,
            'per_page': per_page,
            'status': 'publish'
        }
        
        response = requests.get(
            url,
            params=params,
            auth=HTTPBasicAuth(WP_CONSUMER_KEY, WP_CONSUMER_SECRET),
            timeout=10
        )
        
        if response.status_code == 200:
            products = response.json()
            return [{
                'id': p['id'],
                'name': p['name'],
                'price': float(p['price']) if p['price'] else 0,
                'image': p['images'][0]['src'] if p['images'] else None,
                'permalink': p['permalink'],
                'stock_status': p['stock_status'],
                'short_description': p['short_description']
            } for p in products]
        return []
    except Exception as e:
        print(f"WooCommerce error: {e}")
        return []

def get_products_by_category(category_slug, per_page=5):
    """Get products by category"""
    try:
        # First get category ID
        cat_url = f"{WP_URL}/wp-json/wc/v3/products/categories"
        cat_response = requests.get(
            cat_url,
            params={'slug': category_slug},
            auth=HTTPBasicAuth(WP_CONSUMER_KEY, WP_CONSUMER_SECRET),
            timeout=30
        )
        
        if cat_response.status_code != 200 or not cat_response.json():
            return []
        
        category_id = cat_response.json()[0]['id']
        
        # Get products
        url = f"{WP_URL}/wp-json/wc/v3/products"
        response = requests.get(
            url,
            params={'category': category_id, 'per_page': per_page, 'status': 'publish'},
            auth=HTTPBasicAuth(WP_CONSUMER_KEY, WP_CONSUMER_SECRET),
            timeout=30
        )
        
        if response.status_code == 200:
            products = response.json()
            return [{
                'id': p['id'],
                'name': p['name'],
                'price': float(p['price']) if p['price'] else 0,
                'image': p['images'][0]['src'] if p['images'] else None,
                'permalink': p['permalink'],
                'stock_status': p['stock_status'],
                'short_description': p['short_description']
            } for p in products]
        return []
    except Exception as e:
        print(f"Category error: {e}")
        return []

def find_relevant_products(query):
    """Find relevant products based on query"""
    query_lower = query.lower()
    
    # Mapping complet categorii WooCommerce
    category_map = {
        'pompă|pompe|căldur|caldur': 'pompe-de-caldura',
        'filtr': 'filtrare',
        'robot|aspirat|curat': 'aspiratoare-automate',
        'led|iluminat|lumina': 'iluminare',
        'clor|chimic|tratare|alg': 'chimicale-pentru-piscina',
        'încălz|incalz': 'incalzire-piscina',
        'acoperire|prelata': 'acoperire-piscina',
        'scara|scarita': 'scari-piscina',
        'duș|dus': 'dusuri-piscina',
        'spa|jacuzzi|hidromasaj': 'cazi-hidromasaj',
        'sauna': 'cabine-saune',
        'electroliz|sare': 'aparate-electroliza-si-hidroliza',
        'liner|folii': 'liner-piscina',
        'skimmer': 'skimmere',
        'duze|jet': 'duze-piscina',
        'vana|robinet': 'vane-piscina',
        'termostat|control': 'automatizari-piscina'
    }
    
    # Verifică fiecare pattern
    for pattern, category in category_map.items():
        keywords = pattern.split('|')
        if any(keyword in query_lower for keyword in keywords):
            products = get_products_by_category(category, 5)
            if products:
                return products
    
    # Cazuri speciale
    if 'piscin' in query_lower and any(word in query_lower for word in ['tip', 'model', 'ofer']):
        return get_products_by_category('piscine', 6)
    
    # Generic search ca fallback
    return search_woocommerce_products(query, 5)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            if 'message' not in data:
                self.send_json({"success": False, "error": "Mesaj lipsă"}, 400)
                return
            
            user_message = data['message'].strip()
            
            # Find relevant products
            products = find_relevant_products(user_message)
            
            # Build context with products
            products_context = ""
            if products:
                products_context = "\n\nPRODUSE DISPONIBILE:\n"
                for p in products[:5]:
                    products_context += f"- {p['name']}: {p['price']:.0f} RON"
                    if p['stock_status'] == 'instock':
                        products_context += " (În stoc)"
                    products_context += f" - {p['permalink']}\n"
            
            # Call Groq AI
            api_key = random.choice([k for k in GROQ_KEYS if k])
            if not api_key:
                self.send_json({"success": False, "error": "API key not configured"}, 500)
                return
                
            client = Groq(api_key=api_key)
            
            system_prompt_with_products = SYSTEM_PROMPT + products_context
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt_with_products},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            self.send_json({
                "success": True,
                "response": ai_response,
                "products": products[:5],
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
