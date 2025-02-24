# Total cutting path length calculation

import math
from ezdxf.math import ConstructionPolyline


total_length = 0

def reset_total_length():
    global total_length
    total_length = 0

def total_path_length():
	return total_length


def increase_path_length(length):
	global total_length
	total_length += length
	# print(f"[Total path length:] {total_length}")


def calc_length_line(shape):
	length = shape.dxf.start.distance(shape.dxf.end)
	# print(shape, length, shape.dxf.start, shape.dxf.end)
	increase_path_length(length)


def calc_length_polyline(shape):
	# print(shape, shape.is_closed)
	points = [point for point in shape.points()]
	poly_length = 0
	for indx, point in enumerate(points):
		if not shape.is_closed and indx == 0:
			# print(indx, point)
			continue
		else:
			length = point.distance(points[indx - 1])
			poly_length += length
		# print(indx, point, length, poly_length)

	increase_path_length(poly_length)


def calc_length_spline(shape):
	approx_curve = shape.flattening( 0.1 )
	polyline = ConstructionPolyline(vertices = approx_curve, close = shape.closed)
	spline_length = polyline.length
	# print(shape, shape.closed, spline_length)
	increase_path_length(spline_length)


def calc_length_circle(shape):
	circumference = 2 * math.pi * shape.dxf.radius
	# print(shape, circumference, shape.dxf.center, shape.dxf.radius)
	increase_path_length(circumference)


def calc_length_arc(shape):
	if shape.dxf.start_angle > shape.dxf.end_angle:
		alfa = 360 - shape.dxf.start_angle + shape.dxf.end_angle
	else:
		alfa = shape.dxf.end_angle - shape.dxf.start_angle
	arc_length = math.pi * shape.dxf.radius * alfa / 180
	# print(shape, arc_length, shape.dxf.center, shape.dxf.radius, shape.dxf.start_angle, shape.dxf.end_angle)
	increase_path_length(arc_length)