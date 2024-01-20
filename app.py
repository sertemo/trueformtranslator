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
import time
# librerías de terceros
import pandas as pd
import streamlit as st
from streamlit import delta_generator
# librerías del proyecto
from backend.builder import modify_text_element, build_docx_from_xml
from backend.db import UserDBHandler
from backend.extractor import (extract_word_to_xml, 
                                delete_xml_path, 
                                get_text_elements_and_tree,
                                get_language,
                                get_topic,
                                get_num_words,
                                get_vocabulary,
                                )
from backend.models import XmlDocument, OpenAIResponse
from backend.paths import WORD_FOLDER
from backend.translator import (translate,
                                )
from backend.validator import (exists_apikey, 
                                apikey_is_admin,
                                apikey_is_active,
                                has_words_left,
                                are_special_char
                                )
from backend.utils import (estimate_openai_cost,
                            get_datetime_formatted,
                            add_suffix_to_filename,
                            get_to_extract_list,
                            )
from streamlit_utils import texto, añadir_salto, footer


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
# Instanciamos distintos tipos de mensajes
texto_error = partial(texto, font_family='Dancing Script', font_size=20, centrar=True, color='#FF0033')
texto_descriptivo = partial(texto, font_family='Dancing Script', font_size=20, centrar=True)
texto_titulo = partial(texto, font_family='Rubik Doodle Shadow', font_size=60, centrar=True)
texto_subtitulo = partial(texto, font_family='Dancing Script', centrar=True)

# Funciones
def init() -> None:
    """Inicializa variables de sesión necesarias
    """
    if st.session_state.get("parsed_document") is None:
        st.session_state["parsed_document"] = False
    if st.session_state.get('diccionary') is None:
        st.session_state['diccionary'] = {}
    if st.session_state.get('translated_document') is None:
        st.session_state['translated_document'] = False

def deactivate_flags(flags:list[str]) -> None:
    """desactiva las flags pasadas haciéndola False
    """
    for flag in flags:
        st.session_state[flag] = False

def activate_flags(flags:list[str]) -> None:
    """activa las flags pasadas poniéndola True
    """
    for flag in flags:
        st.session_state[flag] = True

def reset_all() -> None:
    """Desactiva todas las flags y borra la ruta xml completa
    Borra toda la sesión
    """
    deactivate_flags(['parsed_document', 'translated_document'])
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

def show_error(msg:str, progress_bar_list:list[delta_generator.DeltaGenerator]=None) -> None:
    """Función que realiza 4 cosas:
    - muestra mensaje de error
    - vacía las barras de progreso si hay
    - muestra el footer de la app
    - para la ejecución de la app

    Parameters
    ----------
    msg : str
        _description_
    progress_bar : list[DeltaGenerator]
        _description_
    """
    texto_error(msg)
    put_footer()
    if progress_bar_list is not None:
        if not isinstance(progress_bar_list, list):
            raise TypeError(f"Debes pasar una lista de progress bar. Has pasado: {type(progress_bar_list)}")
        [barra.empty() for barra in progress_bar_list]
    st.stop()

