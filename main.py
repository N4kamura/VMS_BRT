from passengers.detection import process_image
import json
from gps.map_matching import *
from vms.vms_display import parse_colored_text_fixed, build_led_image
from gps.gps_data_generator import GPSDataGenerator
from traccar.connection import obtener_coordenadas
from time import sleep
from gps.gtfs_functions import read_stops_info
from big_data.read_json import read_time_between_stations
from time import time

def main():
    # GTFS file paths
    shapes_path = "gtfs/static/shapes.txt"
    stops_path = "gtfs/static/stops.txt"

    # Read GTFS files
    route_coordinates, shapes_dict = read_route_coordinates(shapes_path, multipoints=True)
    stops_info = read_stops_info(stops_path)

    # Traccar credentials
    with open("credentials/credentials_traccar.json", 'r') as cred_file:
        cred_data = json.load(cred_file)
        BASE_URL = cred_data["BASE_URL"]
        USUARIO = cred_data["USUARIO"]
        PASSWORD = cred_data["PASSWORD"]

    count = 0
    while True:
        start_time = time()
        # Traccar coordinates:
        traccar_bus = obtener_coordenadas(BASE_URL, USUARIO, PASSWORD)
        if not traccar_bus:
            print("Error: Could not get bus position from Traccar.")
            continue

        BUS = GPSDataGenerator(
                bus_id = traccar_bus["id"],
                route_id= traccar_bus["deviceId"], # Using deviceID as route_id for now
                latitude= traccar_bus["latitude"],
                longitude= traccar_bus["longitude"],
                speed = traccar_bus["speed"],
                course = traccar_bus["course"]
            )
        
        # Find the closest projection on the route and which segment it is on
        closest_point, segment_index = find_closest_projection((BUS.latitude, BUS.longitude), route_coordinates)

        # Determine the next stop after the closest segment
        next_stop_id = None
        upper_limit_point = len(route_coordinates) # Default to the end of the route

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

        remain_distance_to_station = point_to_segment_distance(route_coordinates, segment_index, closest_point, upper_limit_point)

        # Process images for passenger detection
        # TODO: Integrate with actual image source
        # For testing, we use a placeholder image path
        test_image_path = "passengers_1.png"
        passengers_count = process_image(test_image_path)
        if passengers_count >= 30:
            capacity = "Alto"
        elif passengers_count >= 15:
            capacity = "Medio"
        elif passengers_count >= 0:
            capacity = "Bajo"
        else:
            capacity = "N/A"

        # Big Data reading through API
        # For testing, we use a placeholder JSON path
        big_data_json_path = "tests/big_data.json" # NOTE: Replace with actual API call
        station_name = next_stop_id
        total_length, total_arrival_time = read_time_between_stations(big_data_json_path, station_name)

        # Compute ETA based on remaining distance
        if total_length and total_arrival_time and remain_distance_to_station is not None:
            eta_seconds = (remain_distance_to_station / total_length) * total_arrival_time
            text = f"Ruta {BUS.route_id} >> {int(eta_seconds)} seg >> {capacity}"
            mask_with_colors = parse_colored_text_fixed(text, font_px = 12)
            img = build_led_image(mask_with_colors)
            img.save("led_image.png")

        count += 1
        end_time = time()
        print(text)
        print(f"Iteration {count} completed in {end_time - start_time:.2f} seconds.")
        if count > 5: # XXX: To stop after 5 iterations for testing
            break

        sleep(30)  # Wait before next iteration

if __name__ == "__main__":
    main()