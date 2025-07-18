def get_center_of_bbox(bbox):
    """
    Calculate the center coordinates of a bounding box.

    Args:
        bbox (tuple): Bounding box coordinates in format (x1, y1, x2, y2).

    Returns:
        tuple: Center coordinates (x, y) of the bounding box.
    """
    x1,y1,x2,y2 = bbox
    return int((x1+x2)/2),int((y1+y2)/2)

def measure_distance(p1,p2):
    """
    Calculate the Euclidean distance between two points.

    Args:
        p1 (tuple): First point coordinates (x, y).
        p2 (tuple): Second point coordinates (x, y).

    Returns:
        float: Euclidean distance between the two points.
    """
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5