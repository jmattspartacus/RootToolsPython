import os
import json
from typing import Tuple,List,Union,Mapping,Set,Callable

__cached_objects: Mapping[type, Mapping] = {}
__caching_implementations : Mapping[type, Callable] = {}
__save_to_disk_implementations : Mapping[type, Callable] = {}
__supported_types: Set[type] = set()

def get_supported_types() -> Set[type]:
    return __supported_types
def __get_caching_impl(obj_type: type) -> function:
    if obj_type in __caching_implementations:
        return __caching_implementations[obj_type]
    raise TypeError(f"Caching for {obj_type} is not supported")



