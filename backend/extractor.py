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

Script con el código relacionado con la extracción de la información del documento Word
    """

from docx import Document

def feature_extractor(document:bytes) -> dict:
    """coge el documento y devuelve un dict con todas las características

    Parameters
    ----------
    document : str
        _description_

    Returns
    -------
    dict
        _description_
    """
    doc = Document(document)
    texto_y_estilos = []

    for idx, paragraph in enumerate(doc.paragraphs):
        para_dict = {
                f"para_{idx}": {
                    "texto": paragraph.text,
                    "format": {
                        "left_indent": paragraph.paragraph_format.left_indent,
                        "space_before": paragraph.paragraph_format.space_before,
                        "space_after": paragraph.paragraph_format.space_after,
                        "line_spacing": paragraph.paragraph_format.line_spacing,
                        "keep_together": paragraph.paragraph_format.keep_with_next,
                        "page_break_before": paragraph.paragraph_format.page_break_before,
                        },
                    "runs": []
                }
            }
        for run in paragraph.runs:
            para_dict[f"para_{idx}"]["runs"].append(
                {
                "texto": run.text,
                "negrita": run.bold,
                "cursiva": run.italic,
                "subrayado": run.underline,
                "tipo_fuente": run.font.name,
                "tamaño_fuente": run.font.size.pt if run.font.size else None,
                "color_fuente": run.font.color.rgb,
                "color_tipo_fuente": run.font.color.type,
                #"espaciado": run.font.spacing #! no existe
                # Añadir aquí más propiedades si es necesario
                }
            )
        texto_y_estilos.append(para_dict)
    return texto_y_estilos

def builder():
    """Para reconstruir el documento
    """
    pass
