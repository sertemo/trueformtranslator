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
import os
from pathlib import Path
import random
import time
# librerías de terceros
import streamlit as st
from streamlit import delta_generator
# librerías del proyecto
from backend.builder import build_docx_from_xml
from backend.db import UserDBHandler
from backend.extractor import (get_text_from_docx,
                                extract_word_to_xml, 
                                delete_xml_path, 
                                get_text_elements_and_tree,
                                get_language,
                                get_topic,
                                get_num_words,
                                get_vocabulary,
                                )
from backend.models import OpenAIResponse
from backend.paths import WORD_FOLDER
from backend.translator import (translate,
                                )
from backend.validator import (exists_apikey, 
                                apikey_is_admin,
                                apikey_is_active,
                                has_words_left,
                                are_special_char
                                )
from backend.xml_validator import all_xml_files_good
from backend.utils import (estimate_openai_cost,
                            get_datetime_formatted,
                            add_suffix_to_filename,
                            get_to_extract_list,
                            wait_randomly,
                            )
from streamlit_utils import (texto, 
                            añadir_salto, 
                            footer,
                            accumulate_in_session,
                            activate_flags,
                            deactivate_flags,
                            save_in_session)


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

# Funciones específicas del proyecto
def init() -> None:
    """Inicializa variables de sesión necesarias
    """
    if st.session_state.get("parsed_document") is None:
        st.session_state["parsed_document"] = False
    if st.session_state.get('diccionary') is None:
        st.session_state['diccionary'] = {}
    if st.session_state.get('translated_document') is None:
        st.session_state['translated_document'] = False

def reset_all() -> None:
    """Desactiva todas las flags y borra la ruta xml completa
    Borra toda la sesión
    """
    deactivate_flags(['parsed_document', 'translated_document'])
    delete_xml_path()
    st.session_state.clear()

def show_error_and_stop(msg:str, progress_bar_list:list[delta_generator.DeltaGenerator]=None) -> None:
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

