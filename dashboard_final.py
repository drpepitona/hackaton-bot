"""
DASHBOARD FINAL PARA HACKATHON
Funciona con tu modelo de tokens (ya entrenado)
Si termina el fine-tuning, lo integra automáticamente
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))

from sistema_final_hackathon import SistemaFinalHackathon

# Config
st.set_page_config(
    page_title="Bot Predictivo de Noticias",
    page_icon="📈",
    layout="wide"
)

# CSS
st.markdown("""
<style>
.big-title {font-size: 3rem; font-weight: bold; text-align: center; color: #1f77b4;}
.result-box {background: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;}
</style>
""", unsafe_allow_html=True)

# Inicializar
@st.cache_resource
def init():
    return SistemaFinalHackathon()

st.markdown('<div class="big-title">🤖 Bot Predictivo de Noticias</div>', unsafe_allow_html=True)
st.markdown("### 123,326 noticias históricas | 17 categorías | Modelo de tokens de volatilidad")

sistema = init()

st.success("✓ Sistema listo!")

# Sidebar
with st.sidebar:
    st.header("⚙️ VIX")
    vix = st.slider("Índice de Miedo:", 10, 50, 20)
    
    if vix < 15:
        st.success("🟢 CALMA")
    elif vix < 25:
        st.info("🟡 NORMAL")
    elif vix < 30:
        st.warning("🟠 NERVIOSO")
    else:
        st.error("🔴 PÁNICO")
    
    st.markdown("---")
    st.markdown("### 📊 Datos")
    st.write("• Noticias: **123,326**")
    st.write("• Categorías: **17**")
    st.write("• Assets: **9**")

# Main
st.markdown("---")
st.header("💬 Pregúntale al bot")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📉 Fed tasas"):
        st.session_state.q = "Que pasa si la Fed sube tasas?"
with col2:
    if st.button("⚠️ Terrorismo"):
        st.session_state.q = "Como afecta un ataque terrorista?"
with col3:
    if st.button("💥 Crisis"):
        st.session_state.q = "Analiza una crisis financiera"
with col4:
    if st.button("🛢️ Petróleo"):
        st.session_state.q = "Como afecta el petroleo subiendo?"

pregunta = st.text_area(
    "Tu pregunta:",
    value=st.session_state.get('q', ""),
    height=80,
    placeholder="Ej: ¿Qué pasa si China invade Taiwan?"
)

if st.button("🔮 ANALIZAR", type="primary"):
    if pregunta:
        with st.spinner("Analizando..."):
            resultado = sistema.analizar(pregunta, vix)
            
            st.markdown("---")
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.code(resultado, language=None)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Escribe una pregunta")

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center;color:gray;'>🔬 Basado en 123,326 noticias + Modelo de tokens</div>", unsafe_allow_html=True)

DASHBOARD FINAL PARA HACKATHON
Funciona con tu modelo de tokens (ya entrenado)
Si termina el fine-tuning, lo integra automáticamente
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))

from sistema_final_hackathon import SistemaFinalHackathon

# Config
st.set_page_config(
    page_title="Bot Predictivo de Noticias",
    page_icon="📈",
    layout="wide"
)

# CSS
st.markdown("""
<style>
.big-title {font-size: 3rem; font-weight: bold; text-align: center; color: #1f77b4;}
.result-box {background: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;}
</style>
""", unsafe_allow_html=True)

# Inicializar
@st.cache_resource
def init():
    return SistemaFinalHackathon()

st.markdown('<div class="big-title">🤖 Bot Predictivo de Noticias</div>', unsafe_allow_html=True)
st.markdown("### 123,326 noticias históricas | 17 categorías | Modelo de tokens de volatilidad")

sistema = init()

st.success("✓ Sistema listo!")

# Sidebar
with st.sidebar:
    st.header("⚙️ VIX")
    vix = st.slider("Índice de Miedo:", 10, 50, 20)
    
    if vix < 15:
        st.success("🟢 CALMA")
    elif vix < 25:
        st.info("🟡 NORMAL")
    elif vix < 30:
        st.warning("🟠 NERVIOSO")
    else:
        st.error("🔴 PÁNICO")
    
    st.markdown("---")
    st.markdown("### 📊 Datos")
    st.write("• Noticias: **123,326**")
    st.write("• Categorías: **17**")
    st.write("• Assets: **9**")

# Main
st.markdown("---")
st.header("💬 Pregúntale al bot")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📉 Fed tasas"):
        st.session_state.q = "Que pasa si la Fed sube tasas?"
with col2:
    if st.button("⚠️ Terrorismo"):
        st.session_state.q = "Como afecta un ataque terrorista?"
with col3:
    if st.button("💥 Crisis"):
        st.session_state.q = "Analiza una crisis financiera"
with col4:
    if st.button("🛢️ Petróleo"):
        st.session_state.q = "Como afecta el petroleo subiendo?"

pregunta = st.text_area(
    "Tu pregunta:",
    value=st.session_state.get('q', ""),
    height=80,
    placeholder="Ej: ¿Qué pasa si China invade Taiwan?"
)

if st.button("🔮 ANALIZAR", type="primary"):
    if pregunta:
        with st.spinner("Analizando..."):
            resultado = sistema.analizar(pregunta, vix)
            
            st.markdown("---")
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.code(resultado, language=None)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Escribe una pregunta")

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center;color:gray;'>🔬 Basado en 123,326 noticias + Modelo de tokens</div>", unsafe_allow_html=True)



