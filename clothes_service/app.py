from flask import Flask
from routes.clothes_routes import clothes_bp
app = Flask(__name__)
app.register_blueprint(clothes_bp)
if __name__ == '__main__':
    app.run(port=5007, debug=True)