def extract_translate_replace(
        *,
        apikey:str,
        model:str,
        document_words:int,
        target_language:str,
        filename:str,
        to_extract_list:list[Path],
        progress_bar_list:list[delta_generator.DeltaGenerator],
        chain_params:dict
        ) -> None:
    # Unpack de las progress bar
    document_bar, element_bar = progress_bar_list
    # Contamos el número de documentos a traducir
    n_documentos = len(to_extract_list)
    step_document = 1 / n_documentos

    for idx, doc in enumerate(to_extract_list, start=1):
        document_bar.progress(idx * step_document, f"Gestionando documento {idx}/{n_documentos}...")
        # Creamos el tree y el root
        text_elements, tree = get_text_elements_and_tree(doc)
        n_elements = len(text_elements)
        # Hacemos un sanity check: si n_elements > que document_words, algo se ha parseado mal
        if n_elements > document_words:
            show_error_and_stop("El documento no se ha extraído correctamente debido a su formateo.\
                                    Por favor, asegúrate de que el documento haya sido escrito por ti,", [document_bar, element_bar])
        step_process = 1 / n_elements
        for id, (element, text) in enumerate(text_elements, start=1):
            element_bar.progress(id * step_process, f"Traduciendo al {target_language} elemento {id}/{n_elements}")
            # Validaciones de traducción
            # No traducir caracteres etc.
            if (len(text) == 1) or text.isspace() or text.isdigit() or text.isnumeric() or are_special_char(text.strip()):
                element.text = text
                continue
            # Buscamos en el diccionario si el texto sin espacios ya ha sido traducido
            if (transl:=st.session_state['diccionary'].get(text.strip())) is not None:
                element.text = transl
                continue
            # Gestionamos la 'memoria' pasando texto anterior y posterior al prompt de traducción
            # Solo para el document.xml
            if doc == "document.xml":
                texto_bruto:str = st.session_state['docx_text']
                indice_init = texto_bruto.find(text)
                indice_anterior = max(0, indice_init - 100) # Ojo índices del principio
                texto_anterior = texto_bruto[indice_anterior:indice_init]
                texto_anterior = "..." + " ".join(texto_anterior.split()[1:]) # Quitamos primera palabra y añadimos ...
                # Sacamos el texto posterior
                indice_fin = indice_init + len(text)
                indice_posterior = min(indice_fin + 100, len(text))
                texto_posterior =  texto[indice_fin: indice_posterior]
                texto_posterior = " ".join(texto_posterior.split()[:-1]) + "..."
            else:
                texto_anterior = "..."
                texto_posterior = "..."
            # Añadimos texto_anterior y posterior a la chain_params
            chain_params['texto_anterior'] = texto_anterior
            chain_params['texto_posterior'] = texto_posterior
            # Pasamos por el traductor
            response:OpenAIResponse = translate(apikey=apikey,
                                            model=model,
                                            text=text,
                                            **chain_params)
            translated_text:str = response.response
            translation_cost:float = response.total_cost
            # Si es una sola palabra añadimos al diccionario quitando espacios
            if len(text.split()) == 1:
                st.session_state['diccionary'][text.strip()] = translated_text.strip()
            # Verificamos que los espacios al principio y al final coincidan con el texto original
            # Si no coinciden añadimos espacios pertinentes.
            if text[0].isspace() and (not translated_text[0].isspace()):
                translated_text = " " + translated_text
            if text[-1].isspace() and (not translated_text[-1].isspace()):
                translated_text = translated_text + " " 
            # Sustituimos el texto traducido en el elemento
            element.text = translated_text
            # Acumulamos coste en sesión
            accumulate_in_session(['real_total_cost'], [translation_cost])
            # Cooldown aleatorio con probabilidad del 50%
            if random.random() < 0.5:
                wait_randomly(2)
        # Limpiamos la barra de progreso
        element_bar.empty()
        # Guardamos el arbol en el archivo
        tree.write(doc)
    # Traducimos el nombre del documento
    response:OpenAIResponse = translate(apikey=apikey,
                                            model=model,
                                            text=filename,
                                            **chain_params)
    translated_filename = response.response
    translation_cost = response.total_cost
    # Acumulamos los costes en sesión
    accumulate_in_session(['real_total_cost'], [translation_cost])
    # Guardamos en sesión el nombre traducido
    save_in_session(['translated_filename'], [translated_filename])
    # Limpiamos la barra de documentos
    document_bar.empty()

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
    texto_subtitulo("Consideraciones importantes")
    texto_descriptivo("- No se almacena ninguna información, sin embargo no se recomiendan documentos confidenciales.")
    texto_descriptivo("- Para una traducción óptima se recomienda que el archivo word haya sido creado por el usuario.")
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
    # EXTRACCION
    texto_descriptivo("Carga tu documento Word")
    documento = st.file_uploader("documento", label_visibility="hidden", type=["docx"], on_change=reset_all)
    if documento and not st.session_state.get('parsed_document'):
        # Guardamos el nombre del archivo en sesión
        nombre_archivo, _ = os.path.splitext(documento.name)
        # Creamos la barra de progreso
        preprocess_bar = st.progress(0)
        t_wait = 0.2        
        # Extraemos los textos
        preprocess_bar.progress(0.25, 'Extrayendo los textos...')
        docx_text = get_text_from_docx(BytesIO(documento.read()))
        num_words = get_num_words(docx_text)
        vocabulary = get_vocabulary(docx_text)
        time.sleep(t_wait)     
        # Sacamos el idioma del texto
        preprocess_bar.progress(0.50, 'Identificando el idioma del documento...')
        # Para el idioma pasamos el primer documento de la lista to_extract, que será siempre el document.xml
        idioma_es, idioma_en = get_language(docx_text)
        time.sleep(t_wait)
        # Sacamos el tema del documento
        preprocess_bar.progress(0.75, 'Identificando la temática del documento...')
        # Para sacar el tema usamos el primer documento (document.xml)
        topic:OpenAIResponse = get_topic(docx_text, idioma_es, documento.name)
        preprocess_bar.progress(0.95, 'Estimando costes...')
        estimated_cost = estimate_openai_cost(num_words)
        time.sleep(t_wait)
        # Guardamos todo en sesión
        preprocess_bar.progress(1, 'Guardando en sesión...')
        save_in_session(['nombre_archivo', 'docx_text', 'idioma_es', 'idioma_en', 'tematica',
                            'num_words', 'estimated_cost', 'vocabulary', 'vocab_size'], 
                        [nombre_archivo, docx_text, idioma_es, idioma_en, topic.response,
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
            show_error_and_stop(f'El idioma del documento y el idioma de destino no pueden coincidir.', [validation_bar])         
        # Verificar si la clave está insertada
        validation_bar.progress(0.16, 'Verificando clave...')
        time.sleep(t_wait)
        if not clave:
            show_error_and_stop('Inserta una clave válida para continuar.', [validation_bar])
        # Verificar si clave (o apikey) existe
        validation_bar.progress(0.16, 'Verificando clave...')
        time.sleep(t_wait)
        if not exists_apikey(clave, db_handler):
            show_error_and_stop("La clave no es válida.", [validation_bar])
        # Verificar si apikey de admin
        validation_bar.progress(0.16, 'Verificando clave...')
        time.sleep(t_wait)        
        if not apikey_is_admin(clave, db_handler):            
            # Verificar si usuario activo
            validation_bar.progress(0.16, 'Verificando usuario activo...')
            time.sleep(t_wait)
            if not apikey_is_active(clave, db_handler):
                show_error_and_stop("Tu clase no está activada. Contacta con el administrador.", [validation_bar])
            # Verificar si usuario palabras consumidas + palabras del documento < palabras contratadas
            validation_bar.progress(0.16, 'Verificando palabras restantes...')
            time.sleep(t_wait)
            if not has_words_left(clave, num_words, db_handler):
                show_error_and_stop(f"Has sobrepasado tu límite de palabras a traducir: {db_handler.get_palabras_limite(clave)}")
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
        document_bar = st.progress(0)
        element_bar = st.progress(0)
        start = time.perf_counter()
        # Sacamos los archivos xml del documento
        extract_word_to_xml(BytesIO(documento.read()))
        # Confeccionamos la lista de documentos xml a parsear
        to_extract_list = get_to_extract_list(WORD_FOLDER)
        # lanzamos el bucle de traducción y reemplazo
        try:
            extract_translate_replace(
                apikey=st.session_state.get('openai_apikey'),
                model=st.session_state.get('model'),
                target_language=idioma,
                filename=st.session_state.get('nombre_archivo'),
                to_extract_list=to_extract_list,
                document_words=st.session_state['num_words'],
                progress_bar_list=[document_bar, element_bar],
                chain_params={
                'origin_lang': st.session_state['idioma_es'],
                'destiny_lang': idioma,
                'doc_features': st.session_state['tematica'],
                'doc_context': contexto,
            })
        except Exception as exc:
            show_error_and_stop(f"Ha ocurrido un error: {exc}", [document_bar, element_bar])
        # Pasamos por el validator de XML para para en caso de que haya salido algo mal
        xml_ok, error = all_xml_files_good(WORD_FOLDER)
        if not xml_ok:
            show_error_and_stop(f'Ha habido un error con los XML: {", ".join(error)}. Inténtalo con otro archivo.')
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
    
        # RECONTRUCCION  Y DESCARGA DEL DOCUMENTO
    if st.session_state.get('translated_document'):        
        # Generamos de nuevo el archivo Word
        archivo_descarga = add_suffix_to_filename(documento.name, st.session_state.get('translated_filename'))
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