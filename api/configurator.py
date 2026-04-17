"""
Configurator Piscine - Endpoint conversațional cu Groq AI
"""

from flask import Flask, request, jsonify
from utils import call_groq_text, sanitize_user_input, validate_conversation_id, extract_dimensions_from_text, calculate_pool_volume, format_price
from woocommerce import get_recommended_products, search_products
import json

app = Flask(__name__)

# Conversation storage (în producție: Redis/Database)
conversations = {}

SYSTEM_PROMPT = """Ești asistent AI pentru AquaPiscine.ro, specialist în configurarea și vânzarea piscine.

ROLUL TĂU:
- Ajuți clienții să configureze piscina perfectă
- Recomandări personalizate bazate pe nevoile lor
- Produse reale din catalog WooCommerce
- Calcul preț transparent și detaliat
- Ghidare pas cu pas prin proces

STIL CONVERSAȚIE:
- Prietenos și profesionist
- Întrebări clare și directe
- Răspunsuri structurate cu bullet points
- Emoji-uri pentru claritate (🏊, 💰, ✅, etc)
- Încheie cu call-to-action

PROCES CONFIGURARE:
1. Dimensiuni piscină (lungime x lățime)
2. Tip piscină (beton, fibră sticlă, liner)
3. Echipamente (filtrare, încălzire, LED, etc)
4. Servicii extra (excavare, finisaje, deck)
5. Rezumat ofertă + contact

REGULI:
- Folosește DOAR produse din catalogul furnizat
- Prețuri în RON
- Recomandări bazate pe volum piscină
- Menționează stoc disponibil
- Include link-uri produse
- Fii transparent cu costurile

CONTACT:
- Telefon: 0772 286 246
- Email: contact@aquapiscine.ro
- WhatsApp: https://wa.me/40772286246

Răspunde întotdeauna în limba română."""

