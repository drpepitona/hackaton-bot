"""
🤖 BOT PREDICTIVO - INTERFAZ SIMPLE Y EFECTIVA
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from bot_inteligente_final import BotInteligente

# Configurar página
st.set_page_config(
    page_title="🤖 Bot Predictivo de Noticias",
    page_icon="📈",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .big-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
    }
    .analisis-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar bot (solo una vez)
@st.cache_resource
def inicializar_bot():
    return BotInteligente()

# Header
st.markdown('<div class="big-title">🤖 Bot Predictivo de Noticias</div>', unsafe_allow_html=True)
st.markdown("### Basado en 123,326 noticias históricas | Modelo de tokens de volatilidad")

# Inicializar
with st.spinner("Inicializando bot inteligente..."):
    bot = inicializar_bot()

st.success("✓ Bot listo con 17 categorías y 2,063 eventos históricos!")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    
    vix_actual = st.slider(
        "🔥 VIX (Índice de Miedo):",
        10, 50, 20,
        help="10-15: Calma | 20-25: Normal | 25-30: Nervioso | 30+: Pánico"
    )
    
    # Estado visual
    if vix_actual < 15:
        st.success("🟢 Mercado en CALMA")
    elif vix_actual < 25:
        st.info("🟡 Mercado NORMAL")
    elif vix_actual < 30:
        st.warning("🟠 Mercado NERVIOSO")
    else:
        st.error("🔴 Mercado en PANICO!")
    
    st.markdown("---")
    st.markdown("### 📊 Sistema")
    st.write(f"• Categorías: **17**")
    st.write(f"• Assets: **9**")
    st.write(f"• Noticias: **123,326**")
    st.write(f"• Días analizados: **2,514**")

# Layout principal
st.markdown("---")
st.header("💬 Hazle una pregunta al bot")

# Ejemplos rápidos
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📉 Fed sube tasas"):
        st.session_state.pregunta = "Que pasa si la Fed sube las tasas de interes?"

with col2:
    if st.button("⚠️ Ataque terrorista"):
        st.session_state.pregunta = "Como afecta un ataque terrorista en Europa?"

with col3:
    if st.button("💥 Crisis financiera"):
        st.session_state.pregunta = "Analiza una crisis financiera como 2008"

with col4:
    if st.button("🛢️ Petróleo sube"):
        st.session_state.pregunta = "Como afecta el petroleo subiendo de precio?"

# Input principal
pregunta = st.text_area(
    "Escribe tu pregunta:",
    value=st.session_state.get('pregunta', ""),
    height=100,
    placeholder="Ejemplo: ¿Qué pasa si China invade Taiwan?"
)

# Botón de análisis
if st.button("🔮 ANALIZAR", type="primary", use_container_width=True):
    if pregunta:
        with st.spinner("Analizando con el modelo predictivo..."):
            # Generar análisis
            analisis = bot.analizar(pregunta, vix_actual)
            
            # Mostrar resultado
            st.markdown("---")
            st.markdown('<div class="analisis-box">', unsafe_allow_html=True)
            
            # Formatear análisis para mostrar bonito
            lineas = analisis.split('\n')
            
            for linea in lineas:
                if '======' in linea:
                    st.markdown(f"**{'─'*70}**")
                elif '--- MI RAZONAMIENTO ---' in linea:
                    st.markdown(f"### {linea}")
                elif linea.startswith('1.') or linea.startswith('2.') or linea.startswith('3.') or linea.startswith('4.') or linea.startswith('5.') or linea.startswith('6.'):
                    st.markdown(f"### {linea}")
                elif '>> ACCION RECOMENDADA' in linea:
                    st.markdown(f"### {linea}")
                elif 'PREGUNTA:' in linea or 'CONTEXTO:' in linea or 'CATEGORIA:' in linea:
                    st.markdown(f"**{linea}**")
                elif 'RESUMEN EJECUTIVO' in linea:
                    st.markdown(f"### {linea}")
                elif linea.strip():
                    st.markdown(linea)
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Por favor escribe una pregunta")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🔬 Basado en Modelo de Tokens + 123,326 Noticias Históricas</p>
    <p>Sistema desarrollado para análisis predictivo de noticias financieras</p>
</div>
""", unsafe_allow_html=True)

