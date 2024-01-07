# TrueFormTranslator

Aplicación para traducir a un idioma de tu elección un documento.

Características que quiero incorporar:
- Recuperar imágenes y estilos del documento original y reproducir el mismo documento con el mismo formato pero traducido
- Elección de varios idiomas
- Interfaz sencilla y minimalista.
- Descripción del avance del proceso de traducción
- Tratamiento de los datos en forma de DataFrame
- git Flow
- Limitación de tamaño del documento. En número de palabras ? en megas ?
- Estimación del coste de la traducción antes de traducir
- Diseño del prompt en función del contenido: Realizar un modelo de ML para sacar el o los temas del documento (LDA). Otra opción es requerir al usuario la temática del documento. Con esta temática se realizará un prompt detallado (se le puede pedir a chatGPT que realice el prompt) que se enviará junto con los textos del documento para conformar la columna "traducción" del dataFrame.
- Pasar un modelo de OCR (Reconocimiento de caracteres) sobre las imágenes por si tienen texto ? para traducirlas después?

## Etapas
1. Crear frontend GUI con streamlit:
    - inputs:
        - OpenAI API KEY
        - Idioma destino
        - Temática del documento
        - Documento word a traducir
2. Extracción de todo el texto, estilos, imágenes, tamaños, negritas, encabezados, títulos, pies de página, tablas etc. Guardar en DataFrame
3. Sacar el idioma del texto automáticamente (ISO 639)
4. Sacar tema del documento con Latent Dirichlet o similar y/o con las especificaciones del usuario.
5. Pedir prompt a chatgpt con idioma y temáticas para la traducción.
6. Mapear DataFrame y realizar las traducciones
7. Volver a montar el documento
8. Generar un enlace de descarga

## Librerías
- poetry para la gestión de dependencias
- python-docx para el tratamiento del documento
- textblob y langdetect para detectar el idioma del documento
- scikit-learn para LDA topic modelling
- Langchain para la parte de traducción con la API de OpenAI (CHatGPT)
- Streamlit para la GUI y el despliegue

## Licencia
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