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
- [x] Crear frontend GUI con streamlit: 
    - inputs:
        - OpenAI API KEY
        - Idioma destino
        - Documento word a traducir
- [x] Descompresión del docx en su estructura de archivo xml
- [x] Extracción del texto y sus elementos del archivo document.xml
- [x] Sacar el idioma del texto automáticamente (ISO 639)
- [x] Sacar tema del documento preguntando a OpenAI trackeando costes.
- [x] Realizar la lógica con DB.
- [x] Pedir prompt a chatgpt con idioma, contexto y temáticas para la traducción.
- [x] Realizar validaciones.
- [-] Crear el DataFrame NO. Al final utilizo dicts.
- [x] Mapear los textos y realizar las traducciones.
- [x] Optimizar y generalizar el bucle de traducción.
- [] Estudiar casos particulares.
- [x] Modificar cada elemento con su texto traducido.
- [x] Guardar el archivo xml sustituyendo el anterior.
- [x] Montar de nuevo un docx (zipfile)
- [x] Generar un enlace de descarga
- [] Testear caso de ligaduras en francés ( con prompt de memoria)
- [] Agregar checkpoints para archivos de muchas palabras
- [] Comparar performance de traducción entre gpt-4 y gpt-3.5

## Librerías
- poetry para la gestión de dependencias
- zipfile para la descompresión del docx
- xml.etree.ElementTree para la gestión del documento xml.
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