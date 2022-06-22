from typing import Tuple
from Nominatim import Nominatim
from cloud.server.Region import Region
from geopy.distance import distance


NOMINATIM_CACHE = {}
DUBLIN = Region(dict(
	city="Dublin",
	country="IE",
))


class Regions:
	@classmethod
	def lat_lon(cls, region: Region):
		key = f"{region.city}, {region.country}"
		coords: Tuple[float, float]
		if key in NOMINATIM_CACHE:
			coords = NOMINATIM_CACHE[key]
		else:
			data = Nominatim.lookup(region)
			coords = (data.lat, data.lon)
			NOMINATIM_CACHE[key] = coords

		return coords
	
	@classmethod
	def distance(cls, a: Region, b: Region = DUBLIN):
		return distance(cls.lat_lon(a), cls.lat_lon(b))

	@classmethod
	def nearest_region(cls):
		nearest_region = (None, 9e99)
		from cloud.vendors.Vultr import Vultr
		for region in Vultr.list_regions():
			distance = Regions.distance(region)
			if distance < nearest_region[1]:
				nearest_region = (region, distance)
		return nearest_region[0]