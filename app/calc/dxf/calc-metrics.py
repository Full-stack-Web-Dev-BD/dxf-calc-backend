import os, argparse, json
from datetime import datetime
import ezdxf

from metrics.path_length import *
from metrics.surface_area import *
from metrics.closed_loops import *


shapes = ('LINE', 'ARC', 'CIRCLE', 'SPLINE', 'POLYLINE')
# shapes = ('LINE', 'ARC', 'SPLINE', 'POLYLINE')

methods = {
	'total_path_length_LINE': calc_length_line,
	'total_path_length_SPLINE': calc_length_spline,
	'total_path_length_POLYLINE': calc_length_polyline,
	'total_path_length_CIRCLE': calc_length_circle,
	'total_path_length_ARC': calc_length_arc,

	'surface_area_LINE': calc_extreme_points_line,
	'surface_area_SPLINE': calc_extreme_points_spline,
	'surface_area_POLYLINE': calc_extreme_points_polyline,
	'surface_area_CIRCLE': calc_extreme_points_circle,
	'surface_area_ARC': calc_extreme_points_arc,

	'closed_loops_LINE': calc_closed_loops_line,
	'closed_loops_SPLINE': calc_closed_loops_spline,
	'closed_loops_POLYLINE': calc_closed_loops_polyline,
	'closed_loops_CIRCLE': calc_closed_loops_circle,
	'closed_loops_ARC': calc_closed_loops_arc
}

parser = argparse.ArgumentParser()
parser.add_argument('--dxf') 
dxf_file = parser.parse_args().dxf

doc = ezdxf.readfile(dxf_file)


def check_entity_type(kind):
	if kind in shapes:
		return True
	else:
		# print('Unknown entity type: ' + kind )
		dir_path = os.path.dirname(os.path.realpath(__file__))
		unknown_shapes_types_filename = f'{dir_path}/../unknown_entity_types.txt'
		with open(unknown_shapes_types_filename, 'a') as file:
			msg = f'Unknown entity type - {datetime.now()}\n\tName: {kind}\n\tFile: {dxf_file}\n\n'
			file.write(msg)
		return False


def perform_calculation(action):
	shp = 0
	for shape in doc.entities:
		if not check_entity_type(shape.dxftype()):
			continue

		ref = action + '_' + shape.dxftype()
		print('Running method:', action, shape.dxftype()) 
		methods[ref](shape)
		# print(shape, shape.dxf.handle, shape.dxf.owner, shape.uuid, shape.is_bound)

		print()
		shp += 1

	print(f'Shapes total: {shp}\n')


def main():
	perform_calculation('total_path_length')
	perform_calculation('surface_area')
	perform_calculation('closed_loops')

	output = {
		'cutting_line': total_path_length(),
		'surface_area': surface_area(),
		'dimensions': dimensions(),
		'closed_loops': closed_loops()
	}
	
	print(json.dumps(output))


main()