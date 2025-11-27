import json

def read_time_between_stations(json_path: str, name: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        routes = data.get("routes", {})
        for route in routes:
            if route.get("name") == name:
                total_length = route.get("length", 0) # meters
                time = route.get("time", 0) # seconds
                return total_length, time
    return None, None