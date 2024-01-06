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
# librerías de terceros (pip install)
import streamlit as st
# librerías del proyecto
from streamlit_utils import texto, añadir_salto, imagen_con_enlace

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
    layout="centered",
    initial_sidebar_state="auto",
    )
    # Titulo
    texto("TrueForm Translator", font_family='Rubik Doodle Shadow', font_size=60, centrar=True)
    # Descripción
    texto("Traduce tus documentos Word a un idioma de tu elección.", font_family='Dancing Script', centrar=True)
    añadir_salto()
    col1, col2 = st.columns(2)

    with col1:
        texto("Idioma", font_family='Dancing Script', font_size=20, centrar=True)
        idioma = st.selectbox("idioma", options=LISTA_IDIOMAS, label_visibility="hidden")
    with col2:
        # TODO Si no ponemos temática (se saca auto) aqui puede ir la KEY de OpenAI
        texto("¿Sobre qué trata tu documento?", font_family='Dancing Script', font_size=20, centrar=True)
        tematica = st.text_input("tematica", label_visibility="hidden")
    añadir_salto()
    # Cargar el documento
    texto("Carga tu documento Word", font_family='Dancing Script', font_size=20, centrar=True)
    documento = st.file_uploader("documento", label_visibility="hidden", type=["docx"])
    # TODO Poner text box para api key

    # TODO Mostrara aqui caracteristicas del documento: número de palabras por ejemplo y coste estimado de la traducción
    añadir_salto()
    # Botón para traducir
    traducir = st.button(label="Traducir", use_container_width=True)

    añadir_salto(5)
    # TODO Cierre con referencia a mi redes y licencia Apache
    col1, col2, col3, col4, col5 = st.columns(5)            
    with col2:
        imagen_con_enlace('https://i.imgur.com/umyrYj9.png',
                        'https://github.com/sertemo', 
                        alt_text='GitHub', max_width=20)
    with col3:
        imagen_con_enlace('https://i.imgur.com/hLAeokj.png', 
                        'https://www.linkedin.com/in/stm84/', 
                        alt_text='linkedin', max_width=20)
    with col4:
        imagen_con_enlace('https://i.imgur.com/Qc8t46o.png', 
                        'https://stm-cv.streamlit.app/', 
                        alt_text='Chat-CV', max_width=20)

    texto('Copyright 2024 Sergio Tejedor Moreno', centrar=True, font_size=10)
    texto("Licensed under the Apache License, Version 2.0", centrar=True, font_size=10)



if __name__ == '__main__':
    main()