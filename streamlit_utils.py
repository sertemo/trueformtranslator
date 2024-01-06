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

Script con funciones auxiliares para el entorno de Streamlit
"""
import streamlit as st

DEFAULT_COLOR = '#607274'
font_dict = {
    'Raleway': 'https://fonts.googleapis.com/css2?family=Raleway:wght@700&display=swap',
    'Rubik Doodle Shadow': "https://fonts.googleapis.com/css2?family=Rubik+Doodle+Shadow&display=swap",
    'Dancing Script': 'https://fonts.googleapis.com/css2?family=Dancing+Script&display=swap'
}

def texto(texto:str, /, *, 
        font_size:int=30, 
        color:str=DEFAULT_COLOR, 
        font_family:str="Helvetica", 
        formato:str="", 
        centrar:bool=False) -> None:
    """ 
    Función para personalizar el texto con HTML, permitiendo especificar una URL para una fuente externa.
    """
    if font_family in font_dict:
        font_url = font_dict[font_family]
        estilo_fuente = f"@import url('{font_url}');"
    else:
        estilo_fuente = ""
    font_family_css = f"font-family: {font_family};"
    if formato:
        texto = f"<{formato}>{texto}</{formato}>"
    if centrar:
        texto = f"<div style='text-align: center'>{texto}</div>"
    texto_formateado = f"""
                        <style>
                        {estilo_fuente}
                        </style>
                        <div style='font-size: {font_size}px; color: {color}; {font_family_css}'>
                            {texto}
                        </div>
                        """
    st.markdown(texto_formateado, unsafe_allow_html=True)

def mostrar_enlace(label:str, url:str, *, color:str=DEFAULT_COLOR, font_size:str='16px', centrar:bool=False) -> None:
    """Muestra un enlace personalizado.

    Args:
    label (str): El texto que se mostrará como el enlace.
    url (str): La URL a la que apunta el enlace.
    color (str): Color del texto del enlace.
    font_size (str): Tamaño del texto del enlace.
    centrar (bool): Centra el texto
    """
    html = f'<a href="{url}" target="_blank" style="color: {color}; font-size: {font_size}; text-decoration: none;">{label}</a>'
    if centrar:
        html = f"""
                    <div style='text-align: center'>
                        {html}
                    </div>
                    """
    st.markdown(html, unsafe_allow_html=True)

def añadir_salto(num_saltos:int=1) -> None:
    """Añade <br> en forma de HTML para agregar espacio
    """
    saltos = f"{num_saltos * '<br>'}"
    st.markdown(saltos, unsafe_allow_html=True)

def imagen_con_enlace(url_imagen, url_enlace, alt_text="Imagen", max_width:int=100, centrar:bool=False) -> None:
    """Muestra una imagen que es también un hipervínculo en Streamlit.

    Args:
    url_imagen (str): URL de la imagen a mostrar.
    url_enlace (str): URL a la que el enlace de la imagen debe dirigir.
    alt_text (str): Texto alternativo para la imagen.
    """    
    html = f'<a href="{url_enlace}" target="_blank"><img src="{url_imagen}" alt="{alt_text}" style="max-width:{max_width}%; height:auto;"></a>'
    if centrar:
        html = f"""
                    <div style='text-align: center'>
                        {html}
                    </div>
                    """
    st.markdown(html, unsafe_allow_html=True)

def footer():
    pass