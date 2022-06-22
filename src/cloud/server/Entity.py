from abc import ABC
from typing import Type


class Entity(ABC):
	vendor: Type["Vendor"]