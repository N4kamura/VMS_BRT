import os
from passengers.detection import process_image
import json
from gps.map_matching import *
from gps.gps_data_generator import GPSDataGenerator
import csv
import matplotlib.pyplot as plt
import numpy as np

def main():
    # Reading data file by file
    directory = "tests/data"
    files = os.listdir(directory)

    # XXX: For now
    shapes_path = "gtfs/static/shapes.txt"
    stops_path = "gtfs/static/stops.txt"

    # Read the route coordinates
    route_coordinates, shapes_dict = read_route_coordinates(shapes_path, multipoints=True)

    # Read stops information
    if not os.path.exists(stops_path):
        print("Stops file not found!")
        return
    
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
    
    # Process all files and collect bus positions
    for file in files:
        file_path = os.path.join(directory, file)

        image_path = os.path.join(file_path, "passengers.png")
        vehpos_path = os.path.join(file_path, "vehicle_position.json")

        # Reading coordinates and more info from json file simulating GPS
        with open(vehpos_path, 'r') as f:
            data = json.load(f)
            entity = data['entity'][0]
            BUS = GPSDataGenerator(
                bus_id = entity["id"],
                route_id= entity["vehicle"]["route"],
                latitude= entity["vehicle"]["position"]["latitude"],
                longitude= entity["vehicle"]["position"]["longitude"],
                speed = entity["vehicle"]["position"]["speed"],
                heading = entity["vehicle"]["position"]["heading"]
            )

        # Find the closest projection on the route and which segment it is on
        closest_point, segment_index = find_closest_projection((BUS.latitude, BUS.longitude), route_coordinates)
        # percentage = get_percentage_along_polyline(route_coordinates, closest_point, segment_index)
        # print("Count:", count, "\t%:", f"{percentage:.2f}", "\tValue:", cumulative_distance)

        ## Looking for Big Data Segment ##
        next_stop_id = None
        for point_index, coordinates in enumerate(route_coordinates[segment_index + 1:]):
            lat, lon = coordinates
            for stop_id, stop_data in stops_info.items():
                lan_stop, lon_stop = stop_data["latitude"], stop_data["longitude"]
                if lat == lan_stop and lon == lon_stop:
                    next_stop_id = stop_id
                    upper_limit_point = point_index + 1 + segment_index
                    break
            if next_stop_id:
                break

        print("Upper limit point:", upper_limit_point, "Segment index:", segment_index)
        remain_distance_to_station = point_to_segment_distance(route_coordinates, segment_index, closest_point, upper_limit_point)
        print("Remain distance to station (m):", remain_distance_to_station, "Next stop ID:", stops_info[next_stop_id]["name"])
        

if __name__ == "__main__":
    main()