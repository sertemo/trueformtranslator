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

Script con el código relacionado con la extracción de la información
y/o propiedades del documento Word
    """

from docx import Document
from langdetect import detect, DetectorFactory
import nltk
from pathlib import Path
import pycountry
import shutil
from textblob import TextBlob
import xml.etree.ElementTree as ET
import zipfile

XML_FOLDER = Path('backend/docx_xml')
DOCUMENT_XML_PATH = XML_FOLDER / Path('word') / 'document.xml'


def extract_xml(document:bytes) -> None:
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

def get_text_elements() -> tuple[str, list]:
    """Función que extrae el texto y los elementos texto del archivo
    'document.xml' para poder traducir posteriormente.
    Devuelve una tupla con :
        - el texto completo del documento en str
        - lista con tuplas de elementos y su texto correspondiente

    Returns
    -------
    str
        El texto del documento
    list
        lista de tuplas con todos los elementos y los textos de cada elemento
    """
    # Cargamos archivo document.xml donde está el texto
    tree = ET.parse(DOCUMENT_XML_PATH)
    root = tree.getroot()
    # Espacio de nombres utilizado en el documento Word XML
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    # Encontrar todos los elementos de texto y extraer el texto
    text_elements = []
    texto = """"""    
    for paragraph in root.iterfind('.//w:p', namespaces):
        para_text = []
        for text_elem in paragraph.iterfind('.//w:t', namespaces):
            para_text.append(text_elem.text) # Almacenamos aqui solo el texto para usarlo para sacar idioma o temática
            text_elements.append((text_elem, text_elem.text))
        texto += "\n" + " ".join(para_text)
    return texto, text_elements

def get_language(text:str) -> tuple[str]:
    """Dado un texto en str, devuelve el idioma del texto en
    español y en inglés

    Parameters
    ----------
    text : str
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
    idioma_iso = detect(text)
    idioma_en = pycountry.languages.get(alpha_2=idioma_iso).name
    # Como lo saca en inglés, pasamos por textblob para tenerlo en español
    idioma_es = TextBlob(idioma_en).translate(from_lang='en', to='es').string
    return idioma_es, idioma_en

def get_topics(corpus:list, language:str):
    nltk.download('stopwords')
    pass