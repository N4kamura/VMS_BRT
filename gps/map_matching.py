import os
import math
import csv

def _calculate_segment_length(seg_start, seg_end):
    """
    Calculate the length of a segment between two points using the Haversine formula (in meters).
    This is more accurate for geographic coordinates.
    """
    # Extract latitude and longitude
    lat1, lon1 = seg_start[0], seg_start[1]
    lat2, lon2 = seg_end[0], seg_end[1]
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in meters
    r = 6371000  # meters
    
    # Calculate the distance
    length = c * r
    
    return length

def _calculate_polyline_length(polyline):
    """
    Calculate the total length of a polyline in meters.
    """
    total_length = 0.0
    
    # Sum the length of all segments
    for i in range(len(polyline) - 1):
        seg_length = _calculate_segment_length(polyline[i], polyline[i + 1])
        total_length += seg_length
        # print(f"Segment {i+1} length: {int(total_length)} meters")
    
    return total_length

def read_route_coordinates(shapes_file, multipoints=False):
    """
    Read latitude and longitude coordinates from GTFS shapes.txt file.
    Returns a list of (latitude, longitude) tuples.
    """
    
    # Check if the file exists
    if not os.path.exists(shapes_file):
        raise FileNotFoundError(f"Shapes.txt file not found at {shapes_file}")
    
    # Dictionary to store coordinates for each shape_id
    shapes_dict = {} # TODO: I need an auxiliar function to detect the shape_id based on route_id 8)
    
    # Read the shapes.txt file
    with open(shapes_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            shape_id = row['shape_id']
            lat = float(row['shape_pt_lat'])
            lon = float(row['shape_pt_lon'])
            sequence = int(row['shape_pt_sequence'])
            accumulated_distance = float(row.get('shape_dist_traveled', 0.0))
            
            if shape_id not in shapes_dict:
                shapes_dict[shape_id] = []
            
            # Store the coordinate with its sequence number for proper ordering
            shapes_dict[shape_id].append((sequence, lat, lon, accumulated_distance))
    
    # Sort coordinates by sequence number for each shape
    for shape_id in shapes_dict:
        shapes_dict[shape_id].sort(key=lambda x: x[0])  # Sort by sequence number
    
    # If not multipoints, return coordinates for the first shape_id
    if not multipoints:
        if shapes_dict:
            # Get the first shape_id and return its coordinates
            first_shape_id = next(iter(shapes_dict))
            coordinates = [(lat, lon) for seq, lat, lon, acc_dist in shapes_dict[first_shape_id]]
            return coordinates, shapes_dict
        else:
            return [], {}
    
    # If multipoints, return all coordinates from all shapes
    else:
        all_coordinates = []
        for shape_id in shapes_dict:
            coords = [(lat, lon) for seq, lat, lon, acc_dist in shapes_dict[shape_id]]
            all_coordinates.extend(coords)
        return all_coordinates, shapes_dict

def find_closest_projection(point, polyline):
    """
    Find the closest orthogonal projection of a point onto a polyline.
    Returns the projected point and the segment index.
    """
    min_distance = float('inf')
    closest_point = None
    segment_index = -1
    
    # Check each segment of the polyline
    for i in range(len(polyline) - 1):
        seg_start = polyline[i]
        seg_end = polyline[i + 1]
        
        # Calculate the projection on the segment
        x, y = point[1], point[0]  # lon, lat
        x1, y1 = seg_start[1], seg_start[0]  # lon, lat
        x2, y2 = seg_end[1], seg_end[0]  # lon, lat
        
        # Vector calculations for projection
        dx, dy = x2 - x1, y2 - y1
        length_sq = dx * dx + dy * dy
        
        # Handle degenerate case where segment is a point
        if length_sq == 0:
            proj_x, proj_y = x1, y1
        else:
            # Calculate projection parameter
            t = ((x - x1) * dx + (y - y1) * dy) / length_sq
            # Clamp to segment
            t = max(0, min(1, t))
            # Calculate projected point
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
        
        # Convert back to lat/lon
        projected_point = (proj_y, proj_x)  # lat, lon
        
        # Calculate distance
        dist = math.sqrt((x - proj_x) ** 2 + (y - proj_y) ** 2)
        
        if dist < min_distance:
            min_distance = dist
            closest_point = projected_point
            segment_index = i
    
    return closest_point, segment_index

def point_to_segment_distance(route_coordinates: list[tuple[float, float]], segment_index: int, projected_point: tuple[float, float], upper_limit_point: int) -> float:
    """
    Calculate the remaining distance from the projected point to the upper limit point along the route.

    Args:
        route_coordinates: List of (lat, lon) tuples representing all points of the route
        segment_index: Index of the segment where the projected point is located
        projected_point: (lat, lon) tuple of the already projected point
        upper_limit_point: Index of the point that represents the upper limit in the route (typically the next station)
    
    Returns:
        float: Remaining distance from the projected point to the upper limit point (in meters)
    """
    # Validate segment index
    if segment_index < 0 or segment_index >= len(route_coordinates) - 1:
        raise ValueError(f"Segment index {segment_index} is out of bounds for route with {len(route_coordinates)} points")
    
    # Delimitation of part of the route to consider
    coordinates = route_coordinates[segment_index:upper_limit_point + 1]
    
    ## Calculate the cumulative distance up to the specified segment ##
    cumulative_distance = 0.0

    # Add the length of all complete segments before the target segment
    for i in range(len(coordinates)-1):
        seg_start = coordinates[i]
        seg_end = coordinates[i + 1]
        seg_length = _calculate_segment_length(seg_start, seg_end)
        cumulative_distance += seg_length
    
    # Calculate the partial distance from segment start to the already projected point
    seg_start = route_coordinates[segment_index]
    partial_distance = _calculate_segment_length(seg_start, projected_point)
    
    # Deduct the partial distance from the cumulative distance
    remain_distance_to_station = round(cumulative_distance - partial_distance,2)
    
    return remain_distance_to_station

def get_percentage_along_polyline(polyline, projected_point, segment_index, forward=True):
    # XXX: Possible deprecated function
    """
    Calculate the percentage position of a projected point along the total length of the polyline.
    
    Args:
        polyline: List of (lat, lon) tuples representing the polyline
        projected_point: (lat, lon) tuple of the projected point
        segment_index: Index of the segment where the point is projected
        forward: Boolean indicating if the route follows the original order (True) or reverse (False)
    
    Returns:
        float: Percentage (0-100) of the position along the polyline
    """
    total_length = _calculate_polyline_length(polyline)
    distance_along = point_to_segment_distance(polyline, segment_index, projected_point, forward)
    
    if total_length == 0:
        return 0.0
    
    percentage = round((distance_along / total_length) * 100, 2)
    return percentage