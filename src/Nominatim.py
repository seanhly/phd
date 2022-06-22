import subprocess
from NominatimData import NominatimData

from cloud.server.Region import Region
from JSON import JSON

URL = "https://nominatim.openstreetmap.org/search.php"
class Nominatim:
	def lookup(region: Region):
		url = f"{URL}?q={region.city.replace(' ', '+')}&countrycodes={region.country}&limit=1&format=json"
		return NominatimData(
			JSON.loads(subprocess.check_output(
				["/usr/bin/curl", url],
				stderr=subprocess.DEVNULL
			).decode())[0]
		)