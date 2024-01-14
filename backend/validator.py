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

# Script con el código relacionado con funciones de validación

from .db import UserDBHandler

def exists_apikey(clave:str, handler:UserDBHandler) -> bool:
    """True si la apikey existe en base de datos

    Parameters
    ----------
    apikey : str
        _description_
    handler : UserDBHandler
        _description_

    Returns
    -------
    bool
        _description_
    """
    if handler.get_api_key(clave) is not None:
        return True
    return False

def apikey_is_admin(clave:str, handler:UserDBHandler) -> bool:
    """True si la apikey es de admin

    Parameters
    ----------
    apikey : str
        _description_
    handler : UserDBHandler
        _description_

    Returns
    -------
    bool
        _description_
    """
    if handler.get_admin(clave):
        return True
    return False

def apikey_is_active(clave:str, handler:UserDBHandler) -> bool:
    if handler.get_activo(clave):
        return True
    return False