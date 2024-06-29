from flask import Flask
from flask_cors import CORS
from routes import init_routes
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

CORS(app, supports_credentials=True, origins=["https://localhost:5173"])
init_routes(app)

if __name__ == "__main__":
    app.run(ssl_context=('./certs/cert.pem', './certs/key.pem'), debug=True)
