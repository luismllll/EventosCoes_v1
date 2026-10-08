# ⚡ Monitor e IA para el Centro de Control del SEIN (COES)

Proyecto final que implementa una solución End-to-End para el monitoreo de contingencias eléctricas y la máxima demanda en el Perú.

## 🚀 Arquitectura del Proyecto
1. **Recolección (Scraping):** Extracción automatizada con `BeautifulSoup` y `Requests`.
2. **Modelo de Predicción (ML):** Clasificación de severidad de fallas mediante `Random Forest` y `TF-IDF`.
3. **Dashboard & Chat IA:** Interfaz interactiva en `Streamlit` integrada con `Google Gemini API`.
4. **Contenerización:** Despliegue empaquetado en `Docker`.

## 🛠️ Ejecución Local
```bash
python paso1_scraping.py
python entrenar_modelo.py
streamlit run app.py