import csv

def read_stops_info(stops_path: str):
    stops_info = {}
    with open(stops_path, 'r', newline='', encoding='utf-8') as stops_file:
        reader = csv.DictReader(stops_file)

        for row in reader:
            stop_id = row['stop_id']
            stop_name = row['stop_name']
            stop_lat = float(row['stop_lat'])
            stop_lon = float(row['stop_lon'])
            stop_location_type = row.get('location_type', '0')  # Default to '0' if not present
            stops_info[stop_id] = {
                "name": stop_name,
                "latitude": stop_lat,
                "longitude": stop_lon,
                "location_type": stop_location_type
            }

    return stops_info