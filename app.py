import streamlit as st
import pandas as pd
import google.generativeai as genai
import joblib
import os

st.set_page_config(
    page_title="COES SEIN - Centro de Control",
    page_icon="⚡",
    layout="wide"
)

@st.cache_data(ttl=300)
def cargar_datos():
    ruta_csv = "eventos_demanda_coes.csv"
    if os.path.exists(ruta_csv):
        return pd.read_csv(ruta_csv)
    return pd.DataFrame()

@st.cache_resource
def cargar_modelo_ml():
    ruta_modelo = "modelo_severidad_sein.pkl"
    if os.path.exists(ruta_modelo):
        return joblib.load(ruta_modelo)
    return None

df_data = cargar_datos()
modelo_ml = cargar_modelo_ml()

st.title("⚡ COES SEIN - Centro de Control")
st.caption("Monitoreo de Eventos Relevantes y Máxima Demanda")

# Panel lateral
st.sidebar.header("Filtros y Configuración")
api_key = st.sidebar.text_input("API Key de Gemini:", type="password")

st.sidebar.divider()
secciones_disponibles = df_data["Sección"].unique().tolist() if not df_data.empty else []
seccion_seleccionada = st.sidebar.multiselect(
    "Filtrar por Sección:",
    options=secciones_disponibles,
    default=secciones_disponibles
)

df_filtrado = df_data[df_data["Sección"].isin(seccion_seleccionada)] if not df_data.empty else df_data

tab_dash, tab_ml, tab_chat = st.tabs(["Dashboard", "Modelo de Predicción", "Asistente IA"])

# Dashboard
with tab_dash:
    st.subheader("Indicadores")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Registros", len(df_filtrado))
    col2.metric("Eventos Relevantes", len(df_filtrado[df_filtrado["Sección"] == "Evento Relevante"]) if not df_filtrado.empty else 0)
    col3.metric("Máxima Demanda", len(df_filtrado[df_filtrado["Sección"] == "Máxima Demanda"]) if not df_filtrado.empty else 0)
    
    st.divider()
    st.subheader("Registro de Eventos")
    
    busqueda = st.text_input("Buscar por palabra clave:")
    if busqueda and not df_filtrado.empty:
        df_mostrar = df_filtrado[
            df_filtrado["Título"].astype(str).str.contains(busqueda, case=False, na=False) |
            df_filtrado["Detalle"].astype(str).str.contains(busqueda, case=False, na=False)
        ]
    else:
        df_mostrar = df_filtrado

    st.dataframe(df_mostrar, use_container_width=True)
    
    if not df_mostrar.empty:
        csv_bytes = df_mostrar.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("Descargar CSV", data=csv_bytes, file_name="reporte_coes.csv", mime="text/csv")

# Clasificador con ML
with tab_ml:
    st.subheader("Clasificación de Severidad con Random Forest")
    
    if modelo_ml:
        texto_evaluar = st.text_area("Ingresa la descripción del evento:",
                                     placeholder="Ej: Desconexión de la línea L-2201 por actuación de protecciones...")
        
        if st.button("Evaluar Severidad"):
            if texto_evaluar.strip():
                prediccion = modelo_ml.predict([texto_evaluar])[0]
                probas = modelo_ml.predict_proba([texto_evaluar])[0]
                clases = modelo_ml.classes_
                
                if prediccion == "Alta":
                    st.error(f"Severidad: **{prediccion}**")
                elif prediccion == "Media":
                    st.warning(f"Severidad: **{prediccion}**")
                else:
                    st.success(f"Severidad: **{prediccion}**")
                
                df_prob = pd.DataFrame({"Clase": clases, "Probabilidad": probas})
                st.bar_chart(df_prob.set_index("Clase"))
            else:
                st.info("Ingresa un texto para evaluar.")
    else:
        st.error("Modelo no encontrado. Ejecuta 'python entrenar_modelo.py'.")

# Chat Asistente
with tab_chat:
    st.subheader("Consultas sobre Eventos del SEIN")
    
    if "mensajes_chat" not in st.session_state:
        st.session_state.mensajes_chat = [
            {"role": "assistant", "content": "Hola, soy el asistente del Centro de Control. ¿Qué consulta tienes sobre los eventos del SEIN?"}
        ]

    for msg in st.session_state.mensajes_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ej: ¿Qué fallas ocurrieron por condiciones climatológicas?"):
        st.session_state.mensajes_chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if not api_key:
            respuesta_err = "Ingresa tu API Key de Gemini en el panel lateral."
            with st.chat_message("assistant"):
                st.warning(respuesta_err)
            st.session_state.mensajes_chat.append({"role": "assistant", "content": respuesta_err})
        else:
            with st.chat_message("assistant"):
                with st.spinner("Consultando información..."):
                    try:
                        genai.configure(api_key=api_key)
                        modelos_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                        
                        contexto_texto = df_filtrado.to_string(index=False)
                        prompt_sistema = f"""
                        Eres un Ingeniero de Centro de Control en Perú.
                        Responde basándote solo en estos datos del COES:
                        
                        {contexto_texto}
                        
                        Pregunta: {prompt}
                        """

                        respuesta_texto = None
                        for nombre_m in modelos_disponibles:
                            try:
                                model = genai.GenerativeModel(nombre_m)
                                response = model.generate_content(prompt_sistema)
                                if response and hasattr(response, 'text'):
                                    respuesta_texto = response.text
                                    break
                            except Exception:
                                continue

                        if respuesta_texto:
                            st.markdown(respuesta_texto)
                            st.session_state.mensajes_chat.append({"role": "assistant", "content": respuesta_texto})
                        else:
                            st.error("No se pudo conectar a Gemini.")

                    except Exception as e:
                        st.error(f"Error de conexión: {e}")