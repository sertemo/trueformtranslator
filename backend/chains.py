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
    prompt_traduccion = ChatPromptTemplate.from_template('''
    Eres un excelente identificador de documentos a partir de sus extractos.
    Se te van a pasar dos extractos de un documento en {idioma} llamado {nombre_documento}.
    Tu misión es identificar el tipo de documento al que pertenecen esos extractos.
    Lo importante es obtener información del documento al que pertenecen no los extractos.
    Responde en español.
    Responde solo con los detalles del tipo de documento al que pertenece el extracto.
    Responde breve.

    EXTRACTO 1:
    {extracto_1}

    EXTRACTO 2:
    {extracto_2}

    TU RESPUESTA:
    '''
    )
    llm = get_llm(0.3, os.environ['OPENAI_API_KEY'])

    chain = (
        prompt_traduccion
        | llm
        | StrOutputParser()
    )
    return chain