"""
Copyright 2024 Sergio Tejedor Moreno

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Script con el código de la aplicación principal en Streamlit"""

# librerías internas
from io import BytesIO
# librerías de terceros (pip install)
import streamlit as st
# librerías del proyecto
from backend.extractor import feature_extractor
from streamlit_utils import texto, añadir_salto, imagen_con_enlace, footer


# Constances
LISTA_IDIOMAS = {
    'Español',
    'Francés',
    'Inglés',
    'Alemán',
}


def main():
    # Configuración de la app
    st.set_page_config(
    page_title=f"TrueForm Translator",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="auto",
    )
    # Titulo
    texto("TrueForm Translator", font_family='Rubik Doodle Shadow', font_size=60, centrar=True)
    # Descripción
    texto("Traduce tus documentos Word a un idioma de tu elección.", font_family='Dancing Script', centrar=True)
    añadir_salto()
    # inputs
    col1, col2 = st.columns(2)
    with col1:
        texto("Introduce el idioma al que traducir", font_family='Dancing Script', font_size=20, centrar=True)
        idioma = st.selectbox("idioma", options=LISTA_IDIOMAS, label_visibility="hidden")
    with col2:
        # TODO aqui puede ir la KEY de OpenAI
        texto("Introduce tu clave", font_family='Dancing Script', font_size=20, centrar=True)
        openai_key = st.text_input("tematica", label_visibility="hidden", help="Clave de OpenAI")
    añadir_salto()
    # Cargar el documento
    texto("Carga tu documento Word", font_family='Dancing Script', font_size=20, centrar=True)
    documento = st.file_uploader("documento", label_visibility="hidden", type=["docx"])
    if documento:
        # Extracción de toda la información del documento
        # TODO: Poner progreso siempre
        st.write(feature_extractor(BytesIO(documento.read())))
        

    # TODO Mostrara aqui caracteristicas del documento: número de palabras por ejemplo y coste estimado de la traducción
    añadir_salto()
    # Botón para traducir
    traducir = st.button(label="Traducir", use_container_width=True)

    st.session_state

    # Footer
    footer(2024, licencia=True)


if __name__ == '__main__':
    main()