# 🏊 AquaPiscine Configurator AI

Configurator inteligent de piscine cu AI (Groq) și integrare WooCommerce.

## 🎯 Features

### Configurator Piscine
- 💬 Conversație naturală cu AI (ca ChatGPT)
- 📸 Analiză imagini teren cu Groq Vision
- 🛒 Integrare WooCommerce (produse + prețuri reale)
- 💰 Calcul preț dinamic
- 📄 Generare ofertă PDF
- 📧 Trimitere email automat

### Chat Support AI
- 🤖 Asistent vânzări 24/7
- 🔍 Căutare inteligentă produse
- 💡 Recomandări personalizate
- 🔗 Link-uri directe produse
- 📊 Preview produse în chat

## 🏗️ Arhitectură

```
┌─────────────────────────────────────┐
│  WordPress (Shared Hosting)         │
│  Frontend: HTML/CSS/JavaScript      │
└─────────────────────────────────────┘
            ↓ HTTPS
┌─────────────────────────────────────┐
│  Backend API (Vercel Serverless)    │
│  Python + Groq AI + WooCommerce     │
└─────────────────────────────────────┘
```

## 📁 Structură Proiect

```
aquapiscine-configurator/
├── backend/                 # Python API (Vercel)
│   ├── api/
│   │   ├── chat.py         # Chat support endpoint
│   │   ├── configurator.py # Configurator endpoint
│   │   ├── analyze_image.py # Groq Vision
│   │   ├── woocommerce.py  # WooCommerce API
│   │   └── utils.py        # Helper functions
│   ├── requirements.txt
│   ├── vercel.json
│   └── README.md
│
├── frontend/               # WordPress integration
│   ├── configurator/
│   │   ├── configurator.php
│   │   ├── configurator.js
│   │   └── configurator.css
│   ├── chat-widget/
│   │   ├── chat-widget.php
│   │   ├── chat-widget.js
│   │   └── chat-widget.css
│   └── README.md
│
└── docs/                   # Documentație
    ├── SETUP.md
    ├── API.md
    └── WORDPRESS.md
```

## 🚀 Quick Start

### Backend (Vercel)

1. Clone repo
2. Deploy pe Vercel
3. Configurează environment variables

### Frontend (WordPress)

1. Upload fișiere în tema WordPress
2. Activează shortcode `[configurator_piscine]`
3. Adaugă chat widget în footer

## 🔑 Environment Variables

```
GROQ_API_KEY_1=gsk_...
GROQ_API_KEY_2=gsk_...
WP_URL=https://aquapiscine.ro
WP_CONSUMER_KEY=ck_...
WP_CONSUMER_SECRET=cs_...
```

## 📊 Tech Stack

- **Backend:** Python 3.11, Flask
- **AI:** Groq (Llama 3.3 + Vision)
- **E-commerce:** WooCommerce REST API
- **Deploy:** Vercel Serverless
- **Frontend:** Vanilla JavaScript
- **CMS:** WordPress

## 📝 License

MIT

## 👨‍💻 Author

AquaPiscine.ro - 2026
