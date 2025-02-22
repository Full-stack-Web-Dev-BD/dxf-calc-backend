import os
import json
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.calc.dxf.dxfparser import process_dxf_file

calc_blueprint = Blueprint('calc', __name__, url_prefix='/calc')

UPLOAD_FOLDER = 'uploads/calc'
CONFIG_PATH = 'app/config/materials.json'  # Path to material pricing JSON
ALLOWED_EXTENSIONS = {'dxf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load material pricing from JSON file
def load_materials():
    with open(CONFIG_PATH, 'r') as file:
        return json.load(file)



def calculate_price(data, material_data):
    try:
        # Extract values
        cutting_line = data['cutting_line']
        closed_loops = data['closed_loops']
        quantity = int(data['quantity'])
        material_name = data['material_name']
        thickness = str(data['thickness'])
        
        # Get bounding box dimensions (Width, Height)
        width_m = data['dimensions'][0] / 1000  # Convert mm → meters
        height_m = data['dimensions'][1] / 1000  # Convert mm → meters
        surface_area_m2 = width_m * height_m  # Corrected surface area calculation
        
        # Fetch material parameters
        material = material_data.get(material_name, {})
        params = material.get(thickness, {})

        if not params:
            return {"error": "Invalid material name or thickness"}, 400

        # Convert units
        cutting_line_m = cutting_line / 1000  # Convert mm → meters

        # Extract original cost values
        cost_per_m2 = params['cost_per_m2']
        cost_factor = params['cost_factor']
        loop_cost_per_loop = params['loop_cost']

        # Price calculation (strictly as per PDF)
        area_cost = round(surface_area_m2 * cost_per_m2, 2)
        cutting_cost = round(cutting_line_m * cost_factor, 2)
        loop_cost = round(closed_loops * loop_cost_per_loop, 2)

        # Total price per unit
        unit_price = area_cost + cutting_cost + loop_cost
        total_price = round(unit_price * quantity, 2)  # Multiply by quantity

        # Return full cost breakdown
        return {
            "material_name": material_name,
            "thickness": thickness,
            "quantity": quantity,
            "cost_breakdown": {
                "cutting_cost": cutting_cost,
                "loop_cost": loop_cost,
                "surface_area_cost": area_cost,
                "total_price": total_price
            },
            "original_costs": {
                "cost_per_m2": cost_per_m2,
                "cost_factor": cost_factor,
                "loop_cost_per_loop": loop_cost_per_loop
            }
        }

    except KeyError as e:
        return {"error": f"Missing parameter: {str(e)}"}, 400
    except Exception as e:
        return {"error": str(e)}, 500



@calc_blueprint.route('/upload_dxf', methods=['POST'])
def upload_dxf():
    # Verify request fields
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only DXF files are allowed.'}), 400

    # Extract additional parameters
    try:
        quantity = int(request.form.get('quantity'))
        material_name = request.form.get('material_name')
        thickness = request.form.get('thickness')
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid quantity, material, or thickness'}), 400

    # Generate unique file name
    file_id = str(uuid.uuid4())[:8]  # Generate short unique ID
    filename = secure_filename(file.filename)
    unique_filename = f"{filename.rsplit('.', 1)[0]}_{file_id}.dxf"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    file.save(file_path)

    try:
        # Process DXF file
        dxf_data = process_dxf_file(file_path)
        dxf_data.update({'quantity': quantity, 'material_name': material_name, 'thickness': thickness})

        # Load pricing data & calculate price
        materials = load_materials()
        price = calculate_price(dxf_data, materials)

        # Generate file URL
        file_url = f"http://127.0.0.1:5000/{UPLOAD_FOLDER}/{unique_filename}"

        # Return response
        response = {
            'success': True,
            'file_url': file_url,
            'data': dxf_data,
            'price': price
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)  # Ensure file is deleted after processing
