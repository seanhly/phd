from typing import List


class NominatimData:
	place_id: int
	licence: str
	osm_type: str
	osm_id: int
	boundingbox: List[float]
	lat: float
	lon: float
	display_name: str
	importance: float
	icon: str

	def __init__(self, data):
		self.__dict__ = data
