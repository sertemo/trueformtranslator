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

Script con funciones auxiliares para el backend
    """

from datetime import datetime
import pytz
import random
import re
import string
from typing import Literal

PRICING_PER_TOKEN = {
    'gpt-3.5-turbo': 0.0020e-3,
    "gpt-3.5-turbo-1106": 0.0020e-3, # 16K de contexto
    "gpt-3.5-turbo-instruct": 0.0020e-3, # 4K de contexto
    "gpt-4-32k": 0.12e-3, # 32K de contexto
    "gpt-4": 0.06e-3, 
}

def clean_word(texto:str) -> str:
    """quita los signos de puntuación de la palabra

    Parameters
    ----------
    texto : str
        _description_

    Returns
    -------
    bool
        _description_
    """
    # Crear una tabla de traducción que mapea cada carácter de puntuación a None
    tabla_traduccion = str.maketrans('', '', string.punctuation + '“”')
    # Usar la tabla de traducción para eliminar los signos de puntuación del texto
    return texto.translate(tabla_traduccion)

def get_chunk(dataset:list[str], num_samples:int=5) -> str:
    """Dado una lista con frases de un documento, devuelve
    un 'chunk' en string cogiendo num_samples elementos

    Parameters
    ----------
    dataset : list[str]
        _description_
    num_samples : int, optional
        _description_, by default 5

    Returns
    -------
    str
        _description_
    """
    indice_inf = random.randint(0, len(dataset) - num_samples)
    chunk = dataset[indice_inf:indice_inf+num_samples]
    return " ".join(chunk)

def get_datetime_formatted()-> str:
    """Devuelve la fecha actual formateada en str como:
    %d-%m-%Y %H:%M:%S

    Returns
    -------
    str
        _description_
    """
    return datetime.strftime(datetime.now(tz=pytz.timezone('Europe/Madrid')), format="%d-%m-%Y %H:%M:%S")

def convert_words_to_tokens(num_words:int) -> int:
    """Función para transformar el número de palabras
    en tokens para estimar los cotes de traducción del documento.
    El ratio puede variar

    Parameters
    ----------
    num_words : int
        _description_

    Returns
    -------
    int
        _description_
    """
    ratio = {'tokens': 100, 'words': 75}
    return round((ratio['tokens'] / ratio['words']) * num_words)

def estimate_openai_cost(num_words:int, model:str='gpt-3.5-turbo') -> float:
    """Dado un pricing, un modelo
    y un numero de palabras, devuelve el coste en € estimado

    Parameters
    ----------
    tokens : int
        _description_

    Returns
    -------
    float
        _description_
    """
    if model not in PRICING_PER_TOKEN:
        raise ValueError(f"{model} no es un modelo válido.")
    tokens = convert_words_to_tokens(num_words)
    return round(tokens * PRICING_PER_TOKEN[model], 4)
    
