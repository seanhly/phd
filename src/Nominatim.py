import subprocess
from NominatimData import NominatimData

from cloud.server.Region import Region
from JSON import JSON

URL = "https://nominatim.openstreetmap.org/search.php"


class Nominatim:
	@staticmethod
	def lookup(region: Region):
		q = region.city.replace(' ', '+')
		url = f"{URL}?q={q}&countrycodes={region.country}&limit=1&format=json"
		return NominatimData(
			JSON.loads(subprocess.check_output(
				["/usr/bin/curl", url],
				stderr=subprocess.DEVNULL
			).decode())[0]
		)
