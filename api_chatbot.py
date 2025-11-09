"""
🚀 API Backend para el Chatbot de Análisis Financiero
Expone el BotGeminiCompleto como API REST para el frontend React
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from bot_gemini_completo import BotGeminiCompleto
from src.utils.logger import logger

# Crear app FastAPI
app = FastAPI(
    title="Financial Analysis Bot API",
    description="API para análisis de impacto de noticias en mercados financieros",
    version="1.0.0"
)

# Configurar CORS (permitir frontend React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
        "http://192.168.0.120:8080",
        # Production
        "https://news-bot-drag.lovable.app",  # ✅ Frontend en producción
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar bot una sola vez (singleton)
bot = None

@app.on_event("startup")
async def startup_event():
    """Inicializar el bot al arrancar la API"""
    global bot
    logger.info("🚀 Inicializando Bot Gemini Completo...")
    bot = BotGeminiCompleto()
    logger.info("✓ Bot inicializado y listo")


# Modelos de datos
class AnalysisRequest(BaseModel):
    pregunta: str
    vix: float = 20.0


class AnalysisResponse(BaseModel):
    analisis: str
    categoria: str
    token: float
    num_eventos: int
    alpha: float | None = None
    beta: float | None = None
    relevante: bool = True


# Endpoints
@app.get("/")
async def root():
    """Endpoint de prueba"""
    return {
        "status": "online",
        "message": "API de Análisis Financiero funcionando",
        "bot_status": "ready" if bot and bot.model else "offline"
    }


@app.get("/health")
async def health_check():
    """Health check para verificar que todo funciona"""
    return {
        "status": "healthy",
        "bot_initialized": bot is not None,
        "gemini_available": bot.model is not None if bot else False,
        "categories_loaded": len(bot.df_params) if bot and bot.df_params is not None else 0
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_news(request: AnalysisRequest):
    """
    Analizar una noticia o pregunta financiera
    
    Args:
        pregunta: La pregunta o noticia a analizar
        vix: El nivel actual del VIX (default: 20)
    
    Returns:
        AnalysisResponse con el análisis completo
    """
    if not bot:
        raise HTTPException(status_code=500, detail="Bot no inicializado")
    
    try:
        logger.info(f"📩 Request recibido: {request.pregunta[:50]}...")
        
        # Clasificar primero para obtener metadata
        categoria = bot.clasificar(request.pregunta)
        
        # Verificar si es irrelevante
        if categoria == 'irrelevant':
            return AnalysisResponse(
                analisis=bot._respuesta_irrelevante(request.pregunta),
                categoria="irrelevant",
                token=0.0,
                num_eventos=0,
                relevante=False
            )
        
        # Obtener parámetros de la categoría
        param_data = bot.df_params[bot.df_params['categoria'] == categoria]
        
        if len(param_data) == 0:
            token = 5.0
            num_eventos = 0
            alpha = None
            beta = None
        else:
            row = param_data.iloc[0]
            token = float(row['token'])
            num_eventos = int(row['num_eventos'])
            alpha = float(row.get('alpha', 0)) if 'alpha' in row else None
            beta = float(row.get('beta', 0)) if 'beta' in row else None
        
        # Realizar análisis completo
        analisis = bot.analizar_completo(request.pregunta, request.vix)
        
        logger.info(f"✓ Análisis completado para categoría: {categoria}")
        
        return AnalysisResponse(
            analisis=analisis,
            categoria=categoria,
            token=token,
            num_eventos=num_eventos,
            alpha=alpha,
            beta=beta,
            relevante=True
        )
        
    except Exception as e:
        logger.error(f"Error en análisis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al analizar: {str(e)}")


@app.post("/chat")
async def chat_endpoint(request: AnalysisRequest):
    """
    Endpoint alternativo para compatibilidad con frontend
    Redirige a /analyze
    """
    return await analyze_news(request)


@app.get("/categories")
async def get_categories():
    """Obtener lista de categorías disponibles con sus parámetros"""
    if not bot or bot.df_params is None:
        raise HTTPException(status_code=500, detail="Bot no inicializado")
    
    try:
        # Convertir DataFrame a lista de diccionarios
        categories = bot.df_params.to_dict('records')
        return {
            "categories": categories,
            "total": len(categories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info("="*70)
    logger.info("INICIANDO API DEL CHATBOT")
    logger.info("="*70)
    logger.info("Frontend React: http://localhost:5173")
    logger.info("API Backend: http://localhost:8000")
    logger.info("Docs API: http://localhost:8000/docs")
    logger.info("="*70)
    
    # Iniciar servidor
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

