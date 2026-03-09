from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, send, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

@app.route("/")
def home():
    return render_template("index.html")

# Essential for PWA Installability
@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('static', 'sw.js')

# ... rest of your socketio logic ...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)