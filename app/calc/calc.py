import os
import uuid  # Import UUID for unique file naming
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.calc.dxf.dxfparser import process_dxf_file

calc_blueprint = Blueprint('calc', __name__, url_prefix='/calc')

UPLOAD_FOLDER = 'uploads/calc'
ALLOWED_EXTENSIONS = {'dxf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@calc_blueprint.route('/upload_dxf', methods=['POST'])
def upload_dxf():
    print("Uploading DXF")

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Generate unique ID and append to filename
        unique_id = str(uuid.uuid4())[:8]  # Shorter UUID
        new_filename = f"{filename.rsplit('.', 1)[0]}_{unique_id}.dxf"
        
        file_path = os.path.join(UPLOAD_FOLDER, new_filename)
        file.save(file_path)

        try:
            result = process_dxf_file(file_path)

            # Generate the file URL
            file_url = request.host_url + f'uploads/calc/{new_filename}'

            return jsonify({'success': True, 'data': result, 'file_url': file_url}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type. Only DXF files are allowed.'}), 400
