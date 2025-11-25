from datetime import datetime, time

class GPSDataGenerator:
    def __init__(self, bus_id: str, route_id: str, latitude: float, longitude: float, speed: float, heading: float):
        a = 53
        # Fixed information
        self.bus = bus_id
        self.route_id = route_id

        # Variable information
        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed
        self.heading = heading
        self.timestamp = None

    def send_data(self):
        unix_datetime = datetime.now().timestamp() # Unix timestamp. Simulated like Real GPS.and
        # NOTE: Check this. I guess is not correct for universal Unix timestamp.
        self.timestamp = datetime.fromtimestamp(unix_datetime)
        data = {
            "bus": self.bus,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "route_id": self.route_id,
            "speed": self.speed,
            "heading": self.heading,
            "timestamp": self.timestamp
        }

        return data