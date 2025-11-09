# 🚀 Guía de Deploy a Producción

## 📋 Resumen del Sistema

Tienes **2 aplicaciones** que necesitas deployar:

1. **Backend (Python FastAPI)** - API del chatbot
2. **Frontend (React + Vite)** - Interfaz web

---

## 🎯 OPCIÓN 1: Deploy Completo (Recomendado)

### **Backend → Railway / Render**
### **Frontend → Vercel / Netlify**

---

## 🐍 PARTE 1: Deploy del Backend (Python API)

### **Opción A: Railway (Recomendado - Gratuito)**

#### **Paso 1: Preparar el proyecto**

Crea `runtime.txt` en el proyecto de Python:
```txt
python-3.11
```

Crea `Procfile`:
```
web: uvicorn api_chatbot:app --host 0.0.0.0 --port $PORT
```

#### **Paso 2: Deploy en Railway**

1. Ve a: https://railway.app/
2. Conecta con GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Selecciona tu repo del proyecto Python
5. Railway detectará automáticamente que es Python
6. Añade variables de entorno:
   ```
   GEMINI_API_KEY=AIzaSyB-kVZoo3TAxA5t97qFq_ii0ifeKus1r5k
   PORT=8000
   ```
7. Deploy automático

Te dará una URL como: `https://tu-proyecto.up.railway.app`

---

### **Opción B: Render (Gratuito con límites)**

1. Ve a: https://render.com/
2. Conecta con GitHub
3. "New +" → "Web Service"
4. Conecta tu repo
5. Configuración:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api_chatbot:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3.11
6. Variables de entorno:
   ```
   GEMINI_API_KEY=AIzaSyB-kVZoo3TAxA5t97qFq_ii0ifeKus1r5k
   ```

Te dará una URL como: `https://tu-proyecto.onrender.com`

---

### **Opción C: Heroku**

```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

cd "d:\curosor\ pojects\hackaton"

# Login
heroku login

# Crear app
heroku create nombre-tu-bot-api

# Configurar variable de entorno
heroku config:set GEMINI_API_KEY=AIzaSyB-kVZoo3TAxA5t97qFq_ii0ifeKus1r5k

# Deploy
git init  # si no existe
git add .
git commit -m "Deploy backend"
git push heroku master
```

---

## ⚛️ PARTE 2: Deploy del Frontend (React)

### **Opción A: Lovable (Más Fácil - Ya está configurado)**

Tu proyecto ya está en Lovable según el README:

1. Ve a: https://lovable.dev/projects/a8065e7d-8d1e-44ed-a0a6-5f0cba2e3d04
2. Click en **"Share"** → **"Publish"**
3. Añade variable de entorno en Settings:
   ```
   VITE_CHATBOT_API_URL=https://tu-backend.railway.app
   ```
4. Republica

Te dará un dominio como: `https://tu-proyecto.lovable.app`

---

### **Opción B: Vercel (Recomendado)**

```bash
# Instalar Vercel CLI
npm install -g vercel

cd "C:\Users\josea\OneDrive\Desktop\news-bot-drag-main"

# Login y deploy
vercel

# Añadir variable de entorno
vercel env add VITE_CHATBOT_API_URL
# Pegar: https://tu-backend.railway.app

# Deploy a producción
vercel --prod
```

Te dará: `https://tu-proyecto.vercel.app`

---

### **Opción C: Netlify**

```bash
# Instalar Netlify CLI
npm install -g netlify-cli

cd "C:\Users\josea\OneDrive\Desktop\news-bot-drag-main"

# Build
npm run build

# Login y deploy
netlify login
netlify deploy --prod

# Configurar variable en el dashboard
# VITE_CHATBOT_API_URL = https://tu-backend.railway.app
```

---

## 🔧 PARTE 3: Configuración Final

### **1. Actualizar CORS en el Backend**

Edita `api_chatbot.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "https://tu-proyecto.lovable.app",      # ← Tu dominio frontend
        "https://tu-proyecto.vercel.app",       # ← O Vercel
        "https://tu-dominio.com",               # ← Tu dominio custom
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Redeploy el backend después de cambiar esto.

---

### **2. Variables de Entorno en Producción**

**Backend (Railway/Render):**
```env
GEMINI_API_KEY=AIzaSyB-kVZoo3TAxA5t97qFq_ii0ifeKus1r5k
PORT=8000
```

**Frontend (Vercel/Lovable):**
```env
VITE_CHATBOT_API_URL=https://tu-backend.railway.app
VITE_SUPABASE_URL=[tu-url-existente]
VITE_SUPABASE_ANON_KEY=[tu-key-existente]
```

---

## 🌐 PARTE 4: Dominio Custom (Opcional)

### **Si quieres tu propio dominio (ejemplo: mibotfinanciero.com):**

1. **Compra un dominio** (GoDaddy, Namecheap, etc.)

2. **Configurar DNS:**

   **Para el frontend (Vercel/Lovable):**
   - Tipo: `CNAME`
   - Nombre: `@` o `www`
   - Valor: Tu dominio de Vercel/Lovable

   **Para el backend (Railway):**
   - Tipo: `CNAME`
   - Nombre: `api`
   - Valor: Tu dominio de Railway

3. **Resultado:**
   - Frontend: `https://mibotfinanciero.com`
   - Backend: `https://api.mibotfinanciero.com`

---

## ⚡ OPCIÓN RÁPIDA (5 Minutos)

Si quieres probarlo YA en internet:

### **1. Frontend con Lovable:**
```
1. Ve a tu proyecto Lovable
2. Click "Share" → "Publish"
3. Copia la URL que te da
```

### **2. Backend con Railway:**
```
1. railway.app → Login con GitHub
2. "New Project" → "Deploy from GitHub"
3. Selecciona tu repo
4. Añade GEMINI_API_KEY
5. Deploy automático
6. Copia la URL
```

### **3. Conectar ambos:**
```
1. En Lovable → Settings → Environment Variables
2. Añade: VITE_CHATBOT_API_URL = [URL de Railway]
3. Republish

4. En Railway → api_chatbot.py → Actualiza allow_origins
5. Añade la URL de Lovable
6. Redeploy
```

---

## 📊 Arquitectura en Producción

```
Usuario
  ↓
https://tu-proyecto.lovable.app (Frontend React)
  ↓ API REST
https://tu-bot-api.railway.app (Backend Python)
  ↓
Google Gemini API
  ↓
Análisis con Tokens + Alfa/Beta
```

---

## 💰 Costos Estimados

**Tier Gratuito (suficiente para empezar):**
- Railway: Gratis (500 horas/mes)
- Lovable: Gratis con límites
- Vercel: Gratis (100GB ancho de banda)
- Netlify: Gratis (100GB)
- Supabase: Gratis (500MB DB)
- **Gemini API:** ~$0.10 por 1000 análisis

**Total mensual inicial:** ~$0-5 USD

---

## 🎯 Recomendación Simple

**Para el hackathon/demo:**
1. **Backend:** Railway (gratis, fácil)
2. **Frontend:** Lovable (ya está ahí)
3. **Total tiempo:** 10-15 minutos

**Para producción real:**
1. **Backend:** Railway Pro o AWS
2. **Frontend:** Vercel Pro
3. **Dominio custom:** $10-15/año

---

¿Quieres que te ayude a hacer el deploy ahora mismo en Railway y Lovable? 🚀

