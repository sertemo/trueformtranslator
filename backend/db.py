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

from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from pymongo import MongoClient

from backend.utils import get_datetime_formatted

DEFAULT_DB = 'TrueFormTranslator'
HASH_SCHEMA = CryptContext(schemes=["bcrypt"], deprecated= "auto")

load_dotenv()

def hash_apikey(key:str) -> str:
    """Devuelve una key hasheada

    Returns
    -------
    _type_
        _description_
    """
    return HASH_SCHEMA.hash(key)

def verify_apikey(key:str, key_hash:str) -> bool:
    """Comprueba si la key y la hash key coinciden

    Parameters
    ----------
    key : str
        _description_
    key_hash : str
        _description_

    Returns
    -------
    bool
        _description_
    """
    return HASH_SCHEMA.verify(key, key_hash)

class UsuarioDB(BaseModel):
    nombre:str
    email:str
    telefono:str
    clave:str
    apikey:str
    model:str = 'gpt-3.5-turbo'
    fecha_alta:str = Field(default_factory=get_datetime_formatted)
    activo:bool = True
    admin:bool = False
    palabras_limite:int
    palabras_actual:int = 0
    ultimo_uso:str
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
        self.db[self.collection].insert_one(document.model_dump())

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

    def update(self, busqueda:str, valor_buscado:str, diccionario_modificaciones:dict) -> None:
        assert isinstance(diccionario_modificaciones, dict), f"{diccionario_modificaciones} tiene que ser un diccionario."
        filtro = {busqueda: valor_buscado}
        valores_nuevos = {"$set": diccionario_modificaciones}
        self.db[self.collection].update_one(filtro, valores_nuevos)
    
    def delete_one(self, busqueda:str, valor_buscado:Any) -> None:
        filtro = {busqueda: valor_buscado}
        self.db[self.collection].delete_one(filtro)

    def increment_number(self, campo:str, valor:str, campo_a_incrementar:str, incremento:int|float) -> None:
        """_summary_

        Parameters
        ----------
        campo : str
            campo por el que buscar el documento
        valor : str
            valor que debe tener el documento buscado
        campo_a_incrementar : str
            Que campo queremos incrementar en 1
        """
        self.db[self.collection].update_one(
        {campo : valor}, 
        {"$inc" : {campo_a_incrementar : incremento}}
        )

class UserDBHandler(DBHandler):
    def __init__(self, collection:str, database:str=DEFAULT_DB) -> None:
        super().__init__(collection, database)
        self.conn = self.db[self.collection]


    def get_activo(self, clave:str) -> bool:
        user_dict = self.conn.find_one({"clave": clave})
        return user_dict.get("activo")
    
    
    def get_name(self, clave:str) -> str:
        user_dict = self.conn.find_one({"clave": clave})
        return user_dict.get("nombre")

    
    def get_email(self, clave:str) -> str:
        user_dict = self.conn.find_one({"clave": clave})
        return user_dict.get("email")
    
    
    def get_admin(self, clave:str) -> str:
        user_dict:dict = self.conn.find_one({"clave": clave})
        return user_dict.get("admin")
    
    
    def get_api_key(self, clave:str) -> str | None:
        user_dict:dict = self.conn.find_one({"clave": clave})
        return user_dict.get("apikey") if user_dict is not None else None
    
    
    def get_palabras_limite(self, clave:str) -> int:
        user_dict:dict = self.conn.find_one({"clave": clave})
        return user_dict.get("palabras_limite") if user_dict is not None else 0
    

    def get_palabras_actual(self, clave:str) -> int:
        user_dict:dict = self.conn.find_one({"clave": clave})
        return user_dict.get("get_palabras_actual")
    
    
    def get_nombre(self, clave:str) -> int:
        user_dict:dict = self.conn.find_one({"clave": clave})
        return user_dict.get("nombre")
    
    def get_model(self, clave:str) -> int:
        user_dict:dict = self.conn.find_one({"clave": clave})
        return user_dict.get("model")

if __name__ == '__main__':
    # Para crear el primer documento
    admin = UsuarioDB(
        nombre='Sergio Tejedor',
        email='',
        telefono='',
        clave='',
        apikey='',
        admin=True,
        palabras_limite=0,
        ultimo_uso="",
        facturado_accumulado=0,        
    )
    # UserDBHandler('usuarios').insert(admin)


