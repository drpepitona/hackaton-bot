# 🌍 DEPLOY PARA EL MUNDO - Guía Completa

## 🎯 Objetivo
Hacer que tu bot esté disponible en internet para que CUALQUIER persona pueda usarlo desde cualquier país.

---

## 📋 LO QUE TIENES QUE HACER

### RESUMEN EJECUTIVO (15 minutos)

```
1. Subir BACKEND a Railway     → 5 min
2. Subir FRONTEND a Lovable     → 5 min  
3. Conectar ambos               → 5 min
4. (Opcional) Dominio custom    → 10 min extra
```

**Resultado:** Tu bot accesible desde cualquier parte del mundo 24/7

---

## 🚀 PASO 1: Deploy del Backend (Python)

### **Usar Railway (GRATIS y FÁCIL)**

#### **A. Preparar archivos (YA CASI LISTO)**

1. En tu proyecto Python, crea estos archivos:

**`Procfile`** (para Railway):
```
web: uvicorn api_chatbot:app --host 0.0.0.0 --port $PORT
```

**`runtime.txt`** (opcional):
```
python-3.11
```

**`requirements.txt`** (ya lo tienes, verificar que tenga):
```
fastapi==0.104.1
uvicorn==0.24.0
google-generativeai==0.3.0
pandas==2.0.3
# ... demás dependencias
```

#### **B. Subir a Railway**

1. **Ve a:** https://railway.app/
2. Click **"Login"** → **"Login with GitHub"**
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Selecciona tu repositorio del hackaton
5. Railway detectará automáticamente Python
6. Click **"Deploy"**

#### **C. Configurar Variables de Entorno**

En Railway, ve a tu proyecto:
1. Click en **"Variables"**
2. Añade estas variables:
   ```
   GEMINI_API_KEY=AIzaSyB-kVZoo3TAxA5t97qFq_ii0ifeKus1r5k
   PORT=8000
   ```
3. Click **"Save"**

#### **D. Obtener URL del Backend**

Railway te dará una URL tipo:
```
https://tu-proyecto-production.up.railway.app
```

**¡GUARDA ESTA URL!** La necesitarás para el frontend.

---

## 🎨 PASO 2: Deploy del Frontend (React)

### **Opción A: Lovable (MÁS FÁCIL - Ya está configurado)**

Tu proyecto YA ESTÁ en Lovable según tu README:

1. **Ve a:** https://lovable.dev/projects/a8065e7d-8d1e-44ed-a0a6-5f0cba2e3d04

2. **Settings → Environment Variables:**
   - Click **"Add Variable"**
   - Nombre: `VITE_CHATBOT_API_URL`
   - Valor: `https://tu-proyecto-production.up.railway.app` (la URL de Railway)
   - Click **"Save"**

3. **Click "Share" → "Publish"**

4. Lovable te dará una URL tipo:
   ```
   https://a8065e7d-8d1e-44ed-a0a6-5f0cba2e3d04.lovableproject.com
   ```

---

### **Opción B: Vercel (Alternativa Popular)**

```bash
# Instalar Vercel CLI
npm install -g vercel

# En tu proyecto React
cd "C:\Users\josea\OneDrive\Desktop\news-bot-drag-main"

# Login
vercel login

# Deploy
vercel

# Añadir variable de entorno
vercel env add VITE_CHATBOT_API_URL production
# Pegar: https://tu-proyecto-production.up.railway.app

# Deploy final
vercel --prod
```

Te dará: `https://tu-proyecto.vercel.app`

---

## 🔗 PASO 3: Conectar Backend ↔ Frontend

### **A. Actualizar CORS en el Backend**

Edita `api_chatbot.py` en tu repo:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "https://a8065e7d-8d1e-44ed-a0a6-5f0cba2e3d04.lovableproject.com",  # ← Tu URL de Lovable
        "https://tu-proyecto.vercel.app",  # ← O tu URL de Vercel
        # Añade tu dominio custom aquí si lo tienes
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **B. Hacer commit y push**

```bash
git add api_chatbot.py
git commit -m "Update CORS for production"
git push
```

Railway/Render re-deployará automáticamente.

---

## 🌐 PASO 4: Dominio Custom (Opcional)

Si quieres un dominio como `mibotfinanciero.com`:

