from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
socketio = SocketIO(app)

users = {}

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on("typing")
def handle_typing(username):
    emit("typing", username, broadcast=True, include_self=False)

@socketio.on("join")
def handle_join(username):
    users[request.sid] = username
    send(f"{username} joined the chat", broadcast=True)
    emit("users", list(users.values()), broadcast=True)


@socketio.on("message")
def handle_message(msg):
    send(msg, broadcast=True)


@socketio.on("disconnect")
def handle_disconnect():
    username = users.get(request.sid)

    if username:
        send(f"{username} left the chat", broadcast=True)
        del users[request.sid]
        emit("users", list(users.values()), broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)