🤖 BOT PREDICTIVO - INTERFAZ SIMPLE Y EFECTIVA
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from bot_inteligente_final import BotInteligente

# Configurar página
st.set_page_config(
    page_title="🤖 Bot Predictivo de Noticias",
    page_icon="📈",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .big-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
    }
    .analisis-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar bot (solo una vez)
@st.cache_resource
def inicializar_bot():
    return BotInteligente()

# Header
st.markdown('<div class="big-title">🤖 Bot Predictivo de Noticias</div>', unsafe_allow_html=True)
st.markdown("### Basado en 123,326 noticias históricas | Modelo de tokens de volatilidad")

# Inicializar
with st.spinner("Inicializando bot inteligente..."):
    bot = inicializar_bot()

st.success("✓ Bot listo con 17 categorías y 2,063 eventos históricos!")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    
    vix_actual = st.slider(
        "🔥 VIX (Índice de Miedo):",
        10, 50, 20,
        help="10-15: Calma | 20-25: Normal | 25-30: Nervioso | 30+: Pánico"
    )
    
    # Estado visual
    if vix_actual < 15:
        st.success("🟢 Mercado en CALMA")
    elif vix_actual < 25:
        st.info("🟡 Mercado NORMAL")
    elif vix_actual < 30:
        st.warning("🟠 Mercado NERVIOSO")
    else:
        st.error("🔴 Mercado en PANICO!")
    
    st.markdown("---")
    st.markdown("### 📊 Sistema")
    st.write(f"• Categorías: **17**")
    st.write(f"• Assets: **9**")
    st.write(f"• Noticias: **123,326**")
    st.write(f"• Días analizados: **2,514**")

# Layout principal
st.markdown("---")
st.header("💬 Hazle una pregunta al bot")

# Ejemplos rápidos
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📉 Fed sube tasas"):
        st.session_state.pregunta = "Que pasa si la Fed sube las tasas de interes?"

with col2:
    if st.button("⚠️ Ataque terrorista"):
        st.session_state.pregunta = "Como afecta un ataque terrorista en Europa?"

with col3:
    if st.button("💥 Crisis financiera"):
        st.session_state.pregunta = "Analiza una crisis financiera como 2008"

with col4:
    if st.button("🛢️ Petróleo sube"):
        st.session_state.pregunta = "Como afecta el petroleo subiendo de precio?"

# Input principal
pregunta = st.text_area(
    "Escribe tu pregunta:",
    value=st.session_state.get('pregunta', ""),
    height=100,
    placeholder="Ejemplo: ¿Qué pasa si China invade Taiwan?"
)

# Botón de análisis
if st.button("🔮 ANALIZAR", type="primary", use_container_width=True):
    if pregunta:
        with st.spinner("Analizando con el modelo predictivo..."):
            # Generar análisis
            analisis = bot.analizar(pregunta, vix_actual)
            
            # Mostrar resultado
            st.markdown("---")
            st.markdown('<div class="analisis-box">', unsafe_allow_html=True)
            
            # Formatear análisis para mostrar bonito
            lineas = analisis.split('\n')
            
            for linea in lineas:
                if '======' in linea:
                    st.markdown(f"**{'─'*70}**")
                elif '--- MI RAZONAMIENTO ---' in linea:
                    st.markdown(f"### {linea}")
                elif linea.startswith('1.') or linea.startswith('2.') or linea.startswith('3.') or linea.startswith('4.') or linea.startswith('5.') or linea.startswith('6.'):
                    st.markdown(f"### {linea}")
                elif '>> ACCION RECOMENDADA' in linea:
                    st.markdown(f"### {linea}")
                elif 'PREGUNTA:' in linea or 'CONTEXTO:' in linea or 'CATEGORIA:' in linea:
                    st.markdown(f"**{linea}**")
                elif 'RESUMEN EJECUTIVO' in linea:
                    st.markdown(f"### {linea}")
                elif linea.strip():
                    st.markdown(linea)
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Por favor escribe una pregunta")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🔬 Basado en Modelo de Tokens + 123,326 Noticias Históricas</p>
    <p>Sistema desarrollado para análisis predictivo de noticias financieras</p>
</div>
""", unsafe_allow_html=True)



