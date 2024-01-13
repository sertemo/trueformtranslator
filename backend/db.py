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

# Script con el código relacionado la comunicación con base de datos
# y modelos de base de datos

from collections.abc import Sequence
import os
from typing import Any, Union

from passlib.context import CryptContext
from pydantic import BaseModel, Field
from pymongo import MongoClient

from .utils import get_datetime_formatted

DEFAULT_DB = 'TrueFormTranslator'
HASH_SCHEMA = CryptContext(schemes=["bcrypt"], deprecated= "auto")

def hash_apikey(key:str) -> str:
    """Devuelve una key hasheada

    Returns
    -------
    _type_
        _description_
    """
    return HASH_SCHEMA.hash(key)

class UsuarioDB(BaseModel):
    nombre:str
    email:str
    telefono:str
    apikey:str
    fecha_alta:str = Field(default_factory=get_datetime_formatted)
    activo:bool = True
    admin:bool = False
    palabras_limite:int
    palabras_actual:int = 0
    ultimo_uso:str
    ultimo_modelo:str
    facturado_accumulado:float
    coste_acumulado:float = 0

class DBHandler(Sequence):
    def __init__(self, collection:str, database:str=DEFAULT_DB) -> None:
        self.client = MongoClient(os.environ["DB_MONGO"])
        self.db = self.client[database]
        self.collection = collection
    
    def __len__(self) -> int:
        """Devuelve el número de documentos de la collección
        """
        return len(list(self.db[self.collection].find()))
    
    def __getitem__(self, idx:int) -> list:
        """el indice idx de la collection de la instancia

        Parameters
        ----------
        collections : str
            _description_
        """
        documents = list(self.db[self.collection].find())

        #Borramos el id
        for doc in documents:
            del doc["_id"]
        return documents[idx]
    
    def insert(self, document:Any) -> None:
        self.db[self.collection].insert_one(document.dict(by_alias=True))

    def find_one(self, campo_buscado:str, valor_buscado:Any) -> dict:
        """Devuelve un dict con todos los campos del valor buscado

        Parameters
        ----------
        campo_buscado : str
            _description_
        valor : Any
            _description_

        Returns
        -------
        dict
            _description_
        """
        return self.db[self.collection].find_one({campo_buscado: valor_buscado})

    def find_one_field(self, campo_buscado:str, valor:Any, campo_a_retornar:str) -> Any:
        """Devuelve el valor del campo que coincide con el documento buscado

        Parameters
        ----------
        campo_buscado : str
            _description_
        valor : Any
            _description_

        Returns
        -------
        dict
            _description_
        """
        search_dict = self.db[self.collection].find_one({campo_buscado: valor})

        if search_dict is None:
            return None
        return search_dict[campo_a_retornar] 

    def update(self, busqueda:str, valor_buscado:str, diccionario_modificaciones:dict):
        assert isinstance(diccionario_modificaciones, dict), f"{diccionario_modificaciones} tiene que ser un diccionario."
        filtro = {busqueda: valor_buscado}
        valores_nuevos = {"$set": diccionario_modificaciones}
        self.db[self.collection].update_one(filtro, valores_nuevos)
    
    def delete_one(self, busqueda:str, valor_buscado:Any):
        filtro = {busqueda: valor_buscado}
        self.db[self.collection].delete_one(filtro)

    def increment_one(self):
        pass

class UserDBHandler(DBHandler):
    def __init__(self, collection:str, database:str=DEFAULT_DB) -> None:
        super().__init__(collection, database)
        self.conn = self.db[self.collection]


    def get_activo(self, hash_apikey:str) -> bool:
        user_dict = self.conn.find_one({"apikey": hash_apikey})
        return user_dict["activo"]
    
    
    def get_name(self, hash_apikey:str) -> str:
        user_dict = self.conn.find_one({"apikey": hash_apikey})
        return user_dict["nombre"]    

    
    def get_email(self, hash_apikey:str) -> str:
        user_dict = self.conn.find_one({"apikey": hash_apikey})
        return user_dict["email"]
    
    
    def get_admin(self, hash_apikey:str) -> str:
        user_dict:dict = self.conn.find_one({"apikey": hash_apikey})
        return user_dict.get("admin")
    
    
    def get_api_key(self, hash_apikey:str) -> str | None:
        user_dict:dict = self.conn.find_one({"apikey": hash_apikey})
        return user_dict.get("apikey")
    
    
    def get_palabras_limite(self, hash_apikey:str) -> int:
        user_dict:dict = self.conn.find_one({"apikey": hash_apikey})
        return user_dict.get("palabras_limite")
    

    def get_palabras_actual(self, hash_apikey:str) -> int:
        user_dict:dict = self.conn.find_one({"apikey": hash_apikey})
        return user_dict.get("get_palabras_actual")



