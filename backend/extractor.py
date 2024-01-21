# Copyright 2024 Sergio Tejedor Moreno

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Script con el código relacionado con la extracción de la información
# y/o propiedades del documento Word


import shutil
import zipfile

from docx import Document
from langchain_community.callbacks import get_openai_callback
from langdetect import detect, DetectorFactory
from pathlib import Path
import pycountry
from textblob import TextBlob
import xml.etree.ElementTree as ET

from .chains import get_topic_chain
from .models import OpenAIResponse
from .paths import XML_FOLDER
from .utils import get_chunk, clean_word

def get_text_from_docx(document:bytes) -> str:
    """Devuelve el texto extraido de un documento docx

    Parameters
    ----------
    document : bytes
        _description_

    Returns
    -------
    str
        _description_
    """
    doc:Document = Document(document)
    return " ".join(para.text for para in doc.paragraphs)

def extract_word_to_xml(document:bytes) -> None:
    """Dado un documento docx en bytes, lo descomprime
    en la carpeta XML_PATH

    Parameters
    ----------
    document : bytes
        El documento docx a descomprimir
    """
    with zipfile.ZipFile(document, 'r') as zip_ref:
        zip_ref.extractall(XML_FOLDER)

def delete_xml_path() -> None:
    """Elimina todo el directorio donde están almacenados los archivos xml.
    Elimina todo el arbol
    """
    if XML_FOLDER.exists():
        shutil.rmtree(XML_FOLDER)

def get_text_elements_and_tree(file_xml_path:Path) -> tuple[list[tuple[ET.Element, str]], ET.ElementTree]:
    """Dado un archivo xml extrae cada elemento de texto y devuelve una lista de tuplas 
    con los elementos y sus textos y el tree del documento

    Returns
    -------
    list[tuple[ET.Element, str]]
        tupla con:
        - lista de tuplas con (Elemento, texto del elemento)
        - El tree del documento
    """
    # Cargamos archivo document.xml donde está el texto
    tree = ET.parse(file_xml_path)
    root = tree.getroot()
    # Espacio de nombres utilizado en el documento Word XML
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'wpc': "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
        'wpi': "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
        'wps': "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
        'wp': "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    }
    # Encontrar todos los elementos de texto y extraer el texto
    text_elements = []
    for paragraph in root.iterfind('.//w:p', namespaces):
        for text_elem in paragraph.iterfind('.//w:t', namespaces):
            text_elements.append((text_elem, text_elem.text))
    # Devolvemos la lista y el tree
    return text_elements, tree

def get_language(corpus:str) -> tuple[str]:
    """Dado un texto en str, devuelve el idioma del texto en
    español y en inglés

    Parameters
    ----------
    corpus : str
        Texto a extraer el idioma

    Returns
    -------
    tuple[str]
        Tupla con el nombre del idioma en español y en inglés:
        idioma_es, idioma_en
    """
    # Para que sea determinista
    DetectorFactory.seed = 0
    # Escribimos el texto a traducir
    # Sacamos el idioma en formato ISO 639 y en lenguaje natural
    idioma_iso = detect(corpus)
    idioma_en = pycountry.languages.get(alpha_2=idioma_iso).name
    # Como lo saca en inglés, pasamos por textblob para tenerlo en español
    idioma_es = TextBlob(idioma_en).translate(from_lang='en', to='es').string
    return idioma_es, idioma_en

def get_num_words(corpus:str) -> int:
    """Dado un texto, devuelve el número de palabras aproximado.

    Parameters
    ----------
    corpus : str
        _description_

    Returns
    -------
    int
        _description_
    """
    return len(corpus.split())

def get_vocabulary(corpus:str) -> set:
    """Devuelve un set con todas las palabras diferentes del documento.

    Parameters
    ----------
    corpus : str
        _description_

    Returns
    -------
    set
        _description_
    """

    return set(map(clean_word, corpus.split()))

def get_topic(corpus:str, language:str, doc_name:str) -> OpenAIResponse:
    """Dado un corpus en formato string y un idioma,
    devuelve el tipo de documento o la temática del documento
    junto con el coste de la llamada a la API de OpenAI.
    Devuelve un objeto con los dos atributos

    Parameters
    ----------
    corpus : str
        texto del documento
    language : str
        idioma del documento

    Returns
    -------
    TopicResponse
        (respuesta, coste)
    """
    # Lo primero es crear un 'dataset'. Spliteamos por salto de linea
    dataset = corpus.split('.')
    # Sacamos dos chunk de todo el documento para enviar a openai
    #? No sería mejor sacar 3 chunks uno del principio otro del medio y otro del final de documento ?
    chunk_1 = get_chunk(dataset)
    chunk_2 = get_chunk(dataset)
    # Instanciamos la chain
    chain = get_topic_chain()
    # Envolvemos en callback para sacar el coste
    with get_openai_callback() as cb:
        response = chain.invoke({
            'idioma': language,
            'extracto_1': chunk_1,
            'extracto_2': chunk_2,
            'nombre_documento': doc_name,
        })
        coste_total = cb.total_cost
    # Creamos un objeto para retornar    
    return OpenAIResponse(response, coste_total)
