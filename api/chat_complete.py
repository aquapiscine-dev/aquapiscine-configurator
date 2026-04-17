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

# Complete Category Mapping - ALL 76 categories with comprehensive keywords
CATEGORY_KEYWORDS = {
    # Încălzire (138 produse)
    'pompă|pompe|căldur|caldur|heat|heatpump': 'pompe-de-caldura',
    'încălz|incalz|heating|warm': 'incalzire-piscina',
    'solar|soare': 'incalzire-solara',
    'schimbat|exchanger|heat exchanger': 'schimbatoare-de-caldura',
    'electric|încălzitor|heater': 'incalzitoare-electrice',
    'lemne|wood|fireplace': 'incalzitoare-pe-lemne',
    
    # Filtrare (188 produse)
    'filtr|filter|filtru': 'filtrare-piscina',
    'kit filtr|filtration kit': 'kituri-filtrare',
    'material filtrant|nisip|sticla|sand|glass': 'material-filtrant',
    'piese filtr|filter parts': 'piese-schimb-filtre',
    
    # Curățare (97 produse)
    'robot|aspirat|curat|clean|vacuum': 'curatare-piscina',
    'aspirator automat|automatic cleaner': 'aspiratoare-automate',
    'aspirator manual|manual cleaner': 'aspiratoare-manuale',
    'echipament curat|cleaning equipment': 'echipamente-de-curatare',
    
    # Tratare apă (167 produse)
    'clor|chimic|tratare|ph|alg|chlorine|chemical': 'tratare-piscina',
    'chimicale piscina|pool chemicals': 'chimicale-pentru-piscina',
    'chimicale spa|spa chemicals': 'chimicale-pentru-spa',
    'electroliz|sare|salt|electrolysis': 'aparate-electroliza-si-hidroliza',
    'substanțe|substance|treatment': 'substante-pentru-tratare',
    'sterilizator|uv|ultraviolet': 'sterilizatoare-uv',
    'trusă|analiză|test|kit': 'truse-de-analiza',
    'dozator|doser|dosing': 'pompe-dozatoare',
    
    # Acoperiri (28 produse)
    'acoperire|prelata|cover|covering': 'acoperire-piscina',
    'lamelara|lamele|slat|slatted': 'acoperire-lamelara',
    'policarbonat|polycarbonate': 'acoperire-policarbonat',
    'derulat|roller|reel': 'prelate-si-derulatoare',
    
    # Placare și finisare (226 produse)
    'placare|finisa|finishing|tiling': 'placare-piscina',
    'liner|folii|folie|membrane': 'liner-si-accesorii',
    'mozaic|mosaic|tile': 'mozaic',
    'dale|bordur|coping|edging': 'dale-si-borduri',
    'adeziv|adhesive|glue': 'adezivi',
    'adeziv pvc|pvc glue': 'adezivi-lipire-pvc',
    'chit|rosturi|grout|joint': 'chit-de-rosturi',
    'hidroizola|waterproof|sealing': 'hidroizolatii',
    'vopsea|paint|coating': 'vopsea-pentru-piscine',
    'decorațiuni|decor|decoration': 'decoratiuni-piscina',
    'reparati|repair|fix': 'reparatii-si-aplicatii-speciale',
    
    # Iluminare (75 produse)
    'led|iluminat|lumina|light|lighting|lampă': 'iluminare-piscine',
    
    # Tipuri piscine (32 produse)
    'construi|constru|vreau piscin|tip|model|build': 'tipuri-de-piscine',
    'fibră|fibra|fiberglass|sticla': 'piscine-fibra-de-sticla',
    'isoblok|iso': 'piscine-isoblok',
    'suprateran|above ground': 'piscine-supraterane',
    'poliester|polipropilen|polyester': 'tipuri-de-piscine',
    
    # Spa și saună (193 produse)
    'spa|jacuzzi|hidromasaj|hot tub': 'sauna-si-spa',
    'spa portabil|portable spa': 'spa-portabil',
    'spa public|commercial spa': 'spa-public',
    'sauna|saune|steam': 'saune-uscate',
    'sauna umeda|wet sauna': 'saune-umede',
    'cabina|cabin': 'cabine-saune',
    'soba|stove|heater': 'sobe-electrice',
    'generator|steam generator': 'generatoare-de-abur',
    'dezumidificator|dehumidifier': 'dezumidificatoare',
    'lemn|wood|timber': 'lemn-si-accesorii',
    'usa|door|usi': 'usi-pentru-saune',
    'arome|esente|fragrance|scent': 'arome-si-solutii-de-curatare',
    
    # Componente (144 produse)
    'abs|pvc|component|plastic': 'componente-abs-si-pvc',
    'component abs|abs parts': 'componente-abs',
    'piese abs|abs spare': 'piese-schimb-abs',
    'țevi|fitinguri|teava|pipe|fitting': 'tevi-si-fitinguri',
    
    # Pompe (75 produse)
    'pompă piscina|circulation|pump': 'pompe-piscina',
    'piese pompă|pump parts': 'piese-schimb-pompe',
    
    # Accesorii (167 produse)
    'accesor|accessory|accessories': 'accesorii-piscine',
    'accesor olimpic|olympic': 'accesorii-piscine-olimpice',
    'accesor spa|spa accessories': 'accesorii-spa',
    'accesor confort|comfort': 'accesorii-confort',
    'scara|scarita|ladder|stairs|balustrad': 'scari-si-balustrade',
    'echipament exterior|outdoor|furniture': 'echipamente-exterioare',
    'înot contracurent|counter current|jet': 'inot-contracurent',
    'cascade|waterfall|fountain|fântână': 'echipamente-exterioare',
    
    # Control și automatizare
    'tablou|panou|control|panel': 'panouri-de-comanda',
    'tablou electric|electrical panel': 'tablouri-comanda',
    
    # Oferte
    'lichidare|oferta|discount|sale|promo': 'lichidari-de-stoc',
    'aquapiscine|brand': 'aquapiscine'
}

