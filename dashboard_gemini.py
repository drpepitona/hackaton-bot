"""
🚀 DASHBOARD FINAL - HACKATHON
Bot Predictivo con Gemini + 123k noticias
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from bot_gemini_completo import BotGeminiCompleto

# Configuración de página
st.set_page_config(
    page_title="Bot Predictivo de Noticias",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main { padding: 2rem; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 10px;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    .prediction-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
    }
    h1 { color: #667eea; }
    h2 { color: #764ba2; }
</style>
""", unsafe_allow_html=True)

# Inicializar bot
@st.cache_resource
def init_bot():
    return BotGeminiCompleto()

bot = init_bot()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📊 Bot Predictivo de Noticias Financieras")
    st.markdown("**Análisis con IA basado en 123,326 noticias históricas**")
with col2:
    if bot.model:
        st.success("✓ Gemini Activo")
    else:
        st.warning("⚠ Modo Local")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    
    vix = st.slider(
        "📈 VIX (Índice de Miedo)",
        min_value=10,
        max_value=80,
        value=20,
        help="VIX indica la volatilidad del mercado"
    )
    
    # Indicador VIX
    if vix < 15:
        st.success("🟢 Mercado CALMADO")
    elif vix < 20:
        st.info("🔵 Mercado NORMAL")
    elif vix < 30:
        st.warning("🟡 Mercado NERVIOSO")
    else:
        st.error("🔴 Mercado en PÁNICO")
    
    st.markdown("---")
    
    st.header("📚 Ejemplos")
    ejemplos = [
        "¿Qué pasa si la Fed sube las tasas?",
        "¿Cómo afecta un ataque terrorista?",
        "Analiza una crisis financiera",
        "¿Cómo afecta el petróleo subiendo?",
        "¿Qué pasa con las elecciones en USA?",
        "¿Cómo afecta una guerra en Medio Oriente?",
        "Analiza datos de empleo débiles",
        "¿Qué pasa si el BCE baja tasas?"
    ]
    
    ejemplo_seleccionado = st.selectbox(
        "Selecciona un ejemplo:",
        [""] + ejemplos
    )
    
    st.markdown("---")
    
    st.header("📊 Estadísticas")
    st.metric("Noticias Analizadas", "123,326")
    st.metric("Categorías", "51")
    st.metric("Eventos por Categoría", "298-2,063")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Consulta al Bot")
    
    # Input con ejemplo si se seleccionó
    default_text = ejemplo_seleccionado if ejemplo_seleccionado else ""
    
    pregunta = st.text_area(
        "Escribe tu pregunta sobre noticias financieras:",
        value=default_text,
        height=100,
        placeholder="Ejemplo: ¿Qué pasa si la Fed sube las tasas de interés?"
    )
    
    analizar_btn = st.button("🚀 ANALIZAR", key="analizar")

with col2:
    st.header("ℹ️ Guía")
    st.markdown("""
    **Tipos de preguntas:**
    - 📈 Fed, ECB, tasas
    - 💥 Terrorismo, guerras
    - 💰 PIB, empleo, crisis
    - 🛢️ Petróleo, oro
    - 🗳️ Elecciones
    - 📊 Mercados, forex
    
    **El bot analiza:**
    1. Categoría de noticia
    2. Eventos históricos
    3. Impacto probable
    4. Dirección y magnitud
    5. Recomendación
    """)

# Análisis
if analizar_btn and pregunta:
    with st.spinner("🤖 Analizando con IA..."):
        analisis = bot.analizar_completo(pregunta, vix)
    
    # Mostrar resultado
    st.markdown("---")
    st.header("📊 RESULTADO DEL ANÁLISIS")
    
    # Extraer info del análisis
    lineas = analisis.split('\n')
    
    # Buscar datos clave
    categoria = ""
    token = ""
    eventos = ""
    probabilidad = ""
    direccion = ""
    magnitud = ""
    recomendacion = ""
    
    for linea in lineas:
        if "CATEGORÍA:" in linea:
            categoria = linea.split(":")[-1].strip()
        elif "TOKEN:" in linea:
            token = linea.split(":")[-1].strip()
        elif "EVENTOS HISTÓRICOS:" in linea:
            eventos = linea.split(":")[-1].strip()
        elif "Probabilidad de impacto:" in linea:
            probabilidad = linea.split(":")[-1].strip()
        elif "Dirección esperada:" in linea:
            direccion = linea.split(":")[-1].strip()
        elif "Magnitud típica:" in linea:
            magnitud = linea.split(":")[-1].strip()
        elif "RECOMENDACIÓN:" in linea:
            recomendacion = linea.split(":")[-1].strip()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📂 Categoría</h3>
            <h2>{categoria}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯 Token</h3>
            <h2>{token}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Eventos</h3>
            <h2>{eventos}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎲 Probabilidad</h3>
            <h2>{probabilidad}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Predicción destacada
    st.markdown(f"""
    <div class="prediction-box">
        <h2>🔮 PREDICCIÓN</h2>
        <h3>Dirección: {direccion}</h3>
        <h3>Magnitud: {magnitud}</h3>
        <h3>Recomendación: {recomendacion}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Análisis completo
    with st.expander("📄 Ver Análisis Completo", expanded=True):
        st.text(analisis)
    
    # Botones de acción
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "💾 Descargar Análisis",
            analisis,
            file_name=f"analisis_{categoria}.txt",
            mime="text/plain"
        )
    
    with col2:
        if st.button("🔄 Nuevo Análisis"):
            st.rerun()
    
    with col3:
        if st.button("📊 Ver Más Estadísticas"):
            st.info("Función próximamente...")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Bot Predictivo de Noticias</strong> | Hackathon 2025</p>
    <p>Powered by Gemini AI + 123,326 noticias históricas | Modelo de tokens de volatilidad</p>
</div>
""", unsafe_allow_html=True)


