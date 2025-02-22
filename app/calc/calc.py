from flask import Blueprint, jsonify

calc_blueprint = Blueprint('calc', __name__)

@calc_blueprint.route('/calc', methods=['GET'])
def hello_calc():
    return jsonify(message="Hello, Calc!")
