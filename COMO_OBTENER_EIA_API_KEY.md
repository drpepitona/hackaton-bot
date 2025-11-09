# 🔑 Cómo Obtener tu EIA API Key (GRATIS - 2 minutos)

## ¿Para qué la necesitas?

La **EIA (U.S. Energy Information Administration)** proporciona datos de:
- ⛽ Gas Natural
- 🛢️ Petróleo adicional
- ⚡ Energía
- 💰 Precios de commodities energéticos

Estos datos son **CRUCIALES** para predecir movimientos de mercado.

---

## 📋 Paso a Paso (2 minutos)

### **PASO 1: Ir al sitio de registro**

Abre este link en tu navegador:
```
https://www.eia.gov/opendata/register.php
```

### **PASO 2: Llenar el formulario**

El formulario es MUY simple:

```
First Name:     [Tu nombre]
Last Name:      [Tu apellido]  
Email:          [Tu email]
Organization:   [Puedes poner "Personal" o "Student"]
Affiliation:    [Selecciona "Other" o "Student"]
```

### **PASO 3: Aceptar términos**

✅ Marca la casilla: "I agree to the Terms of Service"

### **PASO 4: Enviar**

Click en **"Register"**

### **PASO 5: Revisar tu email**

📧 Recibirás un email INMEDIATAMENTE con tu API key

El email se verá así:
```
Subject: EIA Open Data API Key

Your API key is: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

Thank you for registering for the EIA Open Data API.
```

---

## 🔧 Configurar tu API Key

### **Opción 1: Archivo .env (Recomendado)**

1. Abre el archivo `.env` en la raíz del proyecto
2. Agrega esta línea:
   ```
   EIA_API_KEY=tu_key_aqui
   ```

3. Guarda el archivo

### **Opción 2: Configuración manual**

Edita: `src/utils/config.py`

```python
# Agregar esta línea
EIA_API_KEY = os.getenv("EIA_API_KEY", "tu_key_aqui")
```

---

## ✅ Verificar que funciona

Ejecuta:
```bash
py src/data_collection/eia_gas_collector.py
```

Si funciona verás:
```
✓ Datos obtenidos: XXX registros
✓ Dataset procesado guardado
```

---

## 📊 ¿Qué datos obtendrás?

Con la EIA API Key podrás obtener:

### **Gas Natural:**
- Producción mensual USA
- Precios spot
- Almacenamiento
- Importaciones/Exportaciones
- Consumo por sector

### **Petróleo (adicional a FRED):**
- Inventarios semanales
- Producción por región
- Capacidad de refinerías
- Demanda por producto

### **Otros:**
- Carbón
- Electricidad
- Energías renovables

---

## 🎯 Importancia para tu IA

Los datos de energía son **CRÍTICOS** porque:

1. 🛢️ **Gas natural = Electricidad** → Afecta costos industriales
2. ⛽ **Precios de energía** → Impulsan inflación
3. 📈 **Sector energético** → ~10% del S&P 500
4. 🌍 **Geopolítica** → Eventos globales afectan precios
5. 💰 **Trading de commodities** → Alta correlación con mercados

---

## ⏱️ Límites de la API (Generosos)

- ✅ **GRATIS para siempre**
- ✅ Sin costo alguno
- ✅ Límite: **5,000 requests por hora**
- ✅ Suficiente para cualquier proyecto

Con 5,000 requests/hora puedes:
- Actualizar datos cada minuto
- Obtener cientos de series diferentes
- Ejecutar backtesting extensivo

---

## 🔒 Seguridad de tu API Key

### ⚠️ **NUNCA hagas esto:**
```python
# ❌ MAL - No hardcodear la key
api_key = "mi_key_secreta_12345"
```

### ✅ **SIEMPRE haz esto:**
```python
# ✅ BIEN - Usar variables de entorno
import os
api_key = os.getenv('EIA_API_KEY')
```

### ✅ **Asegúrate:**
- El archivo `.env` está en `.gitignore`
- Nunca subas tu key a GitHub
- Nunca compartas capturas de pantalla con tu key visible

