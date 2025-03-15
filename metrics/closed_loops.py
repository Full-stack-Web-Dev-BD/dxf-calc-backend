# Cloosed loops count calculation
from ezdxf.entities import Line, LWPolyline, Spline, Circle, Arc

loops = 0


def closed_loops():
	return loops


def reset_loop():
    global loops
    loops = 0


def increase_closed_loops(count = 1):
	global loops
	loops += count
	# print(f"[Closed loops:] {loops}")


def calc_closed_loops_line(shape):
	increase_closed_loops(0)
	

def calc_closed_loops_polyline(shape):
	increase_closed_loops(1 if shape.is_closed else 0)


def calc_closed_loops_spline(shape):
	increase_closed_loops(1 if shape.closed else 0)


def calc_closed_loops_circle(shape):
	increase_closed_loops()


def calc_closed_loops_arc(shape):
	increase_closed_loops(0)



def calc_closed_loops_insert(shape):
    """
    Handles the 'INSERT' type DXF entities for calculating closed loops.
    This function checks if the inserted block forms a closed loop
    by inspecting the entities inside the block.
    """
    block_name = shape.dxf.name  # Block name from INSERT entity
    block = shape.doc.blocks.get(block_name)  # Get the block object using its name from the shape's doc

    closed_loops_count = 0
    points = []

    # Loop through all entities in the block and collect points
    for entity in block:
        if isinstance(entity, Line):
            points.extend([(entity.dxf.start.x, entity.dxf.start.y), (entity.dxf.end.x, entity.dxf.end.y)])
        elif isinstance(entity, LWPolyline):
            for pnt in entity.points():
                points.append((pnt[0], pnt[1]))
        elif isinstance(entity, Spline):
            approx_curve = entity.flattening(0.1)  # Flatten spline into a series of points
            for pnt in approx_curve:
                points.append((pnt[0], pnt[1]))  # Add the flattened points to the list
        elif isinstance(entity, Circle):
            # Circle doesn't need to be explicitly checked for closed loop, as it's inherently a closed shape
            closed_loops_count += 1  # A circle always counts as one closed loop
        elif isinstance(entity, Arc):
            spline = entity.to_spline()  # Convert the arc to a spline
            approx_curve = spline.flattening(0.01)  # Flatten the spline into points
            for pnt in approx_curve:
                points.append((pnt[0], pnt[1]))  # Add the flattened points to the list

    # Check if the points form a closed loop (first point equals the last point)
    if points and points[0] == points[-1]:
        closed_loops_count += 1

    # Increase the closed loops count
    increase_closed_loops(closed_loops_count)