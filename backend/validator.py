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

# Script con el código relacionado con funciones de validación
import re
import string

from .db import UserDBHandler

def exists_apikey(clave:str, handler:UserDBHandler) -> bool:
    """True si la apikey existe en base de datos

    Parameters
    ----------
    apikey : str
        _description_
    handler : UserDBHandler
        _description_

    Returns
    -------
    bool
        _description_
    """
    if handler.get_api_key(clave) is not None:
        return True
    return False

def apikey_is_admin(clave:str, handler:UserDBHandler) -> bool:
    """True si la apikey es de admin

    Parameters
    ----------
    apikey : str
        _description_
    handler : UserDBHandler
        _description_

    Returns
    -------
    bool
        _description_
    """
    if handler.get_admin(clave):
        return True
    return False

def apikey_is_active(clave:str, handler:UserDBHandler) -> bool:
    """True si la clave está activa

    Parameters
    ----------
    clave : str
        _description_
    handler : UserDBHandler
        _description_

    Returns
    -------
    bool
        _description_
    """
    if handler.get_activo(clave):
        return True
    return False

def has_words_left(clave:str, document_words:int, handler:UserDBHandler) -> bool:
    """Devuelve True si el usuario no supera el límite de palabras contratadas
    teniendo en cuenta las palabras del documento actual

    Parameters
    ----------
    clave : str
        _description_
    handler : UserDBHandler
        _description_

    Returns
    -------
    bool
        _description_
    """
    limite = handler.get_palabras_limite(clave)
    palabras_hasta_ahora = handler.get_palabras_actual(clave)
    return palabras_hasta_ahora + document_words < limite

def are_special_char(texto:str) -> bool:
    """True si el texto pasado son todo caracteres especial o de puntuación

    Parameters
    ----------
    texto : str
        _description_

    Returns
    -------
    bool
        _description_
    """
# Crear una expresión regular que incluya todos los caracteres especiales y de puntuación
    caracteres_especiales = re.escape(string.punctuation + '“”')
    # Comprobar si todos los caracteres en la palabra coinciden con la expresión regular
    return re.fullmatch("[" + caracteres_especiales + "]+", texto) is not None

# TODO
def theres_footer() -> bool:
    pass

def theres_header() -> bool:
    pass

