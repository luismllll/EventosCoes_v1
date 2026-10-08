import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

def entrenar_modelo():
    try:
        df = pd.read_csv("eventos_demanda_coes.csv")
    except Exception:
        print("No se encontró el archivo CSV de eventos.")
        return

    # Asignación de etiquetas para entrenamiento
    def clasificar_severidad(texto):
        t = str(texto).lower()
        if any(w in t for w in ['disparo', 'desconexión', 'falla', 'sobrecarga', 'excepcional', 'interrumpieron']):
            return 'Alta'
        elif any(w in t for w in ['mantenimiento', 'libranza', 'inspección']):
            return 'Media'
        else:
            return 'Baja / Operación Normal'

    df['Severidad'] = df['Detalle'].apply(clasificar_severidad)

    X = df['Detalle'].fillna('')
    y = df['Severidad']

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    pipeline.fit(X, y)
    joblib.dump(pipeline, 'modelo_severidad_sein.pkl')
    print("Modelo guardado como 'modelo_severidad_sein.pkl'.")

if __name__ == "__main__":
    entrenar_modelo()