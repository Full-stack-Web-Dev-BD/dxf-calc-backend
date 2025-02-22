from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Load material data
with open('materials.json', 'r') as f:
    MATERIALS = json.load(f)

def calculate_price(data):
    try:
        # Extract values
        cutting_line = data['cutting_line']  # in mm
        surface_area = data['surface_area']  # in mm²
        closed_loops = data['closed_loops']
        quantity = data['quantity']
        material = MATERIALS[data['material_name']]
        thickness = str(data['thickness'])
        
        # Get material parameters
        params = material[thickness]
        
        # Unit conversions
        surface_area_m2 = surface_area / 1_000_000  # mm² → m²
        cutting_line_m = cutting_line / 1000        # mm → meters
        
        # Calculation (adjusted to match PHP logic)
        setup_cost = params['setup_price']
        cutting_cost = cutting_line_m * params['cost_factor']
        loop_cost = closed_loops * params['loop_cost']
        area_cost = surface_area_m2 * params['cost_per_m2']
        
        # Total per unit (critical fix: add all components)
        unit_price = setup_cost + cutting_cost + loop_cost + area_cost
        
        # Apply quantity and round
        total_price = round(unit_price * quantity, 2)
        
        return total_price
        
    except KeyError as e:
        return {"error": f"Missing parameter: {str(e)}"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/calc', methods=['POST'])
def handle_calculation():
    data = request.get_json()
    
    # Validate input
    required = ['cutting_line', 'surface_area', 'closed_loops', 
               'material_name', 'thickness', 'quantity']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
        
    # Calculate and return
    result = calculate_price(data)
    if isinstance(result, tuple):  # Error case
        return jsonify(result[0]), result[1]
        
    return jsonify({
        "price": result,
        "currency": "EUR",
        "material": data['material_name'],
        "thickness": data['thickness'],
        "quantity": data['quantity']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)