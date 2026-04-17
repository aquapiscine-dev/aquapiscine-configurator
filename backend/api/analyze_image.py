"""
Groq Vision API endpoint pentru analiză imagini teren
"""

from flask import Flask, request, jsonify
from utils import call_groq_vision, encode_image_to_base64, sanitize_user_input
import json

app = Flask(__name__)

ANALYSIS_PROMPT = """Analizează această imagine a grădinii/terenului pentru instalarea unei piscine.

Identifică și descrie:

1. DIMENSIUNI TEREN:
   - Suprafață totală disponibilă (estimare în m²)
   - Formă teren (dreptunghiular, L, neregulat, etc)
   - Spațiu util pentru piscină

2. CARACTERISTICI TEREN:
   - Tip teren: plan, ușor înclinat, foarte înclinat
   - Grad înclinare (dacă există)
   - Calitate sol vizibilă

3. OBSTACOLE ȘI VEGETAȚIE:
   - Copaci (număr, poziție, dimensiune)
   - Arbuști și plante
   - Construcții existente (casă, garaj, anexe)
   - Garduri, alei, pavaje

4. ORIENTARE ȘI EXPUNERE:
   - Zone însorite vs umbrite
   - Orientare optimă pentru piscină
   - Protecție vânt (dacă vizibilă)

5. ACCES:
   - Lățime poartă/intrare (pentru excavator)
   - Acces utilități (apă, curent - dacă vizibil)
   - Spațiu manevră echipamente

6. STIL GRĂDINĂ:
   - Modern, rustic, clasic, etc
   - Elemente decorative existente

RECOMANDĂRI:

1. DIMENSIUNE PISCINĂ:
   - Dimensiune optimă recomandată (ex: 8x4m, 10x5m)
   - Justificare bazată pe spațiu disponibil
   - Alternative (mai mică/mai mare)

2. TIP PISCINĂ:
   - Beton, fibră sticlă, sau liner
   - Justificare bazată pe teren și buget
   - Avantaje pentru acest teren specific

3. POZIȚIONARE:
   - Locație exactă recomandată
   - Justificare (soare, acces, estetică)
   - Distanță de casă și obstacole

4. COSTURI EXTRA:
   - Excavare (teren plan vs înclinat)
   - Îndepărtare vegetație
   - Amenajare acces
   - Estimare costuri (dacă posibil)

5. FINISAJE ȘI AMENAJARE:
   - Tip finisaj recomandat (mozaic, liner, etc)
   - Deck/pavaj recomandat
   - Amenajare peisagistică sugerată

Răspunde în limba română, clar și structurat. Fii specific și oferă cifre concrete unde e posibil."""

@app.route('/api/analyze_image', methods=['POST'])
def analyze_image():
    """
    Endpoint pentru analiză imagine teren cu Groq Vision
    
    Request:
        - image: File (multipart/form-data)
        - additional_info: String (opțional) - info suplimentară de la user
        
    Response:
        {
            "success": true,
            "analysis": {
                "terrain": {...},
                "recommendations": {...},
                "estimated_costs": {...}
            },
            "raw_response": "..."
        }
    """
    try:
        # Verifică dacă există imagine
        if 'image' not in request.files:
            return jsonify({
                "success": False,
                "error": "Nu a fost încărcată nicio imagine"
            }), 400
        
        image_file = request.files['image']
        
        # Verifică tip fișier
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
        file_ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                "success": False,
                "error": f"Tip fișier invalid. Permise: {', '.join(allowed_extensions)}"
            }), 400
        
        # Citește și encodează imagine
        image_bytes = image_file.read()
        
        # Verifică dimensiune (max 10MB)
        if len(image_bytes) > 10 * 1024 * 1024:
            return jsonify({
                "success": False,
                "error": "Imagine prea mare. Maxim 10MB."
            }), 400
        
        image_base64 = encode_image_to_base64(image_bytes)
        
        # Info suplimentară de la user (opțional)
        additional_info = request.form.get('additional_info', '')
        if additional_info:
            additional_info = sanitize_user_input(additional_info)
            prompt = f"{ANALYSIS_PROMPT}\n\nINFORMATII SUPLIMENTARE DE LA CLIENT:\n{additional_info}"
        else:
            prompt = ANALYSIS_PROMPT
        
        # Apel Groq Vision
        analysis_text = call_groq_vision(image_base64, prompt)
        
        # Parse răspuns AI în structură
        parsed_analysis = parse_analysis_response(analysis_text)
        
        return jsonify({
            "success": True,
            "analysis": parsed_analysis,
            "raw_response": analysis_text
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Eroare analiză imagine: {str(e)}"
        }), 500

