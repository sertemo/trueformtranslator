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

# Script con el código relacionado con la traducción de OpenAI

from langchain_community.callbacks import get_openai_callback

from .chains import (get_translation_prompt_chain, 
                        get_translation_chain, 
                        get_translation_chain_with_memory
                        )
from .models import OpenAIResponse


def translate(
        apikey:str,
        model:str,
        origin_lang:str,
        destiny_lang:str,
        doc_context:str,
        doc_features:str,
        texto_anterior:str,
        texto_posterior:str,
        text:str,
        ) -> OpenAIResponse:
    """Ejecuta la chain de traducción y devuelve un objeto
    TranslationResponse con (texto traducido, coste)

    Parameters
    ----------
    apikey : str
        _description_
    model : str
        _description_
    origin_lang : str
        _description_
    destiny_lang : str
        _description_
    doc_context : str
        _description_
    doc_features : str
        _description_
    text : str
        _description_

    Returns
    -------
    OpenAIResponse
        _description_
    """
    # Obtenemos la chain
    chain = get_translation_chain_with_memory(apikey, model) # o get_translation_chain
    with get_openai_callback() as cb:
        response = chain.invoke({
            'idioma_origen': origin_lang,
            'idioma_destino': destiny_lang,
            'tematica': doc_features,
            'contexto': doc_context,
            'texto': text,
            'texto_anterior': texto_anterior,
            'texto_posterior': texto_posterior,
        })
        coste_total = cb.total_cost
    return OpenAIResponse(response, coste_total)

def get_translation_prompt( # ! Deprecated
        apikey:str,
        model:str,
        origin_lang:str, 
        destiny_lang:str,
        doc_context:str,
        doc_features:str,
        num_words:int) -> OpenAIResponse:
    """Función que le pide a chatGPT un prompt efectivo con los elementos
    característicos del documento. Devuelve un objeto con la respuesta (el prompt)
    y el coste de la query

    Parameters
    ----------
    origin_lang : str
        _description_
    destiny_lang : str
        _description_
    doc_context : str
        _description_
    doc_features : str
        _description_
    doc_name : str
        _description_
    num_words : int
        _description_

    Returns
    -------
    OpenAIResponse
        (response, cost)
    """
    # instanciamos la chain
    chain = get_translation_prompt_chain(apikey, model)
    # Envolvemos en context manager para sacar el coste
    with get_openai_callback() as cb:
        response = chain.invoke({
            'idioma_origen': origin_lang,
            'idioma_destino': destiny_lang,
            'doc_context': doc_context,
            'doc_features': doc_features,
            'num_palabras': num_words,
        })
        coste_total = cb.total_cost
    return OpenAIResponse(response, coste_total)