SYSTEM_PROMPT = """Ești asistent vânzări AI pentru AquaPiscine.ro.

Răspunzi la întrebări despre piscine și echipamente.

IMPORTANT: 
- NU menționa nume specifice de produse în răspunsul tău
- NU include prețuri în text
- Produsele din catalogul furnizat vor fi afișate AUTOMAT sub mesajul tău cu imagini, prețuri și link-uri
- Vorbește despre CATEGORII și TIPURI de produse, nu despre produse individuale
- Exemplu CORECT: "Avem reduceri la echipamente de curățare și filtrare"
- Exemplu GREȘIT: "Avem Aspiratorul Zodiac la 2500 RON"

Contact:
- Telefon: 0772 286 246
- Email: contact@aquapiscine.ro

Răspunde în limba română, profesionist, concis și util."""

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
    """Get products by category and return category info + products"""
    try:
        # First get category ID and info
        cat_url = f"{WP_URL}/wp-json/wc/v3/products/categories"
        cat_response = requests.get(
            cat_url,
            params={'slug': category_slug},
            auth=HTTPBasicAuth(WP_CONSUMER_KEY, WP_CONSUMER_SECRET),
            timeout=30
        )
        
        if cat_response.status_code != 200 or not cat_response.json():
            return {'products': [], 'category': None}
        
        category_data = cat_response.json()[0]
        category_id = category_data['id']
        
        # Category info
        category_info = {
            'name': category_data['name'],
            'image': category_data.get('image', {}).get('src') if category_data.get('image') else None,
            'link': f"{WP_URL}/categorie-produs/{category_slug}/",
            'count': category_data.get('count', 0)
        }
        
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
            product_list = [{
                'id': p['id'],
                'name': p['name'],
                'price': float(p['price']) if p['price'] else 0,
                'image': p['images'][0]['src'] if p['images'] else None,
                'permalink': p['permalink'],
                'stock_status': p['stock_status'],
                'short_description': p['short_description']
            } for p in products]
            
            return {'products': product_list, 'category': category_info}
        
        return {'products': [], 'category': category_info}
    except Exception as e:
        print(f"Category error: {e}")
        return {'products': [], 'category': None}

def find_relevant_products(query):
    """Find relevant products based on query - TOATE cele 76 categorii"""
    query_lower = query.lower()
    
    # Verifică fiecare pattern din mapping-ul complet
    for pattern, category in CATEGORY_KEYWORDS.items():
        keywords = pattern.split('|')
        if any(keyword in query_lower for keyword in keywords):
            result = get_products_by_category(category, 5)
            if result['products']:
                return result
    
    # Generic search ca fallback
    return {'products': search_woocommerce_products(query, 5), 'category': None}

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
            
            # Find relevant products and category
            result = find_relevant_products(user_message)
            products = result['products']
            category = result['category']
            
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
                "category": category,
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
