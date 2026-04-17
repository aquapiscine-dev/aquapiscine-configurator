# Backend API - AquaPiscine Configurator

Backend Python pentru configurator piscine și chat support cu Groq AI.

## � Support

Probleme? Contact:
- Email: contact@aquapiscine.ro
- Telefon: 0772 286 246

## �🚀 Endpoints

### 1. `/api/configurator` - Configurator Conversațional

**POST** Request:
```json
{
  "message": "Vreau o piscină 8x4m",
  "conversation_id": "uuid-optional",
  "context": {}
}
```

**Response:**
```json
{
  "success": true,
  "response": "Perfect! Piscină 8x4m...",
  "conversation_id": "uuid",
  "products": [...],
  "estimated_price": 35000,
  "next_step": "pool_type",
  "config": {...}
}
```

### 2. `/api/chat` - Chat Support

**POST** Request:
```json
{
  "message": "Cât costă o pompă de căldură?",
  "conversation_id": "uuid-optional"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Am găsit mai multe pompe...",
  "conversation_id": "uuid",
  "products": [...],
  "suggestions": ["Vreau ofertă", "Ce putere?", ...]
}
```

### 3. `/api/analyze_image` - Analiză Imagine Teren

**POST** Request (multipart/form-data):
```
image: File
additional_info: String (optional)
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "terrain": {...},
    "recommendations": {...},
    "estimated_costs": {...}
  },
  "raw_response": "..."
}
```

## 🔧 Setup Local

```bash
# Install dependencies
pip install -r requirements.txt

# Run API
python api/configurator.py
```

## 📦 Deploy Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## 🔑 Environment Variables

Configurează în Vercel Dashboard:

```
GROQ_API_KEY_1=gsk_...
GROQ_API_KEY_2=gsk_...
WP_URL=https://aquapiscine.ro
WP_CONSUMER_KEY=ck_...
WP_CONSUMER_SECRET=cs_...
```

## 📊 Tech Stack

- Python 3.11
- Flask (API framework)
- Groq AI (Llama 3.3 + Vision)
- WooCommerce REST API
- Vercel Serverless Functions

## 🧪 Testing

```bash
# Test configurator
curl -X POST http://localhost:5000/api/configurator \
  -H "Content-Type: application/json" \
  -d '{"message": "Vreau piscină 8x4m"}'

# Test chat
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Cât costă o pompă?"}'

# Test image analysis
curl -X POST http://localhost:5000/api/analyze_image \
  -F "image=@gradina.jpg"
```