def wait_randomly(max:int=1):
    """espera un numero max de segundos de forma aleatoria

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
        xmldocuments_list:list[XmlDocument], 
        progress_bar_list:list[delta_generator.DeltaGenerator],
        chain_params:dict) -> None:
    # Contamos el número de documentos a traducir
    n_documentos = len(xmldocuments_list)
    step_document = 1 / n_documentos
    # unpackeamos las progress_bar. En esta caso sabemos que van a haber 2.
    document_pbar, element_pb = progress_bar_list
    # Iteramos sobre los documentos
    for idx, xmldocument in enumerate(xmldocuments_list, start=1):
        document_pbar.progress(step_document * idx, f'Traduciendo documento {idx}/{n_documentos}...')
        n_elements = len(xmldocument)
        step_element = 1 / n_elements
        # Iteramos sobre el documento, que devuelve los xmlelements:
        for id, xmlelement in enumerate(xmldocument, start=1):
            element_pb.progress(step_element * id, f"Traduciendo elemento {id}/{n_elements}...")
            # Sacamos el texto del objeto
            texto:str = xmlelement.text
            # No traducir caracteres etc.
            if (len(texto) == 1) or texto.isspace() or texto.isdigit() or texto.isnumeric() or are_special_char(texto.strip()):
                xmlelement.translation = texto
                continue
            # Buscamos en el diccionario si el texto sin espacios ya ha sido traducido
            if (transl:=st.session_state['diccionary'].get(texto.strip())) is not None:
                xmlelement.translation = transl
                continue
            # Pasamos por el traductor y sacamos traducción y coste
            response:OpenAIResponse = translate(apikey, model, text=texto, **chain_params)
            translated_text:str = response.response
            translation_cost:float = response.total_cost        
            # Si es una sola palabra añadimos al diccionario quitando espacios
            if len(texto.split()) == 1:
                st.session_state['diccionary'][texto.strip()] = translated_text.strip()
            # Verificamos que los espacios al principio y al final coincidan con el texto original
            # Si no coinciden añadimos espacios pertinentes.
            if texto[0].isspace() and (not translated_text[0].isspace()):
                translated_text = " " + translated_text
            if texto[-1].isspace() and (not translated_text[-1].isspace()):
                translated_text = translated_text + " "        
            # Actualizamos el objeto XmlElement añadiendo un campo traducido y el coste en sesión
            xmlelement.translation = translated_text
            accumulate_in_session(['real_total_cost'], [translation_cost])
            # Cooldown aleatorio con probabilidad del 50%
            if random.random() < 0.5:
                wait_randomly(2)
        # Al acabar todos los elementos, borramos la barra de elementos
        element_pb.empty()
    # Al acabar todos los documentos, borramos la barra de documentos
    document_pbar.empty()

# MAIN FUNCTION
def main() -> None:
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
    texto_titulo("TrueForm Translator")
    # Descripción
    texto_subtitulo("Traduce tus propios documentos Word a un idioma de tu elección.")
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
        texto_descriptivo("Introduce tu clave")
        clave = st.text_input("clave", label_visibility="hidden", help="Tu clave personal dada por el administrador.")
    añadir_salto()
    texto_descriptivo("Especifica el contexto de tu documento")
    contexto = st.selectbox("contexto", 
                                options=LISTA_ESPECIALIDADES, 
                                label_visibility="hidden",
                                index=0)
    añadir_salto()
    # EXTRACCIONES
    texto_descriptivo("Carga tu documento Word")
    documento = st.file_uploader("documento", label_visibility="hidden", type=["docx"], on_change=reset_all)
    if documento and not st.session_state.get('parsed_document'):
        # TODO Meter todo en una pipeline ?
        # Creamos la barra de progreso
        preprocess_bar = st.progress(0)
        t_wait = 0.2
        # Descomprimimos el documento
        preprocess_bar.progress(0.25, 'Descomprimiendo el documento...')
        extract_word_to_xml(BytesIO(documento.read()))
        time.sleep(t_wait)
        # Extraemos los textos del document.xml y sus elementos para poder modificar
        # TODO Aqui verificar si hay header y footer y extraer sus textos
        preprocess_bar.progress(0.5, 'Extrayendo los textos...')
        # Creamos una lista de extraccion con todos los xml que hay que parsear (headers, footers si hay etc)
        to_extract:list = get_to_extract_list(WORD_FOLDER)
        xmldocument_list:list[XmlDocument]= [get_text_elements_and_tree(doc) for doc in to_extract]
        num_words = get_num_words(xmldocument_list)
        vocabulary = get_vocabulary(xmldocument_list)
        time.sleep(t_wait)     
        # Sacamos el idioma del texto
        preprocess_bar.progress(0.75, 'Identificando el idioma del documento...')
        # Para el idioma pasamos el primer documento de la lista to_extract, que será siempre el document.xml
        idioma_es, idioma_en = get_language(xmldocument_list[0].text)
        time.sleep(t_wait)
        # Sacamos el tema del documento
        preprocess_bar.progress(0.9, 'Identificando la temática del documento...')
        # Para sacar el tema usamos el primer documento (document.xml)
        topic:OpenAIResponse = get_topic(xmldocument_list[0].text, idioma_es, documento.name)
        preprocess_bar.progress(0.95, 'Estimando costes...')
        estimated_cost = estimate_openai_cost(num_words)
        time.sleep(t_wait)
        # Guardamos todo en sesión: Tree y elementos de texto para poder traducir y recuperar posiciones
        preprocess_bar.progress(1, 'Guardando en sesión...')
        save_in_session(['xml_document_list', 'idioma_es', 'idioma_en', 'tematica',
                            'num_words', 'estimated_cost', 'vocabulary', 'vocab_size'], 
                        [xmldocument_list, idioma_es, idioma_en, topic.response,
                            num_words, estimated_cost, vocabulary, len(vocabulary)])
        # Acumulamos los costes
        accumulate_in_session(['real_total_cost'], [topic.total_cost])
        time.sleep(t_wait)
        preprocess_bar.empty()
        # Activamos la flag para indicar que se ha cargado archivo correctamente
        activate_flags(['parsed_document'])
        # Escribimos el número de palabras al usuario
    if st.session_state.get('num_words') is not None:
        texto_descriptivo(f"Tu documento tiene {st.session_state['num_words']} palabras")

    añadir_salto()
    # Botón para traducir
    traducir = st.button(label="Traducir", use_container_width=True)
    if traducir and st.session_state.get('parsed_document') and not st.session_state.get('translated_document'):
        # Creamos la barra de progreso
        validation_bar = st.progress(0)
        t_wait = 0.2

        # VALIDACIONES
        # Verificar que el idioma destino != idioma del documento
        validation_bar.progress(0.16, 'Verificando idiomas...')
        time.sleep(t_wait)
        if st.session_state['idioma_es'].lower() == idioma.lower():
            show_error(f'El idioma del documento y el idioma de destino no pueden coincidir.', [validation_bar])         
        # Verificar si la clave está insertada
        validation_bar.progress(0.16, 'Verificando clave...')
        time.sleep(t_wait)
        if not clave:
            show_error('Inserta una clave válida para continuar.', [validation_bar])
        # Verificar si clave (o apikey) existe
        validation_bar.progress(0.16, 'Verificando clave...')
        time.sleep(t_wait)
        if not exists_apikey(clave, db_handler):
            show_error("La clave no es válida.", [validation_bar])
        # Verificar si apikey de admin
        validation_bar.progress(0.16, 'Verificando clave...')
        time.sleep(t_wait)        
        if not apikey_is_admin(clave, db_handler):            
            # Verificar si usuario activo
            validation_bar.progress(0.16, 'Verificando usuario activo...')
            time.sleep(t_wait)
            if not apikey_is_active(clave, db_handler):
                show_error("Tu clase no está activada. Contacta con el administrador.", [validation_bar])
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

        # Mostramos nombre del usuario y palabras acumuladas del total
        user_name = db_handler.get_nombre(clave)
        words_sofar = db_handler.get_palabras_acumulado(clave)
        words_limit = db_handler.get_palabras_limite(clave)
        texto_descriptivo(f"Accediendo a la clave de {user_name}: {words_sofar}/{words_limit}")

        # TRADUCCIONES
        # A Partir de aqui usamos la api key
        translation_document_bar = st.progress(0)
        translation_element_bar = st.progress(0)
        start = time.perf_counter()
        try:
            translation_loop(
                apikey=st.session_state.get('openai_apikey'),
                model=st.session_state.get('model'),
                xmldocuments_list=st.session_state['xml_document_list'],
                progress_bar_list=[translation_document_bar, translation_element_bar],
                chain_params={
                'origin_lang': st.session_state['idioma_es'],
                'destiny_lang': idioma,
                'doc_features': st.session_state['tematica'],
                'doc_context': contexto,
            })
        except Exception as exc:
            show_error(f"Ha ocurrido un error: {exc}", [translation_document_bar, translation_element_bar])
        # Activamos la flag de traducción
        activate_flags(['translated_document'])
        # Visualizar tiempo transcurrido
        añadir_salto()
        minutos = (time.perf_counter() - start) // 60
        segundos = (time.perf_counter() - start) % 60
        texto_descriptivo(f'Traducción finalizada. Tiempo transcurrido: {minutos:.0f} minutos y {segundos:.0f} segundos.') 
        try:
            # Actualizamos la fecha actual y los campos último coste y últimas palabras
            db_handler.update('clave', clave, {'ultimo_uso': get_datetime_formatted(),})
            db_handler.update('clave', clave, {'ultimo_coste': st.session_state['real_total_cost']})
            db_handler.update('clave', clave, {'ultimo_palabras': st.session_state['num_words']})
            # Incrementamos en db las palabras traducidas y el coste
            db_handler.increment_number('clave', clave, 'palabras_acumulado', st.session_state['num_words'])
            db_handler.increment_number('clave', clave, 'coste_acumulado', st.session_state['real_total_cost'])
        except Exception as exc:
            texto_error(f'Se ha producido el siguiente error al guardar los datos: {exc}')
    
        # RECONTRUCCION DEL DOCUMENTO
    if st.session_state.get('translated_document'):        
        # Modificamos los elementos guardados en sesión por su texto traducido
        # Cambiamos los elementos por los textos traducidos y escribimos los arboles
        modify_text_element(st.session_state['xml_document_list'])
        # Generamos de nuevo el archivo Word
        archivo_descarga = add_suffix_to_filename(documento.name, 'translated')
        build_docx_from_xml(archivo_descarga)
        # Mostrar botón para descargar el archivo traducido.
        añadir_salto()
        with open(archivo_descarga, "rb") as file:
            st.download_button(
                label = "Descargar",
                data = file,
                file_name = archivo_descarga,
                mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                #on_click=update_counter, # TODO: Agregar contador de veces que se descarga archivo
                use_container_width=True,
                help="Descarga el documento traducido"
            )

    st.session_state

    # Footer
    put_footer()


if __name__ == '__main__':
    main()