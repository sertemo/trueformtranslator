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

# Script con el código relacionado con la creación del nuevo documento Word ya traducido

import os
import xml.etree.ElementTree as ET
import zipfile

from dotenv import load_dotenv

from .paths import XML_FOLDER

load_dotenv()

def build_docx_from_xml(archivo_destino:str, directorio_fuente:str=XML_FOLDER) -> None:
    """Crea un archivo docx a partir de su árbol de documentos xml

    Parameters
    ----------
    archivo_destino : str
        _description_
    directorio_fuente : str, optional
        _description_, by default XML_FOLDER
    """
    # Crea un archivo zip con la opción de escritura
    with zipfile.ZipFile(archivo_destino, 'w') as docx:
        # Camina por el directorio fuente
        for root, dirs, files in os.walk(directorio_fuente):
            for file in files:
                # Crea el path completo del archivo
                full_path = os.path.join(root, file)
                # Crea el path relativo que va dentro del zip,
                # esto es importante para mantener la estructura
                rel_path = os.path.relpath(full_path, directorio_fuente)
                # Agrega el archivo al zip
                docx.write(full_path, rel_path)
