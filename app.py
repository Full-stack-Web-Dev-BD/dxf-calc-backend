from app import create_app



app = create_app()


# Serve 'uploads' directory as static
app.config['UPLOAD_FOLDER'] = 'uploads'
app.static_folder = 'uploads'




if __name__ == '__main__':
    app.run(debug=True)
    
