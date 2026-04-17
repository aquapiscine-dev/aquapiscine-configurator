# 🚀 Setup Guide - AquaPiscine Configurator

Ghid complet instalare și configurare.

## 📋 Cerințe

- WordPress 5.0+
- PHP 7.4+
- Cont Vercel (gratuit)
- Cont GitHub (gratuit)

## 🔧 Instalare Backend (Vercel)

### 1. Push cod pe GitHub

```bash
cd aquapiscine-configurator
git init
git add .
git commit -m "Initial commit - AquaPiscine Configurator"
git branch -M main
git remote add origin https://github.com/[username]/aquapiscine-configurator.git
git push -u origin main
```

### 2. Deploy pe Vercel

1. Mergi pe https://vercel.com
2. Sign up / Login
3. Click "New Project"
4. Import repository GitHub
5. Selectează `aquapiscine-configurator`
6. Root Directory: `backend`
7. Click "Deploy"

### 3. Configurează Environment Variables

În Vercel Dashboard → Settings → Environment Variables:

```
GROQ_API_KEY_1 = gsk_... (prima cheie Groq funcțională)
GROQ_API_KEY_2 = gsk_... (a doua cheie Groq funcțională)
WP_URL = https://aquapiscine.ro
WP_CONSUMER_KEY = ck_... (WooCommerce Consumer Key)
WP_CONSUMER_SECRET = cs_... (WooCommerce Consumer Secret)
```

**Nota:** Cheile reale le ai salvate separat pentru securitate.

### 4. Notează URL-ul API

După deploy, vei primi URL:
```
https://aquapiscine-configurator.vercel.app
```

API endpoints:
```
https://aquapiscine-configurator.vercel.app/api/configurator
https://aquapiscine-configurator.vercel.app/api/chat
https://aquapiscine-configurator.vercel.app/api/analyze_image
```

## 🎨 Instalare Frontend (WordPress)

### 1. Upload fișiere în tema WordPress

Via FTP sau cPanel File Manager:

```
wp-content/themes/[tema-ta]/configurator/
├── configurator.php
├── configurator.js
└── configurator.css
```

### 2. Modifică configurator.js

Linia 9, înlocuiește cu URL-ul tău Vercel:

```javascript
apiUrl: 'https://aquapiscine-configurator.vercel.app/api',
```

### 3. Adaugă în functions.php

Deschide `wp-content/themes/[tema-ta]/functions.php` și adaugă:

```php
// AquaPiscine Configurator
require_once get_template_directory() . '/configurator/configurator.php';
```

### 4. Creează pagină WordPress

1. WordPress Admin → Pagini → Adaugă pagină nouă
2. Titlu: "Configurator Piscine"
3. URL: `/configurator-piscine/`
4. Conținut: `[configurator_piscine]`
5. Publică

### 5. Testează

Vizitează: `https://aquapiscine.ro/configurator-piscine/`

## ✅ Verificare Funcționalitate

### Test 1: Conversație text

1. Deschide configurator
2. Scrie: "Vreau o piscină 8x4m"
3. Verifică răspuns AI
4. Verifică produse afișate

### Test 2: Upload imagine

1. Click buton 📸
2. Încarcă imagine grădină
3. Verifică analiză AI
4. Verifică recomandări

### Test 3: Calcul preț

1. Completează configurare
2. Verifică preț estimat
3. Verifică produse recomandate

## 🐛 Troubleshooting

### Eroare: "Failed to fetch"

**Cauză:** URL API incorect sau CORS

**Soluție:**
1. Verifică URL în `configurator.js`
2. Verifică că backend e deployed pe Vercel
3. Verifică console browser (F12)

### Eroare: "Groq API error"

**Cauză:** Chei API invalide sau rate limit

**Soluție:**
1. Verifică Environment Variables în Vercel
2. Verifică că cheile sunt corecte
3. Așteaptă 1 minut și încearcă din nou

### Eroare: "WooCommerce API error"

**Cauză:** Credențiale WooCommerce incorecte

**Soluție:**
1. Verifică Consumer Key și Secret în Vercel
2. Verifică că WooCommerce REST API e activ
3. Test: `https://aquapiscine.ro/wp-json/wc/v3/products`

### Shortcode nu funcționează

**Cauză:** Fișier PHP nu e inclus

**Soluție:**
1. Verifică că ai adăugat `require_once` în functions.php
2. Verifică calea către fișier
3. Reîncarcă pagina WordPress

## 📊 Monitoring

### Vercel Logs

Vercel Dashboard → Deployment → Logs

Vezi toate request-urile și erorile.

### WordPress Debug

Adaugă în `wp-config.php`:

```php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
```

Logs în: `wp-content/debug.log`

## 🔄 Update

### Update Backend

```bash
git add .
git commit -m "Update backend"
git push
```

Vercel va redeploy automat.

### Update Frontend

1. Modifică fișiere în `wp-content/themes/[tema]/configurator/`
2. Clear cache WordPress
3. Hard refresh browser (Ctrl+F5)

## 📞 Support

Probleme? Contact:
- Email: contact@aquapiscine.ro
- Telefon: 0772 286 246
