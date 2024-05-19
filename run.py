# run.py

from app.main import create_app

# Create an instance of the Flask application
app = create_app()

if __name__ == '__main__':
    # Run the Flask app
    # You can specify the host and port number inside app.run()
    # For example, app.run(host='0.0.0.0', port=5000)
    app.run(host='0.0.0.0', port=5000, debug=True)  # Set debug=False in a production environment
