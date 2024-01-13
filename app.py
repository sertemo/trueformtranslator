# Copyright 2024 Sergio Tejedor Moreno

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Script con el código de la aplicación principal en Streamlit

# librerías internas
from io import BytesIO
import time
# librerías de terceros
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
# librerías del proyecto
from backend.db import UserDBHandler
from backend.extractor import (extract_xml, 
                                delete_xml_path, 
                                get_text_elements,
                                get_language,
                                get_topic,
                                get_num_words,
                                TopicResponse,
                                )
from backend.validator import exists_apikey
from streamlit_utils import texto, añadir_salto, imagen_con_enlace, footer


# Constantes
LISTA_IDIOMAS = [
    'Español',
    'Francés',
    'Inglés',
    'Alemán',
]
LISTA_ESPECIALIDADES = [
    'Genérico',
    'Aplicaciones y móvil',
    'Belleza, Moda Cosmética',
    'Empresa y finanzas',
    'Legal',
    'Fabricación e ingeniería',
    'Marketing SEO, publicidad',
    'Médica',
    'Novela',
    'Tecnología y Software',
    'Videojuegos',
]
# Instanciamos el handler para interacción con db
db_handler = UserDBHandler('usuarios')

# Funciones
def init() -> None:
    """Inicializa variables de sesión necesarias
    """
    if st.session_state.get("parsed_document") is None:
        st.session_state["parsed_document"] = False

def deactivate_flag() -> None:
    """desactiva la flag 'parsed_document' dando a entender que se ha parseado
    un documento, es decir que se ha cargado en el uploader
    """
    st.session_state['parsed_document'] = False

def activate_flag() -> None:
    """desactiva la flag 'parsed_document' dando a entender que se ha parseado
    un documento, es decir que se ha cargado en el uploader
    """
    st.session_state['parsed_document'] = True

def reset_all() -> None:
    """Desactiva la flag y borra la ruta xml completa
    Borra toda la sesión
    """
    deactivate_flag()
    delete_xml_path()
    st.session_state.clear()

def save_in_session(keys:list, values:list) -> None:
    """Guarda en sesión las listas de textos extraidos y los elementos

    Parameters
    ----------
    keys : list
        Lista con los nombres de las variables a guardar
    values : list
        Lista con los valores de las variables a guardar
    """
    if len(keys) != len(values):
        raise ValueError(f"keys y values deben tener la misma longitud: {len(keys)} != {len(values)}")
    for k, v in zip(keys,values):
        st.session_state[k] = v

def accumulate_in_session(keys:list, values:list[int|float]) -> None:
    """Acumula los valores pasados. Solo válido para números

    Parameters
    ----------
    keys : list
        lista de las keys a acumular
    values : list[int|float]
        valores a acumular
    """
    if len(keys) != len(values):
        raise ValueError(f"keys y values deben tener la misma longitud: {len(keys)} != {len(values)}")
    for k, v in zip(keys,values):
        if not isinstance(v, (int, float)):
            raise TypeError(f"Sólo válidos int o float, no {type(v)}.")
        st.session_state[k] = st.session_state.get(k, 0) + v


def main():
    # Configuración de la app
    st.set_page_config(
    page_title=f"TrueForm Translator",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="auto",
    )
    # Cargamos variables de entorno
    load_dotenv()
    # inicializamos session state
    init()
    # Titulo
    texto("TrueForm Translator", font_family='Rubik Doodle Shadow', font_size=60, centrar=True)
    # Descripción
    texto("Traduce tus documentos Word a un idioma de tu elección.", font_family='Dancing Script', centrar=True)
    añadir_salto()
    # inputs
    col1, col2 = st.columns(2)
    with col1:
        texto("Introduce el idioma al que traducir", font_family='Dancing Script', font_size=20, centrar=True)
        idioma = st.selectbox("idioma", 
                            options=LISTA_IDIOMAS, 
                            label_visibility="hidden",
                            index=1)
    with col2:
        # KEY de OpenAI
        texto("Introduce tu clave", font_family='Dancing Script', font_size=20, centrar=True)
        api_key = st.text_input("openai_key", label_visibility="hidden", help="Clave de OpenAI")
    añadir_salto()
    texto("Marca la especialización de tu documento", font_family='Dancing Script', font_size=20, centrar=True)
    especializacion = st.selectbox("especializacion", 
                                options=LISTA_ESPECIALIDADES, 
                                label_visibility="hidden",
                                index=0)
    añadir_salto()
    # Cargar el documento
    texto("Carga tu documento Word", font_family='Dancing Script', font_size=20, centrar=True)
    documento = st.file_uploader("documento", label_visibility="hidden", type=["docx"], on_change=reset_all)
    if documento and not st.session_state.get('parsed_document'):
        # TODO Meter toda la pipeline en una función cuando esté terminada
        # Creamos la barra de progreso
        my_bar = st.progress(0)
        t_wait = 0.2
        # Descomprimimos el documento
        my_bar.progress(0.25, 'Descomprimiendo el documento...')
        extract_xml(BytesIO(documento.read()))
        time.sleep(t_wait)
        # Extraemos los textos del document.xml y sus elementos para poder modificar
        my_bar.progress(0.5, 'Extrayendo los textos...')
        text, element_list = get_text_elements()
        num_words = get_num_words(text)
        time.sleep(t_wait)     
        # Sacamos el idioma del texto
        my_bar.progress(0.75, 'Identificando el idioma del documento...')
        idioma_es, idioma_en = get_language(text)
        time.sleep(t_wait)
        # Sacamos el tema del documento
        my_bar.progress(0.9, 'Identificando la temática del documento...')
        topic:TopicResponse = get_topic(text, idioma_es, documento.name)
        # Guardamos todo en sesión
        my_bar.progress(1, 'Guardando en sesión...')
        # Creamos el DataFrame sobre el que trabajaremos
        doc_df = pd.DataFrame(element_list, columns=['element', 'text'])
        save_in_session(['doc_df', 'text', 'elements_list', 'idioma_es', 'idioma_en', 'tematica',
                            'num_words'], 
                        [doc_df, text, element_list, idioma_es, idioma_en, topic.response,
                            num_words])
        # Acumulamos los costes
        accumulate_in_session(['total_cost'], [topic.total_cost])
        time.sleep(t_wait)
        my_bar.empty()
        # Activamos la flag para indicar que se ha cargado archivo correctamente
        activate_flag()
    #! borrar
    if 'doc_df' in st.session_state:
        st.dataframe(st.session_state['doc_df'])
        

    # TODO Mostrara aqui caracteristicas del documento: número de palabras por ejemplo y coste estimado de la traducción
    añadir_salto()
    # Botón para traducir
    traducir = st.button(label="Traducir", use_container_width=True)
    if traducir and st.session_state.get('parsed_document'):
        # TODO Verificar que el idioma destino != idioma del documento
        # TODO Verificar si APi key insertada
        # TODO Verificar si apikey existe
        if not exists_apikey(api_key, db_handler):
            st.error("La clave no es válida.")
        # TODO Verificar si apikey de admin
        # TODO Verificar si usuario activo
        # TODO Verificar si usuario palabras consumidas + palabras del documento < palabras contratadas


    st.session_state

    # Footer
    footer(2024, licencia=True)


if __name__ == '__main__':
    main()