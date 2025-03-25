from flask import Flask
from routes.mobile_routes import mobile_bp
app = Flask(__name__)
app.register_blueprint(mobile_bp)
if __name__ == '__main__':
    app.run(port=5006, debug=True)