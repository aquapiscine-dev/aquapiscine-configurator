"""
Utility functions pentru AquaPiscine Configurator
"""

import os
import random
import base64
from typing import Dict, List, Optional
from groq import Groq

# Groq API Keys (rotație automată)
# Keys sunt în environment variables pentru securitate
GROQ_API_KEYS = [
    os.getenv('GROQ_API_KEY_1'),
    os.getenv('GROQ_API_KEY_2')
]

def get_groq_client() -> Groq:
    """Returnează client Groq cu cheie aleatorie"""
    api_key = random.choice(GROQ_API_KEYS)
    return Groq(api_key=api_key)

def call_groq_text(messages: List[Dict], model: str = "llama-3.3-70b-versatile", max_tokens: int = 2000) -> str:
    """
    Apel Groq API pentru text
    
    Args:
        messages: Lista mesaje conversație
        model: Model Groq
        max_tokens: Tokens maxime răspuns
        
    Returns:
        Răspuns AI
    """
    try:
        client = get_groq_client()
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Retry cu alt key
        try:
            client = get_groq_client()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as retry_error:
            raise Exception(f"Groq API error: {str(retry_error)}")

def call_groq_vision(image_base64: str, prompt: str, model: str = "llama-3.2-90b-vision-preview") -> str:
    """
    Apel Groq Vision API pentru analiză imagini
    
    Args:
        image_base64: Imagine encodată base64
        prompt: Prompt pentru analiză
        model: Model Vision
        
    Returns:
        Analiză AI
    """
    try:
        client = get_groq_client()
        
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        }]
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Retry cu alt key
        try:
            client = get_groq_client()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as retry_error:
            raise Exception(f"Groq Vision API error: {str(retry_error)}")

def encode_image_to_base64(image_bytes: bytes) -> str:
    """
    Encodează imagine în base64
    
    Args:
        image_bytes: Bytes imagine
        
    Returns:
        String base64
    """
    return base64.b64encode(image_bytes).decode('utf-8')

def format_price(price: float) -> str:
    """
    Formatează preț în RON
    
    Args:
        price: Preț numeric
        
    Returns:
        Preț formatat (ex: "16.790 RON")
    """
    return f"{price:,.0f} RON".replace(",", ".")

def validate_conversation_id(conversation_id: Optional[str]) -> str:
    """
    Validează sau generează conversation ID
    
    Args:
        conversation_id: ID conversație existent
        
    Returns:
        ID conversație valid
    """
    if conversation_id and len(conversation_id) > 0:
        return conversation_id
    
    import uuid
    return str(uuid.uuid4())

def sanitize_user_input(user_input: str) -> str:
    """
    Curăță input utilizator
    
    Args:
        user_input: Input brut
        
    Returns:
        Input curățat
    """
    if not user_input:
        return ""
    
    # Remove leading/trailing whitespace
    cleaned = user_input.strip()
    
    # Limit length
    if len(cleaned) > 1000:
        cleaned = cleaned[:1000]
    
    return cleaned

def extract_dimensions_from_text(text: str) -> Optional[Dict[str, float]]:
    """
    Extrage dimensiuni piscină din text
    
    Args:
        text: Text utilizator (ex: "8x4m", "10 pe 5 metri")
        
    Returns:
        Dict cu lungime și lățime sau None
    """
    import re
    
    # Pattern: 8x4, 8 x 4, 8x4m, 8 pe 4, etc
    patterns = [
        r'(\d+)\s*[xX×]\s*(\d+)',
        r'(\d+)\s+pe\s+(\d+)',
        r'(\d+)\s*[/]\s*(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            length = float(match.group(1))
            width = float(match.group(2))
            return {
                'length': length,
                'width': width,
                'area': length * width
            }
    
    return None

def calculate_pool_volume(length: float, width: float, depth: float = 1.5) -> float:
    """
    Calculează volumul piscine
    
    Args:
        length: Lungime (m)
        width: Lățime (m)
        depth: Adâncime medie (m)
        
    Returns:
        Volum (m³)
    """
    return length * width * depth

def get_recommended_equipment_size(volume: float, equipment_type: str) -> Dict:
    """
    Recomandă dimensiune echipament bazat pe volum
    
    Args:
        volume: Volum piscină (m³)
        equipment_type: Tip echipament (filtration, heating, etc)
        
    Returns:
        Dict cu recomandări
    """
    recommendations = {}
    
    if equipment_type == 'filtration':
        # Flow rate = volum / 4 ore
        flow_rate = volume / 4
        recommendations = {
            'flow_rate': flow_rate,
            'recommended_size': f"{flow_rate:.1f} m³/h",
            'description': f"Pentru {volume}m³, recomandăm pompă filtrare {flow_rate:.1f} m³/h"
        }
    
    elif equipment_type == 'heating':
        # 1 kW per 5m³
        power = volume / 5
        recommendations = {
            'power': power,
            'recommended_size': f"{power:.1f} kW",
            'description': f"Pentru {volume}m³, recomandăm pompă căldură {power:.1f} kW"
        }
    
    return recommendations
