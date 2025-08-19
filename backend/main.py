from app import create_app
import os

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Run development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )