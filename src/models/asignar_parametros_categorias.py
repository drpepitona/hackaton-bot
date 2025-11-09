"""
Asignación Inteligente de Parámetros α y β por Categoría

ESTRATEGIA:
En lugar de optimizar desde cero, usamos las características
de los tokens para asignar α y β inteligentemente.

REGLAS:
1. Token alto + Alta volatilidad = β alto (efecto polvorín)
2. Alta asimetría (muy alcista o muy bajista) = α alto
3. Baja volatilidad = α bajo, β bajo
"""
import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import PROCESSED_DATA_DIR, MODELS_DIR
from src.utils.logger import logger


class AsignadorParametros:
    """
    Asigna α y β a cada categoría basándose en características
    """
    
    def __init__(self):
        self.params_por_categoria = {}
        self.vix_critico = 20.0
        self.df_tokens = None
        
        logger.info("✓ AsignadorParametros inicializado")
    
    def cargar_tokens(self):
        """Carga tokens"""
        token_files = list(PROCESSED_DATA_DIR.glob("landau/tokens_volatilidad_*.csv"))
        if token_files:
            self.df_tokens = pd.read_csv(token_files[0])
            logger.info(f"✓ Tokens cargados: {len(self.df_tokens)}")
            return True
        return False
    
    def calcular_parametros_categoria(self, row):
        """
        Calcula α y β para una categoría basándose en sus características
        
        LÓGICA REVISADA:
        
        α (Amplificador) - CONSERVADOR:
          - El TOKEN ya da la probabilidad base (token 7.4 = 74%)
          - α debe ser un AJUSTE pequeño, no un multiplicador grande
          - Fórmula: α = 0.15 + (volatilidad * 5)
          - Rango: [0.15, 0.65]
          - Con VIX 40 (v_norm=2.0), amplificación máxima: ~50-60%
        
        β (Exponente/Polvorín):
          - Depende de la volatilidad y categoría
          - Alta volatilidad = β alto (más sensible a VIX)
          - Fórmula: β = 0.8 + (volatilidad * 15) + bonus_categoria
          - Rango: [0.8, 3.0]
        
        Bonus β por tipo de noticia:
          - Guerra/Terror: +0.8 (efecto polvorín EXTREMO)
          - Crisis: +0.6 (efecto polvorín ALTO)
          - Fed/ECB: +0.3 (efecto polvorín MODERADO)
          - GDP/Empleo: +0.2 (efecto polvorín LEVE)
          - Housing/Earnings: +0.0 (estable)
        
        EJEMPLO:
          Terrorism: token=7.4 (74% base), volatilidad=0.70%
          
          α = 0.15 + (0.007 * 5) = 0.185
          β = 0.8 + (0.007 * 15) + 0.8 = 1.705
          
          VIX 15 (calma):  74% × (1 + 0.185 × (-0.25)^1.705) = 74% × 0.98 = 72%
          VIX 40 (pánico): 74% × (1 + 0.185 × (1.0)^1.705)   = 74% × 1.185 = 88%
          
          → Ajuste razonable: 72%-88% (no explota a 100%+)
        """
        categoria = row['categoria']
        token = row['token']
        volatilidad = row['volatilidad_promedio']
        
        # Calcular α (amplificador CONSERVADOR)
        # α pequeño = ajuste sutil, no explosión
        alpha = 0.15 + (volatilidad * 5.0)
        alpha = max(0.15, min(0.65, alpha))
        
        # Calcular β base (efecto polvorín)
        beta_base = 0.8 + (volatilidad * 15.0)
        
        # Bonus por categoría (efecto polvorín esperado)
        bonus = 0.0
        
        if any(kw in categoria for kw in ['war', 'terrorism', 'terror', 'attack']):
            bonus = 0.8  # Efecto polvorín EXTREMO
            # Incrementar α un poco para estas categorías críticas
            alpha = min(0.65, alpha * 1.5)
        elif any(kw in categoria for kw in ['crisis', 'crash', 'bailout']):
            bonus = 0.6  # Efecto polvorín ALTO
            alpha = min(0.65, alpha * 1.3)
        elif any(kw in categoria for kw in ['fed', 'ecb', 'rates', 'policy']):
            bonus = 0.3  # Efecto polvorín MODERADO
            alpha = min(0.65, alpha * 1.2)
        elif any(kw in categoria for kw in ['gdp', 'employment', 'unemployment']):
            bonus = 0.2  # Efecto polvorín LEVE
            alpha = min(0.65, alpha * 1.1)
        else:
            bonus = 0.0  # Sin bonus
        
        beta = beta_base + bonus
        beta = max(0.8, min(3.0, beta))
        
        return alpha, beta
    
    def asignar_todos_parametros(self):
        """
        Asigna parámetros a todas las categorías
        """
        logger.info("\n" + "="*70)
        logger.info("ASIGNACIÓN DE PARÁMETROS POR CATEGORÍA")
        logger.info("="*70)
        
        # Filtrar solo SPY
        df_spy = self.df_tokens[self.df_tokens['asset'] == 'SPY'].copy()
        
        for idx, row in df_spy.iterrows():
            categoria = row['categoria']
            
            alpha, beta = self.calcular_parametros_categoria(row)
            
            self.params_por_categoria[categoria] = {
                'alpha': float(alpha),
                'beta': float(beta),
                'token': float(row['token']),
                'volatilidad': float(row['volatilidad_promedio']),
                'num_eventos': int(row['num_eventos']),
                'pct_alcista': float(row['pct_alcista'])
            }
            
            logger.info(f"  {categoria:<25s}: α={alpha:.3f}, β={beta:.3f} "
                       f"(token={row['token']:.1f}, vol={row['volatilidad_promedio']*100:.2f}%)")
        
        logger.info(f"\n✓ Parámetros asignados: {len(self.params_por_categoria)} categorías")
    
    def analizar_parametros(self):
        """
        Analiza la distribución de parámetros
        """
        logger.info("\n" + "="*70)
        logger.info("ANÁLISIS DE PARÁMETROS")
        logger.info("="*70)
        
        # Ordenar por β (efecto polvorín)
        categorias_sorted = sorted(
            self.params_por_categoria.items(),
            key=lambda x: x[1]['beta'],
            reverse=True
        )
        
        logger.info("\n🔥 TOP 10 - MAYOR EFECTO POLVORÍN (β):")
        logger.info("─"*70)
        logger.info(f"{'Categoría':<25s} | {'α':>6s} | {'β':>6s} | {'Token':>6s} | {'Vol':>8s}")
        logger.info("─"*70)
        
        for cat, params in categorias_sorted[:10]:
            logger.info(f"{cat:<25s} | {params['alpha']:>6.3f} | {params['beta']:>6.3f} | "
                       f"{params['token']:>6.1f} | {params['volatilidad']*100:>7.2f}%")
        
        logger.info("\n💤 TOP 10 - MENOR EFECTO POLVORÍN (β):")
        logger.info("─"*70)
        
        for cat, params in categorias_sorted[-10:]:
            logger.info(f"{cat:<25s} | {params['alpha']:>6.3f} | {params['beta']:>6.3f} | "
                       f"{params['token']:>6.1f} | {params['volatilidad']*100:>7.2f}%")
        
        # Estadísticas
        betas = [p['beta'] for p in self.params_por_categoria.values()]
        alphas = [p['alpha'] for p in self.params_por_categoria.values()]
        
        logger.info("\n📊 ESTADÍSTICAS GLOBALES:")
        logger.info(f"  β promedio: {np.mean(betas):.3f}")
        logger.info(f"  β min-max: [{np.min(betas):.3f}, {np.max(betas):.3f}]")
        logger.info(f"  α promedio: {np.mean(alphas):.3f}")
        logger.info(f"  α min-max: [{np.min(alphas):.3f}, {np.max(alphas):.3f}]")
        
        # Clasificar por intensidad
        logger.info("\n🎯 CLASIFICACIÓN POR INTENSIDAD:")
        
        extreme = [(c, p) for c, p in categorias_sorted if p['beta'] > 2.0]
        high = [(c, p) for c, p in categorias_sorted if 1.5 < p['beta'] <= 2.0]
        moderate = [(c, p) for c, p in categorias_sorted if 1.0 < p['beta'] <= 1.5]
        low = [(c, p) for c, p in categorias_sorted if p['beta'] <= 1.0]
        
        logger.info(f"\n  EXTREMO (β > 2.0): {len(extreme)} categorías")
        for cat, params in extreme:
            logger.info(f"    • {cat}: β={params['beta']:.2f}, token={params['token']:.1f}")
        
        logger.info(f"\n  ALTO (1.5 < β ≤ 2.0): {len(high)} categorías")
        for cat, params in high[:5]:
            logger.info(f"    • {cat}: β={params['beta']:.2f}, token={params['token']:.1f}")
        
        logger.info(f"\n  MODERADO (1.0 < β ≤ 1.5): {len(moderate)} categorías")
        for cat, params in moderate[:5]:
            logger.info(f"    • {cat}: β={params['beta']:.2f}, token={params['token']:.1f}")
        
        logger.info(f"\n  BAJO (β ≤ 1.0): {len(low)} categorías")
    
    def calcular_impacto_contextual(self, p_base, vix, alpha, beta):
        """Calcula impacto contextual"""
        v_norm = vix / self.vix_critico
        
        if v_norm <= 1.0:
            impacto = p_base * (1.0 - alpha * 0.1 * (1 - v_norm))
        else:
            impacto = p_base * (1.0 + alpha * ((v_norm - 1.0) ** beta))
        
        return max(0, min(100, impacto))
    
    def demo_predicciones(self):
        """
        Demuestra predicciones con diferentes categorías y VIX
        """
        logger.info("\n" + "="*70)
        logger.info("DEMO: COMPARACIÓN DE CATEGORÍAS")
        logger.info("="*70)
        
        # Seleccionar categorías interesantes
        categorias_demo = []
        
        for cat in ['war_russia', 'terrorism', 'financial_crisis', 'fed_rates', 'us_gdp_data']:
            if cat in self.params_por_categoria:
                categorias_demo.append(cat)
        
        if not categorias_demo:
            # Usar las primeras disponibles
            categorias_demo = list(self.params_por_categoria.keys())[:5]
        
        vix_levels = [12, 20, 30, 40]
        
        for cat in categorias_demo:
            params = self.params_por_categoria[cat]
            p_base = (params['token'] / 10.0) * 100
            
            logger.info(f"\n{cat.upper()} (token={params['token']:.1f}, α={params['alpha']:.2f}, β={params['beta']:.2f})")
            logger.info(f"  P_base: {p_base:.1f}%")
            
            resultados = []
            for vix in vix_levels:
                p_ctx = self.calcular_impacto_contextual(
                    p_base, vix, params['alpha'], params['beta']
                )
                ajuste = ((p_ctx / p_base - 1) * 100) if p_base > 0 else 0
                resultados.append(f"VIX {vix}: {p_ctx:.0f}% ({ajuste:+.0f}%)")
            
            logger.info(f"  {' | '.join(resultados)}")
    
    def guardar_modelo(self):
        """Guarda modelo"""
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # Pickle
        filepath = MODELS_DIR / f"modelo_refinado_vix_categorias_{timestamp}.pkl"
        modelo = {
            'params_por_categoria': self.params_por_categoria,
            'vix_critico': self.vix_critico,
            'df_tokens': self.df_tokens
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(modelo, f)
        
        logger.info(f"\n✓ Modelo guardado: {filepath}")
        
        # JSON legible
        json_path = PROCESSED_DATA_DIR / "landau" / f"parametros_por_categoria_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(self.params_por_categoria, f, indent=2)
        
        logger.info(f"✓ JSON guardado: {json_path}")
        
        # CSV para análisis
        df_params = pd.DataFrame([
            {
                'categoria': cat,
                'alpha': p['alpha'],
                'beta': p['beta'],
                'token': p['token'],
                'volatilidad': p['volatilidad'],
                'num_eventos': p['num_eventos']
            }
            for cat, p in self.params_por_categoria.items()
        ])
        
        csv_path = PROCESSED_DATA_DIR / "landau" / f"parametros_por_categoria_{timestamp}.csv"
        df_params.to_csv(csv_path, index=False)
        
        logger.info(f"✓ CSV guardado: {csv_path}")
        
        return filepath


def main():
    """Pipeline completo"""
    logger.info("="*70)
    logger.info("ASIGNACIÓN INTELIGENTE DE PARÁMETROS α Y β")
    logger.info("="*70)
    logger.info("Basado en características de tokens y tipo de noticia")
    logger.info("")
    
    asignador = AsignadorParametros()
    
    # 1. Cargar tokens
    logger.info("\n【FASE 1】 Cargando tokens...")
    if not asignador.cargar_tokens():
        logger.error("❌ No se pudieron cargar tokens")
        return
    
    # 2. Asignar parámetros
    logger.info("\n【FASE 2】 Asignando parámetros...")
    asignador.asignar_todos_parametros()
    
    # 3. Analizar
    logger.info("\n【FASE 3】 Analizando...")
    asignador.analizar_parametros()
    
    # 4. Demo
    logger.info("\n【FASE 4】 Demo de predicciones...")
    asignador.demo_predicciones()
    
    # 5. Guardar
    logger.info("\n【FASE 5】 Guardando modelo...")
    asignador.guardar_modelo()
    
    logger.info("\n" + "="*70)
    logger.info("✓✓✓ MODELO CON PARÁMETROS POR CATEGORÍA COMPLETADO ✓✓✓")
    logger.info("="*70)
    
    logger.info("\n📋 RESUMEN:")
    logger.info(f"  • {len(asignador.params_por_categoria)} categorías")
    betas = [p['beta'] for p in asignador.params_por_categoria.values()]
    logger.info(f"  • β rango: [{min(betas):.2f}, {max(betas):.2f}]")
    logger.info(f"  • Categorías β>2.0: {sum(1 for b in betas if b > 2.0)}")


if __name__ == "__main__":
    main()

