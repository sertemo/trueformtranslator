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

# Script con clases modelo a usar en la aplicación
from collections import namedtuple
from collections.abc import Sequence
import xml.etree.ElementTree as ET

OpenAIResponse = namedtuple('OpenAIResponse', ['response', 'total_cost'])

class XmlElement:
    def __init__(self, element:ET) -> None:
        self.element = element
        self.text = element.text
        self.translation = None

    def __repr__(self) -> str:
        return f'''{self.__class__.__name__}(
                        element: {self.element}
                        text: {self.text}
                        translation: {self.translation}
                    )'''

class XmlDocument(Sequence):
    """Iterando sobre un objeto XmlContainer
    devuelve los XmlElements que tenga almacenado

    Parameters
    ----------
    Sequence : _type_
        _description_
    """
    def __init__(self, 
                    name:str, 
                    tree:ET, 
                    text:str, 
                    element_list:list[XmlElement]
                    ) -> None:
        self.name = name
        self.tree = tree
        self.text = text
        self.element_list = element_list

    def __len__(self) -> int:
        return len(self.element_list)

    def __getitem__(self, idx) -> XmlElement:
        return self.element_list[idx]

    def __repr__(self) -> str:
        return f'''{self.__class__.__name__}(
            {self.name}(
                {self.element_list}
                )
            )'''