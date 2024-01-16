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
from functools import partial
from io import BytesIO
import random
import re
import time
# librerías de terceros
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from streamlit import delta_generator
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
from backend.translator import (translate,
                                TranslationResponse)
from backend.validator import (exists_apikey, 
                                apikey_is_admin,
                                apikey_is_active,
                                has_words_left,
                                are_special_char)
from backend.utils import estimate_openai_cost
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
    'Filosófico',
    'Legal',
    'Fabricación e ingeniería',
    'Marketing SEO, publicidad',
    'Médico',
    'Novela',
    'Tecnología y Software',
    'Videojuegos',
]
# Instanciamos el handler para interacción con db
db_handler = UserDBHandler('usuarios')
# instancia footer con argumentos fijos
put_footer = partial(footer, 2024, True)

# Funciones
def init() -> None:
    """Inicializa variables de sesión necesarias
    """
    if st.session_state.get("parsed_document") is None:
        st.session_state["parsed_document"] = False
        if st.session_state.get('diccionary') is None:
            st.session_state['diccionary'] = {}

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

def show_error(msg:str, progress_bar:delta_generator.DeltaGenerator=None) -> None:
    """Función que realiza 4 cosas:
    - muestra mensaje de error
    - vacía la barra de progreso si hay
    - muestra el footer de la app
    - para la ejecución de la app

    Parameters
    ----------
    msg : str
        _description_
    progress_bar : _type_
        _description_
    """
    st.error(msg, icon='🛑')
    put_footer()
    if progress_bar is not None:
        progress_bar.empty()
    st.stop()

def wait_randomly(max:int=1):
    """max es en 

    Parameters
    ----------
    max : int
        _description_
    """
    cooldown = round(random.random(), 1) * max
    time.sleep(cooldown)

def translation_loop(
        *,
        apikey:str,
        model:str,
        objects_list:list[dict], 
        progress_bar:delta_generator.DeltaGenerator,
        chain_params:dict) -> None:
    n_elements = len(objects_list)
    step = 1 / n_elements
    for idx, obj in enumerate(objects_list):
        progress_bar.progress(step * idx, f'Traduciendo {idx}/{n_elements}...')
        # Sacamos el texto del objeto
        texto:str = obj['text']
        # No traducir caracteres etc.
        if (len(texto) == 1) or texto.isspace() or texto.isdigit() or texto.isnumeric() or are_special_char(texto.strip()):
            obj['translation'] = texto
            continue
        # Buscamos en el diccionario si el texto sin espacios ya ha sido traducido
        if (transl:=st.session_state['diccionary'].get(texto.strip())) is not None:
            obj['translation'] = transl
            continue

        # Pasamos por el traductor y sacamos traducción y coste
        response:TranslationResponse = translate(apikey, model, text=texto, **chain_params)
        translated_text:str = response.response
        translation_cost:float = response.total_cost        
        # Si es una sola palabra añadimos al diccionario quitando espacios
        if len(texto.split()) == 1:
            st.session_state['diccionary'][texto.strip()] = translated_text.strip()
        # Verificamos que los espacios al principio y al final coincidan con el texto original
        if texto[0].isspace() and (not translated_text[0].isspace()):
            translated_text = " " + translated_text
        if texto[-1].isspace() and (not translated_text[-1].isspace()):
            translated_text = translated_text + " "        
        # Actualizamos el objeto añadiendo un campo traducido y el coste en sesión
        obj['translation'] = translated_text
        accumulate_in_session(['real_total_cost'], [translation_cost])
        # Cooldown aleatorio
        if random.random() < 0.5:
            wait_randomly(2)
        
    progress_bar.empty()

