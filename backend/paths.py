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

# Script que recoge las rutas a archivos relevantes

from pathlib import Path

XML_FOLDER = Path('backend/docx_xml')
WORD_FOLDER = XML_FOLDER / Path('word')
DOCUMENT_XML_PATH = WORD_FOLDER / 'document.xml'