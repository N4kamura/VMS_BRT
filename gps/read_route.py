import shapefile
import os
import math

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
    
    return total_length

def read_route_coordinates(shapefile_path, multipoints=False):
    """
    Read latitude and longitude coordinates from Route_401.shp file.
    Returns a list of (latitude, longitude) tuples.
    """
    # Check if the file exists
    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"Shapefile not found at {shapefile_path}")
    
    # Read the shapefile
    sf = shapefile.Reader(shapefile_path)
    
    # Get all shapes (there should be only one line)
    shapes = sf.shapes()
    
    # Extract coordinates from the first (and only) shape
    if shapes and multipoints == False:
        shape = shapes[0]  # NOTE: Get the first shape
        points = shape.points  # Get all points in the shape
        
        # Convert to list of (latitude, longitude) tuples
        # NOTE: In shapefiles, the order is typically (longitude, latitude)
        coordinates = [(point[1], point[0]) for point in points]
        return coordinates
    
    elif shapes and multipoints == True:
        all_coordinates = []
        for shape in shapes:
            points = shape.points
            coords = [(point[1], point[0]) for point in points]
            all_coordinates.extend(coords)
        return all_coordinates
    
    else:
        return []

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

def point_to_segment_distance(route_coordinates, segment_index, projected_point, forward=True):
    """
    Calculate the cumulative distance along the route up to a specific point on a given segment.
    
    Args:
        route_coordinates: List of (lat, lon) tuples representing all points of the multiline
        segment_index: Index of the segment where the point is located
        projected_point: (lat, lon) tuple of the already projected point
        forward: Boolean indicating if the route follows the original order (True) or reverse (False)
    
    Returns:
        float: Cumulative distance along the route up to the point (in meters)
    """
    # Validate segment index
    if segment_index < 0 or segment_index >= len(route_coordinates) - 1:
        raise ValueError(f"Segment index {segment_index} is out of bounds for route with {len(route_coordinates)} points")
    
    # If forward is False, we need to reverse the route coordinates
    coordinates = route_coordinates if forward else list(reversed(route_coordinates))
    
    # Calculate the index in the potentially reversed coordinates
    # If we reversed the route, we need to adjust the segment index accordingly
    if not forward:
        adjusted_segment_index = len(coordinates) - 2 - segment_index
    else:
        adjusted_segment_index = segment_index
    
    # Calculate the cumulative distance up to the specified segment
    cumulative_distance = 0.0
    
    # Add the length of all complete segments before the target segment
    for i in range(adjusted_segment_index):
        seg_start = coordinates[i]
        seg_end = coordinates[i + 1]
        seg_length = _calculate_segment_length(seg_start, seg_end)
        cumulative_distance += seg_length
    
    # Calculate the partial distance from segment start to the already projected point
    seg_start = coordinates[adjusted_segment_index]
    partial_distance = _calculate_segment_length(seg_start, projected_point)
    
    # Add the partial distance to the cumulative distance
    total_distance = round(cumulative_distance + partial_distance,2)
    
    return total_distance

def get_percentage_along_polyline(polyline, projected_point, segment_index, forward=True):
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

