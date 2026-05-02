from __future__ import annotations

import time

from geopy.geocoders import Nominatim


class GeocodingService:
    """Turns a city and country into latitude and longitude coordinates."""

    def __init__(self, user_agent: str = "city_map_poster", delay_seconds: float = 1) -> None:
        self.geolocator = Nominatim(user_agent=user_agent)
        self.delay_seconds = delay_seconds

    def get_coordinates(self, city: str, country: str) -> tuple[float, float]:
        print("Looking up coordinates...")
        time.sleep(self.delay_seconds)

        location = self.geolocator.geocode(f"{city}, {country}")
        if location is None:
            raise ValueError(f"Could not find coordinates for {city}, {country}")

        print(f"Found: {location.address}")
        print(f"Coordinates: {location.latitude}, {location.longitude}")
        return location.latitude, location.longitude
