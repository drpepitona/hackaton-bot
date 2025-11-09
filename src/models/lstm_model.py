"""
Modelo LSTM para predicción de series temporales financieras
"""
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.logger import logger


class LSTMPredictor:
    """
    Modelo LSTM para predicción de precios de acciones
    """
    
    def __init__(self, sequence_length=60, n_features=1):
        """
        Inicializa el modelo LSTM
        
        Args:
            sequence_length: Número de pasos temporales a usar para predicción
            n_features: Número de características de entrada
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        logger.info(f"LSTMPredictor inicializado (seq_len={sequence_length}, features={n_features})")
    
    def build_model(self, lstm_units=[50, 50], dropout_rate=0.2, learning_rate=0.001):
        """
        Construye la arquitectura del modelo LSTM
        
        Args:
            lstm_units: Lista con el número de unidades por capa LSTM
            dropout_rate: Tasa de dropout para regularización
            learning_rate: Tasa de aprendizaje
        """
        self.model = Sequential()
        
        # Primera capa LSTM
        self.model.add(LSTM(
            units=lstm_units[0],
            return_sequences=len(lstm_units) > 1,
            input_shape=(self.sequence_length, self.n_features)
        ))
        self.model.add(Dropout(dropout_rate))
        
        # Capas LSTM adicionales
        for i, units in enumerate(lstm_units[1:], 1):
            return_sequences = i < len(lstm_units) - 1
            self.model.add(LSTM(units=units, return_sequences=return_sequences))
            self.model.add(Dropout(dropout_rate))
        
        # Capa densa final
        self.model.add(Dense(units=25, activation='relu'))
        self.model.add(Dense(units=1))
        
        # Compilar modelo
        self.model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss='mean_squared_error',
            metrics=['mae', 'mape']
        )
        
        logger.info(f"Modelo LSTM construido con {len(lstm_units)} capas")
        logger.info(f"Parámetros totales: {self.model.count_params():,}")
        
        return self.model
    
    def prepare_data(self, data, target_column='Close'):
        """
        Prepara los datos para el modelo LSTM
        
        Args:
            data: DataFrame con los datos
            target_column: Columna objetivo a predecir
            
        Returns:
            X_train, y_train: Datos de entrenamiento preparados
        """
        # Extraer columna objetivo
        values = data[target_column].values.reshape(-1, 1)
        
        # Escalar datos
        scaled_data = self.scaler.fit_transform(values)
        
        # Crear secuencias
        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        logger.info(f"Datos preparados: X shape={X.shape}, y shape={y.shape}")
        
        return X, y
    
    def train(self, X_train, y_train, X_val=None, y_val=None, 
              epochs=100, batch_size=32, verbose=1):
        """
        Entrena el modelo LSTM
        
        Args:
            X_train: Datos de entrenamiento
            y_train: Etiquetas de entrenamiento
            X_val: Datos de validación (opcional)
            y_val: Etiquetas de validación (opcional)
            epochs: Número de épocas
            batch_size: Tamaño del batch
            verbose: Nivel de verbosidad
            
        Returns:
            history: Historial de entrenamiento
        """
        if self.model is None:
            self.build_model()
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss' if X_val is not None else 'loss',
                factor=0.5,
                patience=10,
                min_lr=1e-7,
                verbose=1
            )
        ]
        
        logger.info(f"Iniciando entrenamiento por {epochs} épocas...")
        
        validation_data = (X_val, y_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=verbose
        )
        
        logger.info("✓ Entrenamiento completado")
        
        return history
    
    def predict(self, X):
        """
        Realiza predicciones
        
        Args:
            X: Datos de entrada
            
        Returns:
            Predicciones des-escaladas
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado. Llama a build_model() y train() primero.")
        
        predictions = self.model.predict(X)
        predictions = self.scaler.inverse_transform(predictions)
        
        return predictions
    
    def save_model(self, filepath):
        """
        Guarda el modelo entrenado
        
        Args:
            filepath: Ruta donde guardar el modelo
        """
        self.model.save(filepath)
        logger.info(f"✓ Modelo guardado en {filepath}")
    
    def load_model(self, filepath):
        """
        Carga un modelo previamente guardado
        
        Args:
            filepath: Ruta del modelo a cargar
        """
        from tensorflow.keras.models import load_model as keras_load
        self.model = keras_load(filepath)
        logger.info(f"✓ Modelo cargado desde {filepath}")
    
    def evaluate(self, X_test, y_test):
        """
        Evalúa el modelo en datos de prueba
        
        Args:
            X_test: Datos de prueba
            y_test: Etiquetas de prueba
            
        Returns:
            Métricas de evaluación
        """
        results = self.model.evaluate(X_test, y_test, verbose=0)
        metrics = dict(zip(self.model.metrics_names, results))
        
        logger.info("Resultados de evaluación:")
        for metric, value in metrics.items():
            logger.info(f"  {metric}: {value:.4f}")
        
        return metrics


def main():
    """Ejemplo de uso del modelo LSTM"""
    from src.data_collection.market_collector import MarketCollector
    from sklearn.model_selection import train_test_split
    
    logger.info("="*50)
    logger.info("EJEMPLO DE ENTRENAMIENTO DE MODELO LSTM")
    logger.info("="*50)
    
    # Recolectar datos
    logger.info("\n1. Recolectando datos...")
    collector = MarketCollector()
    data = collector.get_stock_data("SPY")
    
    if data is None or data.empty:
        logger.error("No se pudieron obtener datos")
        return
    
    # Preparar modelo
    logger.info("\n2. Preparando modelo LSTM...")
    model = LSTMPredictor(sequence_length=60)
    model.build_model(lstm_units=[50, 50], dropout_rate=0.2)
    
    # Preparar datos
    logger.info("\n3. Preparando datos...")
    X, y = model.prepare_data(data)
    
    # Dividir en train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # Entrenar
    logger.info("\n4. Entrenando modelo...")
    history = model.train(
        X_train, y_train,
        X_val=X_test, y_val=y_test,
        epochs=50,
        batch_size=32
    )
    
    # Evaluar
    logger.info("\n5. Evaluando modelo...")
    metrics = model.evaluate(X_test, y_test)
    
    # Guardar
    logger.info("\n6. Guardando modelo...")
    from src.utils.config import MODELS_DIR
    model_path = MODELS_DIR / "lstm_spy_model.h5"
    model.save_model(model_path)
    
    logger.info("\n✓ ¡Proceso completado exitosamente!")


if __name__ == "__main__":
    main()




