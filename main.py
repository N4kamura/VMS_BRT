import os
from passengers.detection import process_image
import json
from gps.read_route import *

def main():
    # Reading data file by file
    directory = "tests/data"
    files = os.listdir(directory)

    # XXX: For now
    shapefile_path = "tests/shapes/A_to_B.shp"

    for file in files:
        file_path = os.path.join(directory, file)

        image_path = os.path.join(file_path, "passengers.png")
        vehpos_path = os.path.join(file_path, "vehicle_position.json")

        # Counting passengers
        # count = process_image(image_path)

        # Reading coordinates and more info from json file
        with open(vehpos_path, 'r') as f:
            data = json.load(f)
            entity = data['entity'][0]
            latitude = entity['vehicle']['position']['latitude']
            longitude = entity['vehicle']['position']['longitude']
            route = entity['vehicle']['route']

        # Read the route coordinates
        route_coordinates = read_route_coordinates(shapefile_path, multipoints=True)
        # print("Route coordinates:", route_coordinates)
        # Find the closest projection on the route and which segment it is on
        closest_point, segment_index = find_closest_projection((latitude, longitude), route_coordinates)
        cumulative_distance = point_to_segment_distance(route_coordinates, segment_index, closest_point)
        print("H:", cumulative_distance)

        percentage = get_percentage_along_polyline(route_coordinates, closest_point, segment_index)
        print("%:", percentage)

        # TODO: Get time according to percentage of the route from Big Data

if __name__ == "__main__":
    main()