def parse_analysis_response(analysis_text: str) -> dict:
    """
    Parsează răspuns AI în structură
    
    Args:
        analysis_text: Răspuns raw de la Groq Vision
        
    Returns:
        Dict structurat cu analiză
    """
    import re
    
    parsed = {
        "terrain": {
            "area": extract_area(analysis_text),
            "shape": extract_shape(analysis_text),
            "slope": extract_slope(analysis_text),
            "obstacles": extract_obstacles(analysis_text)
        },
        "recommendations": {
            "pool_size": extract_pool_size(analysis_text),
            "pool_type": extract_pool_type(analysis_text),
            "position": extract_position(analysis_text),
            "finishes": extract_finishes(analysis_text)
        },
        "estimated_costs": {
            "excavation": extract_excavation_cost(analysis_text),
            "total_extra": extract_total_extra_cost(analysis_text)
        },
        "summary": extract_summary(analysis_text)
    }
    
    return parsed

def extract_area(text: str) -> str:
    """Extrage suprafață teren"""
    match = re.search(r'(\d+[-~]?\d*)\s*m[²2]', text)
    return match.group(0) if match else "Nedeterminat"

def extract_shape(text: str) -> str:
    """Extrage formă teren"""
    shapes = ['dreptunghiular', 'pătrat', 'L', 'neregulat', 'trapezoid']
    for shape in shapes:
        if shape.lower() in text.lower():
            return shape.capitalize()
    return "Nedeterminat"

def extract_slope(text: str) -> str:
    """Extrage înclinare teren"""
    if 'plan' in text.lower() and 'înclinat' not in text.lower():
        return "Plan"
    elif 'ușor înclinat' in text.lower():
        return "Ușor înclinat"
    elif 'foarte înclinat' in text.lower() or 'puternic înclinat' in text.lower():
        return "Foarte înclinat"
    return "Nedeterminat"

def extract_obstacles(text: str) -> list:
    """Extrage obstacole"""
    obstacles = []
    if 'copac' in text.lower():
        obstacles.append("Copaci")
    if 'arbuști' in text.lower() or 'plante' in text.lower():
        obstacles.append("Vegetație")
    if 'construcț' in text.lower():
        obstacles.append("Construcții")
    return obstacles if obstacles else ["Fără obstacole majore"]

def extract_pool_size(text: str) -> str:
    """Extrage dimensiune recomandată piscină"""
    match = re.search(r'(\d+)\s*[xX×]\s*(\d+)\s*m', text)
    return match.group(0) if match else "8x4m (recomandat)"

def extract_pool_type(text: str) -> str:
    """Extrage tip piscină recomandat"""
    types = ['beton', 'fibră sticlă', 'liner']
    for pool_type in types:
        if pool_type.lower() in text.lower():
            return pool_type.title()
    return "Fibră sticlă"

def extract_position(text: str) -> str:
    """Extrage poziționare recomandată"""
    positions = ['centru', 'dreapta', 'stânga', 'fund', 'față']
    for pos in positions:
        if pos in text.lower():
            return pos.capitalize()
    return "Centru grădină"

def extract_finishes(text: str) -> str:
    """Extrage finisaje recomandate"""
    if 'mozaic' in text.lower():
        return "Mozaic"
    elif 'liner' in text.lower():
        return "Liner PVC"
    return "Mozaic sau liner"

def extract_excavation_cost(text: str) -> str:
    """Extrage cost excavare"""
    match = re.search(r'(\d+[.,]?\d*)\s*(?:EUR|RON|lei)', text)
    if match:
        return match.group(0)
    
    # Estimare bazată pe înclinare
    if 'foarte înclinat' in text.lower():
        return "8.000-10.000 EUR"
    elif 'ușor înclinat' in text.lower():
        return "5.000-7.000 EUR"
    elif 'plan' in text.lower():
        return "3.000-5.000 EUR"
    
    return "5.000-8.000 EUR (estimare)"

def extract_total_extra_cost(text: str) -> str:
    """Extrage costuri extra totale"""
    match = re.search(r'total.*?(\d+[.,]?\d*)\s*(?:EUR|RON|lei)', text, re.IGNORECASE)
    return match.group(1) + " EUR" if match else "Nedeterminat"

def extract_summary(text: str) -> str:
    """Extrage rezumat scurt"""
    lines = text.split('\n')
    summary_lines = []
    
    for line in lines[:10]:
        if line.strip() and not line.strip().startswith('#'):
            summary_lines.append(line.strip())
            if len(summary_lines) >= 3:
                break
    
    return ' '.join(summary_lines) if summary_lines else text[:200]

if __name__ == '__main__':
    app.run(debug=True)
