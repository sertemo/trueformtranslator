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

Script con funciones auxiliares
    """

import random

def get_chunk(dataset:list[str], num_samples:int=5) -> str:
    """Dado una lista con frases de un documento, devuelve
    un 'chunk' en string cogiendo num_samples elementos

    Parameters
    ----------
    dataset : list[str]
        _description_
    num_samples : int, optional
        _description_, by default 5

    Returns
    -------
    str
        _description_
    """
    indice_inf = random.randint(0, len(dataset) - num_samples)
    chunk = dataset[indice_inf:indice_inf+num_samples]
    return " ".join(chunk)