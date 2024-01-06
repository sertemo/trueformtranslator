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
        - Idioma destino
        - Temática del documento
2. Extracción de todo el texto, estilos, imágenes, tamaños, negritas, encabezados, títulos, pies de página, tablas etc. Guardar en DataFrame
3. Sacar tema del documento con Latent Dirichlet o similar y/o con las especificaciones del usuario.
4. Pedir prompt a chatgpt con idioma y temáticas para la traducción.
5. Mapear DataFrame y realizar las traducciones
6. Volver a montar el documento
7. Generar un enlace de descarga

## Librerías
- poetry para la gestión de dependencias
- python-docx para el tratamiento del documento
- Langchain para la parte de traducción con la API de OpenAI (CHatGPT)
- Streamlit para la GUI y el despliegue