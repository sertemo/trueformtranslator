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

Script con el código relacionado con langchain, los prompts y las chains
    """

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.base import RunnableSequence
from langchain_openai import ChatOpenAI
import os

OPENAI_API_KEY_ADMIN = os.environ['OPENAI_API_KEY']

def get_llm(temperature:float, api_key:str, model:str='gpt-3.5-turbo') -> ChatOpenAI:
    """Devuelve un objeto ChatOpenAi de langchain con los parametros
    pasados por argumento

    Parameters
    ----------
    temperature : float
        _description_
    api_key : str
        _description_
    model : str, optional
        _description_, by default 'gpt3.5-turbo'

    Returns
    -------
    ChatOpenAI
        _description_
    """
    return ChatOpenAI(temperature=temperature,
                        openai_api_key=api_key,
                        model=model)

def get_topic_chain() -> RunnableSequence:
    """Devuelve la chain de sacar el topic para invocar con los parámetros
    idioma y extracto necesarios.

    Returns
    -------
    RunnableSequence
        La chain para invocar
    """
    prompt_traduccion = ChatPromptTemplate.from_template(
        '''
        Eres un excelente identificador de documentos a partir de sus extractos.
        Se te van a pasar dos extractos en {idioma} que pertenecen a un mismo documento llamado {nombre_documento}.
        Tu misión es obtener información del documento al que pertenecen esos extractos.
        Responde en español.
        Responde solo con los detalles del tipo de documento al que pertenece el extracto.
        Responde breve.

        EXTRACTO 1:
        {extracto_1}

        EXTRACTO 2:
        {extracto_2}

        TU RESPUESTA:
        El documento en cuestión es
        '''
        )
    llm = get_llm(0.3, OPENAI_API_KEY_ADMIN)

    chain = (
        prompt_traduccion
        | llm
        | StrOutputParser()
    )
    return chain

def get_translation_chain(apikey:str, model:str) -> RunnableSequence:
    """Devuelve la chain para la traducción de los textos.

    Parameters
    ----------
    apikey : str
        _description_
    model : str
        _description_

    Returns
    -------
    RunnableSequence
        _description_
    """
    prompt = ChatPromptTemplate.from_template(
        '''
        Eres un experto traductor de documentos.
        Tu misión es traducir un documento del {idioma_origen} al {idioma_destino}.
        El documento es {tematica} de tipo {contexto}.
        Los textos del documento a traducir serán en forma de palabras, frases o párrafos.
        Respeta el formato del texto en la traducción. Ejemplo de Español a Francés:
        TEXTO: ' dónde hacía calor, '
        TRADUCCIÓN: ' où il faisait chaud, '

        Traduce solo los textos en {idioma_origen}.
        No traduzcas nombres propios.
        Responde solo con la traducción en {idioma_destino}.

        TEXTO: {texto}
        TRADUCCIÓN:
        ''')
    llm = get_llm(0.1, api_key=apikey, model=model)

    chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    return chain
# Prueba de chain insertando una especie de 'memoria'
def get_translation_chain_with_memory(apikey:str, model:str) -> RunnableSequence:
    """Devuelve la chain para la traducción de los textos.
    Este prompt incorpora el texto anterior y posterior

    Parameters
    ----------
    apikey : str
        _description_
    model : str
        _description_

    Returns
    -------
    RunnableSequence
        _description_
    """
    prompt = ChatPromptTemplate.from_template(
        '''
        Eres un experto traductor de documentos.
        Tu misión es traducir un documento del {idioma_origen} al {idioma_destino}.
        El documento es {tematica} de tipo {contexto}.
        Los textos del documento a traducir serán en forma de palabras, frases o párrafos.
        Se te pasará el texto anterior y posterior al texto a traducir para que tengas el contexto.
        Respeta el formato del texto en la traducción. Ejemplo de Español a Francés:
        TEXTO: ' dónde hacía calor, '
        TRADUCCIÓN: ' où il faisait chaud, '

        Traduce solo los textos en {idioma_origen}.
        No traduzcas nombres propios.
        Traduce solo el TEXTO A TRADUCIR.
        Responde solo con la traducción en {idioma_destino}.

        TEXTO ANTERIOR: {texto_anterior}
        TEXTO POSTERIOR: {texto_posterior}
        TEXTO A TRADUCIR: {texto}
        TRADUCCIÓN:
        ''')
    llm = get_llm(0.1, api_key=apikey, model=model)

    chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    return chain

def get_translation_prompt_chain(apikey:str, model:str) -> RunnableSequence: #! Deprecated    
    """Crea la chain para pedir un prompt a chatgpt

    Returns
    -------
    RunnableSequence
        _description_
    """
    prompt_translation_prompt = ChatPromptTemplate.from_template(
        '''
        Eres un excelente creador de prompts para ChatGPT.
        Tu misión es crear el mejor prompt efectivo para traducir un documento Word del {idioma_origen} al {idioma_destino}.                                            
        Estas son algunas características importante que debes considerar:
            - El contexto o temática del documento es: {doc_context}.
            - Algunas características adicionales del documento o alguno de sus extractos: {doc_features}.
            - El documento tiene {num_palabras} palabras.
            - Los elementos a traducir del documento se pasarán en forma de frases, párrafos o palabras sueltas.
        
        Responde solo con el prompt, nada más.

        TU PROMPT:
        Traduce
        '''
        )
    llm = get_llm(0.1, apikey, model)

    chain = (
        prompt_translation_prompt
        | llm
        | StrOutputParser()
    )
    return chain