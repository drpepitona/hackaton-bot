# 📤 Guía: Subir Proyecto a GitHub

## ✅ Estado Actual
- ✓ Repositorio Git inicializado
- ✓ Archivos listos para commit
- ⏳ Falta configurar identidad y crear repo en GitHub

---

## 🎯 PASOS PARA SUBIR A GITHUB

### **Paso 1: Configurar Git (una sola vez)**

En tu terminal de PowerShell, ejecuta:

```bash
git config --global user.email "tu-email@gmail.com"
git config --global user.name "Tu Nombre"
```

**Ejemplo:**
```bash
git config --global user.email "jose@example.com"
git config --global user.name "Jose"
```

---

### **Paso 2: Hacer el Commit Inicial**

En tu terminal:

```bash
cd "d:\curosor\ pojects\hackaton"

git commit -m "Initial commit: Financial Analysis Bot with Gemini AI"
```

---

### **Paso 3: Crear Repositorio en GitHub**

1. **Ve a:** https://github.com/new

2. **Configura:**
   - Repository name: `financial-analysis-bot` (o el nombre que quieras)
   - Description: `Bot de análisis financiero con IA (Gemini) y parámetros Landau`
   - Visibility: **Public** (para que Railway/Vercel puedan acceder gratis)
   - ❌ NO marcar "Add a README file"
   - ❌ NO marcar "Add .gitignore"
   - ❌ NO marcar "Choose a license"

3. Click **"Create repository"**

4. **GitHub te mostrará comandos** - copia la segunda sección que dice:
   ```bash
   ...push an existing repository from the command line
   ```

---

### **Paso 4: Conectar con GitHub y Subir**

GitHub te dará comandos como estos (cópialos de TU página):

```bash
cd "d:\curosor\ pojects\hackaton"

git remote add origin https://github.com/TU-USUARIO/TU-REPO.git
git branch -M main
git push -u origin main
```

**Ejemplo real:**
```bash
git remote add origin https://github.com/joseperez/financial-analysis-bot.git
git branch -M main
git push -u origin main
```

Cuando ejecutes `git push`, te pedirá autenticación:
- **Usuario:** tu-usuario-github
- **Contraseña:** NO uses tu contraseña, usa un **Personal Access Token**

---

### **Paso 5: Crear Personal Access Token (si es necesario)**

Si git te pide contraseña:

1. Ve a: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Classic"**
3. Selecciona:
   - ✓ `repo` (todos los checkboxes)
   - Expiration: 90 days
4. Click **"Generate token"**
5. **COPIA EL TOKEN** (solo lo verás una vez)
6. Usa ese token como contraseña cuando hagas `git push`

---

## 🎯 COMANDOS COMPLETOS (COPIA Y PEGA)

Ejecuta estos comandos uno por uno en tu terminal:

```bash
# 1. Configurar identidad
git config --global user.email "tu-email@example.com"
git config --global user.name "Tu Nombre"

# 2. Navegar al proyecto
cd "d:\curosor\ pojects\hackaton"

# 3. Hacer commit
git commit -m "Initial commit: Financial Analysis Bot with Gemini AI"

# 4. Crear repo en GitHub (hazlo en el navegador)
# Ve a: https://github.com/new

# 5. Conectar con GitHub (reemplaza TU-USUARIO y TU-REPO)
git remote add origin https://github.com/TU-USUARIO/TU-REPO.git
git branch -M main
git push -u origin main
```

---

## ✅ Verificar que se subió

Después del push, ve a:
```
https://github.com/TU-USUARIO/TU-REPO
```

Deberías ver:
- ✓ README.md con la descripción
- ✓ api_chatbot.py
- ✓ bot_gemini_completo.py
- ✓ requirements.txt
- ✓ Carpeta src/
- ✓ Carpeta data/processed/landau/

---

## 🚀 DESPUÉS DE SUBIR A GITHUB

### **Deploy Inmediato (5 min):**

1. **Railway para el backend:**
   - Ve a: railway.app
   - "New Project" → "Deploy from GitHub repo"
   - Selecciona tu repo recién creado
   - Añade variable: `GEMINI_API_KEY`
   - Deploy automático
   - Copia la URL

2. **Lovable para el frontend:**
   - Ve a tu proyecto Lovable
   - Settings → Environment Variables
   - Añade: `VITE_CHATBOT_API_URL` = URL de Railway
   - Share → Publish

**¡LISTO!** Tu bot está en internet 🌍

---

## 💡 TIP: Mantener Actualizado

Después de hacer cambios:

```bash
cd "d:\curosor\ pojects\hackaton"
git add .
git commit -m "Descripción de los cambios"
git push
```

Railway/Render re-deployarán automáticamente.

---

¿Listo para ejecutar los comandos? Empieza con:
```bash
git config --global user.email "tu-email@gmail.com"
git config --global user.name "Tu Nombre"
```

