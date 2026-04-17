"""
WooCommerce API Integration pentru AquaPiscine
"""

import requests
from typing import List, Dict, Optional
from requests.auth import HTTPBasicAuth

# WooCommerce credentials
WP_URL = "https://aquapiscine.ro/wp-json/wc/v3"
CONSUMER_KEY = "ck_ba954e8a9950d49d532551881dbf913c0f387f75"
CONSUMER_SECRET = "cs_a62ac74188b15e0ac2a6141d4842ee5a1f62aea3"

def search_products(query: str, category: Optional[str] = None, per_page: int = 10) -> List[Dict]:
    """
    Caută produse în WooCommerce
    
    Args:
        query: Termen căutare
        category: Categorie (opțional)
        per_page: Număr rezultate
        
    Returns:
        Listă produse
    """
    try:
        params = {
            "search": query,
            "per_page": per_page,
            "status": "publish",
            "stock_status": "instock"
        }
        
        if category:
            # Get category ID
            cat_id = get_category_id(category)
            if cat_id:
                params["category"] = cat_id
        
        response = requests.get(
            f"{WP_URL}/products",
            auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET),
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            products = response.json()
            return format_products(products)
        
        return []
        
    except Exception as e:
        print(f"Error searching products: {e}")
        return []

def get_product_by_id(product_id: int) -> Optional[Dict]:
    """
    Obține produs după ID
    
    Args:
        product_id: ID produs
        
    Returns:
        Dict produs sau None
    """
    try:
        response = requests.get(
            f"{WP_URL}/products/{product_id}",
            auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET),
            timeout=10
        )
        
        if response.status_code == 200:
            product = response.json()
            return format_product(product)
        
        return None
        
    except Exception as e:
        print(f"Error getting product: {e}")
        return None

def get_products_by_category(category_slug: str, per_page: int = 20) -> List[Dict]:
    """
    Obține produse dintr-o categorie
    
    Args:
        category_slug: Slug categorie
        per_page: Număr produse
        
    Returns:
        Listă produse
    """
    try:
        cat_id = get_category_id(category_slug)
        if not cat_id:
            return []
        
        params = {
            "category": cat_id,
            "per_page": per_page,
            "status": "publish",
            "stock_status": "instock"
        }
        
        response = requests.get(
            f"{WP_URL}/products",
            auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET),
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            products = response.json()
            return format_products(products)
        
        return []
        
    except Exception as e:
        print(f"Error getting category products: {e}")
        return []

def get_category_id(category_slug: str) -> Optional[int]:
    """
    Obține ID categorie după slug
    
    Args:
        category_slug: Slug categorie
        
    Returns:
        ID categorie sau None
    """
    # Mapping categorii comune
    category_map = {
        "piscine": 165,
        "piscine-fibra": 167,
        "piscine-supratera ne": 166,
        "filtrare": 171,
        "pompe-caldura": 195,
        "incalzire": 192,
        "iluminare": 188,
        "tratare": 179,
        "acoperire": 199,
        "aspiratoare": 169
    }
    
    return category_map.get(category_slug.lower())

def format_product(product: Dict) -> Dict:
    """
    Formatează produs pentru răspuns
    
    Args:
        product: Produs WooCommerce raw
        
    Returns:
        Produs formatat
    """
    return {
        "id": product.get("id"),
        "name": product.get("name"),
        "price": float(product.get("price", 0)),
        "regular_price": float(product.get("regular_price", 0)),
        "sale_price": float(product.get("sale_price", 0)) if product.get("sale_price") else None,
        "description": product.get("short_description", ""),
        "image": product.get("images", [{}])[0].get("src") if product.get("images") else None,
        "permalink": product.get("permalink"),
        "stock_status": product.get("stock_status"),
        "stock_quantity": product.get("stock_quantity"),
        "categories": [cat.get("name") for cat in product.get("categories", [])],
        "attributes": {attr.get("name"): attr.get("options") for attr in product.get("attributes", [])}
    }

def format_products(products: List[Dict]) -> List[Dict]:
    """
    Formatează listă produse
    
    Args:
        products: Listă produse WooCommerce raw
        
    Returns:
        Listă produse formatate
    """
    return [format_product(p) for p in products]

def get_recommended_products(pool_type: str, pool_volume: float) -> Dict[str, List[Dict]]:
    """
    Obține produse recomandate pentru configurație piscină
    
    Args:
        pool_type: Tip piscină (beton, fibra, liner)
        pool_volume: Volum piscină (m³)
        
    Returns:
        Dict cu categorii produse recomandate
    """
    recommendations = {
        "pool": [],
        "filtration": [],
        "heating": [],
        "lighting": [],
        "cleaning": [],
        "cover": []
    }
    
    # Piscină
    if pool_type == "fibra":
        recommendations["pool"] = get_products_by_category("piscine-fibra", per_page=5)
    
    # Filtrare (obligatoriu)
    filtration_products = get_products_by_category("filtrare", per_page=10)
    # Filtrează după volum (flow rate)
    required_flow = pool_volume / 4
    recommendations["filtration"] = [
        p for p in filtration_products 
        if required_flow * 0.8 <= extract_flow_rate(p) <= required_flow * 1.5
    ][:3]
    
    # Încălzire
    heating_products = get_products_by_category("pompe-caldura", per_page=10)
    required_power = pool_volume / 5
    recommendations["heating"] = [
        p for p in heating_products
        if required_power * 0.8 <= extract_power(p) <= required_power * 1.5
    ][:3]
    
    # Iluminare
    recommendations["lighting"] = get_products_by_category("iluminare", per_page=5)
    
    # Curățare
    recommendations["cleaning"] = get_products_by_category("aspiratoare", per_page=5)
    
    # Acoperire
    recommendations["cover"] = get_products_by_category("acoperire", per_page=5)
    
    return recommendations

def extract_flow_rate(product: Dict) -> float:
    """
    Extrage flow rate din nume/descriere produs
    
    Args:
        product: Produs
        
    Returns:
        Flow rate (m³/h)
    """
    import re
    
    text = f"{product.get('name', '')} {product.get('description', '')}"
    
    # Pattern: 10m³/h, 10 m3/h, etc
    match = re.search(r'(\d+(?:\.\d+)?)\s*m[³3]/h', text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    
    return 0.0

def extract_power(product: Dict) -> float:
    """
    Extrage putere din nume/descriere produs
    
    Args:
        product: Produs
        
    Returns:
        Putere (kW)
    """
    import re
    
    text = f"{product.get('name', '')} {product.get('description', '')}"
    
    # Pattern: 15kW, 15 kW, 15.5kW, etc
    match = re.search(r'(\d+(?:\.\d+)?)\s*kW', text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    
    return 0.0
