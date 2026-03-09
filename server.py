from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import sqlite3
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

DB = "chat.db"


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room TEXT,
        sender TEXT,
        message TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


def get_private_room(u1, u2):
    return "_".join(sorted([u1, u2]))


@app.route("/")
def home():
    return render_template("index.html")


@socketio.on("join")
def handle_join(username):

    users[request.sid] = username

    join_room("global")

    emit("users", list(users.values()), broadcast=True)


@socketio.on("open_private")
def open_private(data):

    user1 = users.get(request.sid)
    user2 = data["target"]

    room = get_private_room(user1, user2)

    join_room(room)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT sender,message FROM messages WHERE room=?", (room,))
    history = c.fetchall()

    conn.close()

    emit("history", history)


@socketio.on("send_global")
def send_global(msg):

    sender = users.get(request.sid)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "INSERT INTO messages(room,sender,message) VALUES(?,?,?)",
        ("global", sender, msg)
    )

    conn.commit()
    conn.close()

    emit("message", {"user": sender, "msg": msg}, room="global")


@socketio.on("send_private")
def send_private(data):

    sender = users.get(request.sid)
    receiver = data["to"]
    msg = data["msg"]

    room = get_private_room(sender, receiver)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "INSERT INTO messages(room,sender,message) VALUES(?,?,?)",
        (room, sender, msg)
    )

    conn.commit()
    conn.close()

    emit("private_message", {"user": sender, "msg": msg}, room=room)


@socketio.on("disconnect")
def disconnect():

    users.pop(request.sid, None)

    emit("users", list(users.values()), broadcast=True)


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    socketio.run(app, host="0.0.0.0", port=port)