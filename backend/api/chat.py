"""
Chat Support AI - Asistent vânzări 24/7
"""

from flask import Flask, request, jsonify
from utils import call_groq_text, sanitize_user_input, validate_conversation_id, format_price
from woocommerce import search_products, get_product_by_id, get_products_by_category
import json

app = Flask(__name__)

# Conversation storage
chat_conversations = {}

CHAT_SYSTEM_PROMPT = """Ești asistent vânzări AI pentru AquaPiscine.ro, magazin online de piscine și echipamente.

ROLUL TĂU:
- Răspunzi la întrebări despre produse
- Recomandări personalizate
- Ajuți clienții să găsească produsul potrivit
- Rezolvi probleme tehnice (apă verde, filtrare, etc)
- Ghidezi către achiziție

STIL:
- Prietenos și util
- Răspunsuri clare și concise
- Emoji-uri pentru claritate
- Link-uri directe produse
- Call-to-action la final

PRODUSE DISPONIBILE:
- Piscine (fibră sticlă, supraterane, Isoblok)
- Filtrare (pompe, filtre, material filtrant)
- Încălzire (pompe căldură, încălzitoare electrice)
- Tratare apă (clor, algicide, pH)
- Iluminare LED
- Curățare (aspiratoare, roboti)
- Acoperiri
- Accesorii

CONTACT:
- Telefon: 0772 286 246
- Email: contact@aquapiscine.ro
- WhatsApp: https://wa.me/40772286246

REGULI:
- Folosește DOAR produse din catalogul furnizat
- Prețuri în RON
- Menționează stoc disponibil
- Include link-uri produse
- Sugerează produse complementare
- Încheie cu întrebare sau call-to-action

Răspunde în limba română."""

@app.route('/api/chat', methods=['POST'])
def chat_support():
    """
    Endpoint chat support
    
    Request:
        {
            "message": "Mesaj user",
            "conversation_id": "uuid" (opțional)
        }
        
    Response:
        {
            "success": true,
            "response": "Răspuns AI",
            "conversation_id": "uuid",
            "products": [...],
            "suggestions": [...]
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
        
        # Inițializează conversație
        if conversation_id not in chat_conversations:
            chat_conversations[conversation_id] = {
                "messages": [],
                "context": {}
            }
        
        conversation = chat_conversations[conversation_id]
        
        # Caută produse relevante
        relevant_products = find_relevant_products(user_message)
        
        # Construiește context cu produse
        products_context = build_products_context(relevant_products)
        
        # Adaugă mesaj user
        conversation['messages'].append({
            "role": "user",
            "content": user_message
        })
        
        # Construiește messages pentru Groq
        messages = [
            {"role": "system", "content": CHAT_SYSTEM_PROMPT}
        ]
        
        if products_context:
            messages.append({
                "role": "system",
                "content": f"PRODUSE RELEVANTE:\n{products_context}"
            })
        
        messages.extend(conversation['messages'])
        
        # Apel Groq AI
        ai_response = call_groq_text(messages, max_tokens=1000)
        
        # Adaugă răspuns AI
        conversation['messages'].append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Generează sugestii quick reply
        suggestions = generate_suggestions(user_message, ai_response)
        
        return jsonify({
            "success": True,
            "response": ai_response,
            "conversation_id": conversation_id,
            "products": relevant_products[:5],
            "suggestions": suggestions
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Eroare chat: {str(e)}"
        }), 500

def find_relevant_products(query: str) -> list:
    """
    Găsește produse relevante pentru query
    
    Args:
        query: Query utilizator
        
    Returns:
        Listă produse relevante
    """
    products = []
    
    # Keywords mapping
    keywords_map = {
        'pompă': ['pompe-caldura', 'pompe'],
        'filtr': ['filtrare'],
        'încălz': ['incalzire', 'pompe-caldura'],
        'led': ['iluminare'],
        'clor': ['tratare'],
        'robot': ['aspiratoare'],
        'acoperire': ['acoperire'],
        'piscină': ['piscine']
    }
    
    # Caută în query
    for keyword, categories in keywords_map.items():
        if keyword in query.lower():
            for category in categories:
                cat_products = get_products_by_category(category, per_page=5)
                products.extend(cat_products)
                if len(products) >= 10:
                    break
            break
    
    # Dacă nu găsește nimic, caută generic
    if not products:
        products = search_products(query, per_page=5)
    
    return products

def build_products_context(products: list) -> str:
    """
    Construiește context cu produse pentru AI
    
    Args:
        products: Listă produse
        
    Returns:
        String context
    """
    if not products:
        return ""
    
    context_lines = []
    
    for prod in products[:5]:
        line = f"- {prod['name']}: {format_price(prod['price'])}"
        
        if prod.get('stock_status') == 'instock':
            line += " ✅ Stoc disponibil"
        
        line += f" | Link: {prod['permalink']}"
        
        context_lines.append(line)
    
    return "\n".join(context_lines)

def generate_suggestions(user_message: str, ai_response: str) -> list:
    """
    Generează sugestii quick reply
    
    Args:
        user_message: Mesaj user
        ai_response: Răspuns AI
        
    Returns:
        Listă sugestii
    """
    suggestions = []
    
    # Sugestii bazate pe context
    if 'preț' in user_message.lower() or 'cost' in user_message.lower():
        suggestions.extend([
            "Vreau ofertă personalizată",
            "Care sunt opțiunile de plată?",
            "Aveți garanție?"
        ])
    elif 'filtr' in user_message.lower():
        suggestions.extend([
            "Cum se întreține filtrul?",
            "Ce material filtrant recomandați?",
            "Cât costă instalarea?"
        ])
    elif 'pompă' in user_message.lower():
        suggestions.extend([
            "Ce putere îmi trebuie?",
            "Consum energie electrică?",
            "Garanție pompă?"
        ])
    else:
        suggestions.extend([
            "Vreau să configurez o piscină",
            "Aveți livrare gratuită?",
            "Vreau să vorbesc cu specialist"
        ])
    
    return suggestions[:3]

def handler(request):
    """Vercel serverless function handler"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == '__main__':
    app.run(debug=True)