---

## 🆘 ¿Problemas?

### **No recibo el email**
- Revisa SPAM/Correo no deseado
- Espera 5 minutos
- Intenta con otro email

### **La key no funciona**
- Verifica que copiaste toda la key (sin espacios)
- Revisa que está en el archivo `.env` correctamente
- Reinicia Python después de agregar la key

### **Error 403**
- Significa que no se está enviando la key
- Verifica la configuración en `.env`
- Asegúrate que el nombre es exactamente `EIA_API_KEY`

---

## 📞 Links Útiles

- **Registro:** https://www.eia.gov/opendata/register.php
- **Documentación:** https://www.eia.gov/opendata/
- **API Browser:** https://www.eia.gov/opendata/browser/
- **FAQ:** https://www.eia.gov/opendata/faq.php

---

## 🎉 Una vez que tengas tu key...

Podrás ejecutar:

```bash
# Gas Natural
py src/data_collection/eia_gas_collector.py

# Petróleo (si creamos más scripts)
py src/data_collection/eia_oil_collector.py

# Todos los datos energéticos
py src/data_collection/eia_full_collector.py
```

Y tendrás acceso a **MILES de series de datos** sobre energía que complementarán perfectamente tus datos económicos y de mercado.

---

**⏰ Tiempo total:** 2 minutos  
**💰 Costo:** $0 (GRATIS)  
**🎁 Beneficio:** Miles de series de datos energéticos  
**🚀 Impacto en tu IA:** ALTO - Datos de energía son predictores clave

---

## ✅ Checklist Rápido

- [ ] Ir a: https://www.eia.gov/opendata/register.php
- [ ] Llenar formulario (1 minuto)
- [ ] Revisar email
- [ ] Copiar API key
- [ ] Agregar a archivo `.env`
- [ ] Ejecutar: `py src/data_collection/eia_gas_collector.py`
- [ ] ¡Disfrutar de los datos! 🎉

---

**¿Necesitas ayuda?** Avísame cuando tengas tu API key y te ayudo a configurarla.


## ¿Para qué la necesitas?

La **EIA (U.S. Energy Information Administration)** proporciona datos de:
- ⛽ Gas Natural
- 🛢️ Petróleo adicional
- ⚡ Energía
- 💰 Precios de commodities energéticos

Estos datos son **CRUCIALES** para predecir movimientos de mercado.

---

## 📋 Paso a Paso (2 minutos)

### **PASO 1: Ir al sitio de registro**

Abre este link en tu navegador:
```
https://www.eia.gov/opendata/register.php
```

### **PASO 2: Llenar el formulario**

El formulario es MUY simple:

```
First Name:     [Tu nombre]
Last Name:      [Tu apellido]  
Email:          [Tu email]
Organization:   [Puedes poner "Personal" o "Student"]
Affiliation:    [Selecciona "Other" o "Student"]
```

### **PASO 3: Aceptar términos**

✅ Marca la casilla: "I agree to the Terms of Service"

### **PASO 4: Enviar**

Click en **"Register"**

### **PASO 5: Revisar tu email**

📧 Recibirás un email INMEDIATAMENTE con tu API key

El email se verá así:
```
Subject: EIA Open Data API Key

Your API key is: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

Thank you for registering for the EIA Open Data API.
```

---

## 🔧 Configurar tu API Key

### **Opción 1: Archivo .env (Recomendado)**

1. Abre el archivo `.env` en la raíz del proyecto
2. Agrega esta línea:
   ```
   EIA_API_KEY=tu_key_aqui
   ```

3. Guarda el archivo

### **Opción 2: Configuración manual**

Edita: `src/utils/config.py`

```python
# Agregar esta línea
EIA_API_KEY = os.getenv("EIA_API_KEY", "tu_key_aqui")
```

---

## ✅ Verificar que funciona

Ejecuta:
```bash
py src/data_collection/eia_gas_collector.py
```

