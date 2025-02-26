from app import create_app
from flask_cors import CORS

app = create_app()

# Enable CORS for all routes
CORS(app)

# Serve 'uploads' directory as static
app.config['UPLOAD_FOLDER'] = 'uploads'
app.static_folder = 'uploads'

if __name__ == '__main__':
    app.run(debug=True)
