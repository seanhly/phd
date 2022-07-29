from typing import Tuple
from JSON import JSON
from Nominatim import Nominatim
from cloud.server.Region import Region
from geopy.distance import distance
from os.path import exists
from constants import PHD_NEAREST_SERVER


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
		if exists(PHD_NEAREST_SERVER):
			with open(PHD_NEAREST_SERVER, "r") as f:
				return Region(JSON.load(f), None)
		nearest_region = (None, 9e99)
		from cloud.vendors.Vultr import Vultr
		for region in Vultr.list_regions():
			the_distance = Regions.distance(region)
			if the_distance < nearest_region[1]:
				nearest_region = (region, the_distance)
		the_region = nearest_region[0]
		with open(PHD_NEAREST_SERVER, "w") as f:
			d = the_region.__dict__
			del d["vendor"]
			JSON.dump(d, f)
		return the_region