Si funciona verás:
```
✓ Datos obtenidos: XXX registros
✓ Dataset procesado guardado
```

---

## 📊 ¿Qué datos obtendrás?

Con la EIA API Key podrás obtener:

### **Gas Natural:**
- Producción mensual USA
- Precios spot
- Almacenamiento
- Importaciones/Exportaciones
- Consumo por sector

### **Petróleo (adicional a FRED):**
- Inventarios semanales
- Producción por región
- Capacidad de refinerías
- Demanda por producto

### **Otros:**
- Carbón
- Electricidad
- Energías renovables

---

## 🎯 Importancia para tu IA

Los datos de energía son **CRÍTICOS** porque:

1. 🛢️ **Gas natural = Electricidad** → Afecta costos industriales
2. ⛽ **Precios de energía** → Impulsan inflación
3. 📈 **Sector energético** → ~10% del S&P 500
4. 🌍 **Geopolítica** → Eventos globales afectan precios
5. 💰 **Trading de commodities** → Alta correlación con mercados

---

## ⏱️ Límites de la API (Generosos)

- ✅ **GRATIS para siempre**
- ✅ Sin costo alguno
- ✅ Límite: **5,000 requests por hora**
- ✅ Suficiente para cualquier proyecto

Con 5,000 requests/hora puedes:
- Actualizar datos cada minuto
- Obtener cientos de series diferentes
- Ejecutar backtesting extensivo

---

## 🔒 Seguridad de tu API Key

### ⚠️ **NUNCA hagas esto:**
```python
# ❌ MAL - No hardcodear la key
api_key = "mi_key_secreta_12345"
```

### ✅ **SIEMPRE haz esto:**
```python
# ✅ BIEN - Usar variables de entorno
import os
api_key = os.getenv('EIA_API_KEY')
```

### ✅ **Asegúrate:**
- El archivo `.env` está en `.gitignore`
- Nunca subas tu key a GitHub
- Nunca compartas capturas de pantalla con tu key visible

---

## 🆘 ¿Problemas?

### **No recibo el email**
- Revisa SPAM/Correo no deseado
- Espera 5 minutos
- Intenta con otro email

### **La key no funciona**
- Verifica que copiaste toda la key (sin espacios)
- Revisa que está en el archivo `.env` correctamente
- Reinicia Python después de agregar la key

### **Error 403**
- Significa que no se está enviando la key
- Verifica la configuración en `.env`
- Asegúrate que el nombre es exactamente `EIA_API_KEY`

---

## 📞 Links Útiles

- **Registro:** https://www.eia.gov/opendata/register.php
- **Documentación:** https://www.eia.gov/opendata/
- **API Browser:** https://www.eia.gov/opendata/browser/
- **FAQ:** https://www.eia.gov/opendata/faq.php

---

## 🎉 Una vez que tengas tu key...

Podrás ejecutar:

```bash
# Gas Natural
py src/data_collection/eia_gas_collector.py

# Petróleo (si creamos más scripts)
py src/data_collection/eia_oil_collector.py

# Todos los datos energéticos
py src/data_collection/eia_full_collector.py
```

Y tendrás acceso a **MILES de series de datos** sobre energía que complementarán perfectamente tus datos económicos y de mercado.

---

**⏰ Tiempo total:** 2 minutos  
**💰 Costo:** $0 (GRATIS)  
**🎁 Beneficio:** Miles de series de datos energéticos  
**🚀 Impacto en tu IA:** ALTO - Datos de energía son predictores clave

---

## ✅ Checklist Rápido

- [ ] Ir a: https://www.eia.gov/opendata/register.php
- [ ] Llenar formulario (1 minuto)
- [ ] Revisar email
- [ ] Copiar API key
- [ ] Agregar a archivo `.env`
- [ ] Ejecutar: `py src/data_collection/eia_gas_collector.py`
- [ ] ¡Disfrutar de los datos! 🎉

---

**¿Necesitas ayuda?** Avísame cuando tengas tu API key y te ayudo a configurarla.



