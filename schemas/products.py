from typing import TypedDict, List, Optional

class Category(TypedDict):
    id: str
    name: str

class Product(TypedDict):
    code: str
    name: str
    category_id: str

class Group(TypedDict):
    id: str
    name: str
    category_id: str

class Subgroup(TypedDict):
    id: str
    name: str
    group_id: str