### **A. Comprar Dominio**

Sitios recomendados:
- **Namecheap:** $8-12/año
- **GoDaddy:** $10-15/año
- **Google Domains:** $12/año

### **B. Configurar DNS**

En tu proveedor de dominio, añade estos registros:

**Para Frontend:**
```
Tipo: CNAME
Nombre: www
Valor: cname.vercel-dns.com  (si usas Vercel)
```

**Para Backend:**
```
Tipo: CNAME
Nombre: api
Valor: tu-proyecto.up.railway.app
```

### **C. Configurar en las plataformas**

**En Vercel/Lovable:**
- Settings → Domains → Add Domain
- Añade: `www.mibotfinanciero.com`

**En Railway:**
- Settings → Domains → Add Domain
- Añade: `api.mibotfinanciero.com`

### **D. Resultado Final:**

```
Frontend: https://www.mibotfinanciero.com
Backend:  https://api.mibotfinanciero.com
```

---

## ⚡ OPCIÓN MÁS RÁPIDA (SIN DOMINIO CUSTOM)

### **Deploy en 15 minutos:**

#### **1. Backend → Railway**
```bash
1. railway.app → Login GitHub
2. New Project → From GitHub
3. Selecciona repo
4. Add variable: GEMINI_API_KEY
5. Deploy
6. Copia URL: https://xxx.railway.app
```

#### **2. Frontend → Lovable**
```bash
1. lovable.dev → Tu proyecto
2. Settings → Env Variables
3. VITE_CHATBOT_API_URL = https://xxx.railway.app
4. Share → Publish
5. Copia URL
```

#### **3. Actualizar CORS**
```bash
1. Edita api_chatbot.py
2. Añade URL de Lovable en allow_origins
3. Git push
4. Railway redeploy automático
```

**¡LISTO!** Tu bot está en línea 🌍

---

## 📊 Arquitectura Final

```
Usuario desde CUALQUIER PAÍS
         ↓
https://tu-proyecto.lovable.app (Frontend)
         ↓ HTTPS
https://tu-bot.railway.app (Backend API)
         ↓ HTTPS
Google Gemini API
         ↓
Base de datos con 123k noticias + Alfa/Beta
         ↓
Análisis financiero + Recomendación
         ↓
RESPUESTA al usuario
```

---

## 💰 Costos

### **Tier Gratuito (suficiente para empezar):**
```
Railway:  500 horas/mes gratis = ~$0
Lovable:  Hosting gratis = $0
Vercel:   100GB tráfico = $0
Gemini:   ~1000 análisis/día = $3/mes
──────────────────────────────────
TOTAL:    ~$3/mes (solo Gemini API)
```

### **Si crece mucho (1000+ usuarios/día):**
```
Railway Pro:   $20/mes
Vercel Pro:    $20/mes
Gemini API:    $50-100/mes
Dominio:       $1/mes
──────────────────────────────────
TOTAL:         ~$100/mes
```

---

## 🛡️ Seguridad

### **Proteger tu API Key:**

**NUNCA** pongas la API key en el frontend. Ya está bien:
- ✅ API Key en el backend (seguro)
- ✅ Frontend solo hace requests HTTP
- ✅ Usuario nunca ve la key

### **Rate Limiting (opcional):**

Añade a `api_chatbot.py`:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("10/minute")  # Máximo 10 requests por minuto
async def analyze_news(...):
    ...
```

---

## 📝 CHECKLIST FINAL

Antes de compartir tu URL:

- [ ] Backend funcionando: `https://xxx.railway.app/health`
- [ ] Frontend carga: `https://xxx.lovable.app`
- [ ] Chat funciona (escribe pregunta → recibe respuesta)
- [ ] CORS configurado correctamente
- [ ] Variables de entorno configuradas
- [ ] Gemini API responde (no error 429)
- [ ] Análisis muestra tokens, alfa, beta
- [ ] Filtra preguntas irrelevantes

---

## 🎉 SIGUIENTE PASO

¿Quieres que te ayude a:

1. **Subir a Railway YA** (15 min)
2. **Configurar dominio custom** (si ya tienes uno)
3. **Optimizar para producción** (caché, rate limits, etc.)
4. **Crear documentación para usuarios**

¿Qué prefieres? 🚀

