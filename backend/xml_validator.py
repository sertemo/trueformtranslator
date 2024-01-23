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

# Script para realizar alguna validación de archivos xml con etree de lxml

from lxml import etree
from pathlib import Path

def get_xml_validation_errors(path:Path) -> dict[str, str]:
    """Devuelve un dict con los archivos xml que han dado error
    y el error en cuestión. Si no hay errores devuelve un dict vacío.

    Parameters
    ----------
    path : Path
        _description_

    Returns
    -------
    dict[str, str]
        _description_
    """
    vals = {}
    for xml_file in path.iterdir():
        if xml_file.is_file():
            try:
                with open(xml_file, 'rb') as f:
                    xml_doc = etree.parse(f)
            except etree.XMLSyntaxError as err_synt:
                vals[xml_file.name] = err
            except Exception as err:
                vals[xml_file.name] = err
    return vals

def all_xml_files_good(path:Path) -> tuple[bool, None] | tuple[bool, dict[str, str]]:
    """Devuelve True, None si todos los xml son válidos,
    False, dict con archivos y errores producidos en caso contrario

    Parameters
    ----------
    path : Path
        _description_

    Returns
    -------
    bool
        _description_
    """
    vals = get_xml_validation_errors(path)
    if not vals:
        return True, None
    else:
        return False, vals