@app.route('/api/configurator', methods=['POST'])
def configurator_chat():
    """
    Endpoint conversație configurator
    
    Request:
        {
            "message": "Mesaj user",
            "conversation_id": "uuid" (opțional),
            "context": {} (opțional - dimensiuni, tip, etc)
        }
        
    Response:
        {
            "success": true,
            "response": "Răspuns AI",
            "conversation_id": "uuid",
            "products": [...],
            "estimated_price": 0,
            "next_step": "..."
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Mesaj lipsă"
            }), 400
        
        user_message = sanitize_user_input(data['message'])
        conversation_id = validate_conversation_id(data.get('conversation_id'))
        context = data.get('context', {})
        
        # Inițializează conversație dacă e nouă
        if conversation_id not in conversations:
            conversations[conversation_id] = {
                "messages": [],
                "config": {
                    "dimensions": None,
                    "pool_type": None,
                    "volume": None,
                    "equipment": [],
                    "extras": []
                },
                "total_price": 0
            }
        
        conversation = conversations[conversation_id]
        
        # Extrage dimensiuni din mesaj (dacă există)
        dimensions = extract_dimensions_from_text(user_message)
        if dimensions:
            conversation['config']['dimensions'] = dimensions
            conversation['config']['volume'] = calculate_pool_volume(
                dimensions['length'],
                dimensions['width']
            )
        
        # Construiește context pentru AI
        ai_context = build_ai_context(conversation, context)
        
        # Adaugă mesaj user
        conversation['messages'].append({
            "role": "user",
            "content": user_message
        })
        
        # Construiește messages pentru Groq
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": ai_context}
        ] + conversation['messages']
        
        # Apel Groq AI
        ai_response = call_groq_text(messages, max_tokens=1500)
        
        # Adaugă răspuns AI în conversație
        conversation['messages'].append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Extrage produse menționate
        products = extract_products_from_response(ai_response, conversation['config'])
        
        # Calculează preț estimat
        estimated_price = calculate_estimated_price(conversation['config'], products)
        conversation['total_price'] = estimated_price
        
        # Determină next step
        next_step = determine_next_step(conversation)
        
        return jsonify({
            "success": True,
            "response": ai_response,
            "conversation_id": conversation_id,
            "products": products,
            "estimated_price": estimated_price,
            "next_step": next_step,
            "config": conversation['config']
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Eroare configurator: {str(e)}"
        }), 500

def build_ai_context(conversation: dict, additional_context: dict) -> str:
    """
    Construiește context pentru AI bazat pe conversație
    
    Args:
        conversation: Conversație curentă
        additional_context: Context adițional
        
    Returns:
        String context pentru AI
    """
    config = conversation['config']
    
    context_parts = ["CONTEXT CONVERSAȚIE:"]
    
    if config['dimensions']:
        dim = config['dimensions']
        context_parts.append(f"- Dimensiuni: {dim['length']}x{dim['width']}m ({dim['area']}m²)")
        context_parts.append(f"- Volum estimat: {config['volume']:.1f}m³")
    
    if config['pool_type']:
        context_parts.append(f"- Tip piscină: {config['pool_type']}")
    
    if config['equipment']:
        context_parts.append(f"- Echipamente selectate: {', '.join(config['equipment'])}")
    
    if config['extras']:
        context_parts.append(f"- Servicii extra: {', '.join(config['extras'])}")
    
    if conversation['total_price'] > 0:
        context_parts.append(f"- Preț total curent: {format_price(conversation['total_price'])}")
    
    # Adaugă produse relevante din WooCommerce
    if config['volume']:
        products_context = get_products_context(config)
        if products_context:
            context_parts.append("\nPRODUSE DISPONIBILE:")
            context_parts.append(products_context)
    
    return "\n".join(context_parts)

def get_products_context(config: dict) -> str:
    """
    Obține context produse din WooCommerce
    
    Args:
        config: Configurație curentă
        
    Returns:
        String cu produse relevante
    """
    if not config.get('volume'):
        return ""
    
    pool_type = config.get('pool_type', 'fibra')
    volume = config['volume']
    
    # Obține produse recomandate
    recommended = get_recommended_products(pool_type, volume)
    
    context_lines = []
    
    # Filtrare
    if recommended['filtration']:
        context_lines.append("\nFILTRARE:")
        for prod in recommended['filtration'][:3]:
            context_lines.append(f"- {prod['name']}: {format_price(prod['price'])} ({prod['permalink']})")
    
    # Încălzire
    if recommended['heating']:
        context_lines.append("\nÎNCĂLZIRE:")
        for prod in recommended['heating'][:3]:
            context_lines.append(f"- {prod['name']}: {format_price(prod['price'])} ({prod['permalink']})")
    
    # Iluminare
    if recommended['lighting']:
        context_lines.append("\nILUMINARE:")
        for prod in recommended['lighting'][:3]:
            context_lines.append(f"- {prod['name']}: {format_price(prod['price'])} ({prod['permalink']})")
    
    return "\n".join(context_lines)

def extract_products_from_response(response: str, config: dict) -> list:
    """
    Extrage produse menționate în răspuns AI
    
    Args:
        response: Răspuns AI
        config: Configurație
        
    Returns:
        Listă produse
    """
    products = []
    
    # Caută produse în răspuns
    if config.get('volume'):
        pool_type = config.get('pool_type', 'fibra')
        volume = config['volume']
        
        recommended = get_recommended_products(pool_type, volume)
        
        # Verifică ce categorii sunt menționate
        if 'filtr' in response.lower():
            products.extend(recommended['filtration'][:2])
        
        if 'încălz' in response.lower() or 'pompă' in response.lower():
            products.extend(recommended['heating'][:2])
        
        if 'led' in response.lower() or 'iluminat' in response.lower():
            products.extend(recommended['lighting'][:2])
    
    return products

def calculate_estimated_price(config: dict, products: list) -> float:
    """
    Calculează preț estimat total
    
    Args:
        config: Configurație
        products: Produse selectate
        
    Returns:
        Preț total
    """
    total = 0.0
    
    # Preț piscină bazat pe tip și dimensiuni
    if config.get('dimensions') and config.get('pool_type'):
        area = config['dimensions']['area']
        pool_type = config['pool_type']
        
        # Prețuri estimate per m²
        price_per_sqm = {
            'beton': 1000,
            'fibra': 750,
            'liner': 600
        }
        
        base_price = area * price_per_sqm.get(pool_type, 750)
        total += base_price
    
    # Adaugă prețuri produse
    for product in products:
        total += product.get('price', 0)
    
    # Excavare (dacă menționată)
    if 'excavare' in config.get('extras', []):
        total += 5000  # Preț mediu excavare
    
    return total

def determine_next_step(conversation: dict) -> str:
    """
    Determină următorul pas în configurare
    
    Args:
        conversation: Conversație
        
    Returns:
        Next step
    """
    config = conversation['config']
    
    if not config['dimensions']:
        return "dimensions"
    elif not config['pool_type']:
        return "pool_type"
    elif not config['equipment']:
        return "equipment"
    elif not config['extras']:
        return "extras"
    else:
        return "summary"

def handler(request):
    """Vercel serverless function handler"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == '__main__':
    app.run(debug=True)