#TODO Crear flag de "traducido" true o false como parsed_document y no dejar traducir si ya se ha traducido
def main():
    # Configuración de la app
    st.set_page_config(
    page_title=f"TrueForm Translator",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="auto",
    )
    # inicializamos session state
    init()
    # Titulo
    texto("TrueForm Translator", font_family='Rubik Doodle Shadow', font_size=60, centrar=True)
    # Descripción
    texto("Traduce tus propios documentos Word a un idioma de tu elección.", font_family='Dancing Script', centrar=True)
    # TODO Añadir indicaciones importantes:
    # TODO Documentso words personales
    # TODO Que no sean confidenciales
    # TODO Escoger bien el contexto etc.
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
        clave = st.text_input("clave", label_visibility="hidden", help="Tu clave personal dada por el administrador.")
    añadir_salto()
    texto("Especifica el contexto de tu documento", font_family='Dancing Script', font_size=20, centrar=True)
    contexto = st.selectbox("contexto", 
                                options=LISTA_ESPECIALIDADES, 
                                label_visibility="hidden",
                                index=0)
    añadir_salto()
    # Cargar el documento
    texto("Carga tu documento Word", font_family='Dancing Script', font_size=20, centrar=True)
    documento = st.file_uploader("documento", label_visibility="hidden", type=["docx"], on_change=reset_all)
    if documento and not st.session_state.get('parsed_document'):
        # TODO Meter todo en una pipeline ?
        # Creamos la barra de progreso
        preprocess_bar = st.progress(0)
        t_wait = 0.2
        # Descomprimimos el documento
        preprocess_bar.progress(0.25, 'Descomprimiendo el documento...')
        extract_xml(BytesIO(documento.read()))
        time.sleep(t_wait)
        # Extraemos los textos del document.xml y sus elementos para poder modificar
        preprocess_bar.progress(0.5, 'Extrayendo los textos...')
        text, xml_elements_list = get_text_elements()
        num_words = get_num_words(text)
        time.sleep(t_wait)     
        # Sacamos el idioma del texto
        preprocess_bar.progress(0.75, 'Identificando el idioma del documento...')
        idioma_es, idioma_en = get_language(text)
        time.sleep(t_wait)
        # Sacamos el tema del documento
        preprocess_bar.progress(0.9, 'Identificando la temática del documento...')
        topic:TopicResponse = get_topic(text, idioma_es, documento.name)
        preprocess_bar.progress(0.95, 'Estimando costes...')
        estimated_cost = estimate_openai_cost(num_words)
        time.sleep(t_wait)
        # Guardamos todo en sesión
        preprocess_bar.progress(1, 'Guardando en sesión...')
        save_in_session(['text', 'xml_elements_list', 'idioma_es', 'idioma_en', 'tematica',
                            'num_words', 'estimated_cost'], 
                        [text, xml_elements_list, idioma_es, idioma_en, topic.response,
                            num_words, estimated_cost])
        # Acumulamos los costes
        accumulate_in_session(['real_total_cost'], [topic.total_cost])
        time.sleep(t_wait)
        preprocess_bar.empty()
        # Activamos la flag para indicar que se ha cargado archivo correctamente
        activate_flag()
        # Escribimos el número de palabras al usuario
    if st.session_state.get('num_words') is not None:
        texto(f"Tu documento tiene {st.session_state['num_words']} palabras", font_family='Dancing Script', font_size=20, centrar=True)

    añadir_salto()
    # Botón para traducir
    traducir = st.button(label="Traducir", use_container_width=True)
    if traducir and st.session_state.get('parsed_document'):
        # Creamos la barra de progreso
        validation_bar = st.progress(0)
        t_wait = 0.2

        # VALIDACIONES
        # Verificar que el idioma destino != idioma del documento
        validation_bar.progress(0.16, 'Verificando idiomas...')
        time.sleep(t_wait)
        if st.session_state['idioma_es'].lower() == idioma.lower():
            show_error(f'El idioma del documento y el idioma de destino no pueden coincidir.', validation_bar)         
        # Verificar si la clave está insertada
        validation_bar.progress(0.16, 'Verificando clave...')
        time.sleep(t_wait)
        if not clave:
            show_error('Inserta una clave válida para continuar.', validation_bar)
        # Verificar si clave (o apikey) existe
        validation_bar.progress(0.16, 'Verificando clave...')
        time.sleep(t_wait)
        if not exists_apikey(clave, db_handler):
            show_error("La clave no es válida.", validation_bar)
        # Verificar si apikey de admin
        validation_bar.progress(0.16, 'Verificando clave...')
        time.sleep(t_wait)
        # Mostramos nombre del usuario
        user_name = db_handler.get_nombre(clave)
        texto(f"Accediendo a la clave de {user_name}", font_family='Dancing Script', font_size=20, centrar=True)
        if not apikey_is_admin(clave, db_handler):            
            # Verificar si usuario activo
            validation_bar.progress(0.16, 'Verificando usuario activo...')
            time.sleep(t_wait)
            if not apikey_is_active(clave, db_handler):
                show_error("Tu clase no está activada. Contacta con el administrador.", validation_bar)
            # Verificar si usuario palabras consumidas + palabras del documento < palabras contratadas
            validation_bar.progress(0.16, 'Verificando palabras restantes...')
            time.sleep(t_wait)
            if not has_words_left(clave, num_words, db_handler):
                show_error(f"Has sobrepasado tu límite de palabras a traducir: {db_handler.get_palabras_limite(clave)}")
        # Guardamos la api key y el modelo en sesión
        save_in_session(['openai_apikey', 'model'], [db_handler.get_api_key(clave), db_handler.get_model(clave)])
        validation_bar.progress(1, 'Validaciones completadass')
        time.sleep(t_wait)
        validation_bar.empty()

        # TRADUCCIONES
        # A Partir de aqui usamos la api key
        translation_bar = st.progress(0)
        start = time.perf_counter()
        try:
            translation_loop(
                apikey=st.session_state.get('openai_apikey'),
                model=st.session_state.get('model'),
                objects_list=st.session_state['xml_elements_list'],
                progress_bar=translation_bar,
                chain_params={
                'origin_lang': st.session_state['idioma_es'],
                'destiny_lang': idioma,
                'doc_features': st.session_state['tematica'],
                'doc_context': contexto,
            })
        except Exception as exc:
            show_error(f"Ha ocurrido un error: {exc}", translation_bar)
        # TODO Visualizar tiempo transcurrido
        texto('Traducción finalizada.', font_family='Dancing Script', font_size=20, centrar=True)
        # TODO Actualizar en db si todo ha salido bien el número de palabras del usuario y el coste.
        # TODO Mostrar botón para descargar el archivo traducido.

    st.session_state

    # Footer
    put_footer()


if __name__ == '__main__':
    main()