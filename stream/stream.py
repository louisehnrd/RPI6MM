#!/usr/bin/python3
from flask import Flask, render_template
from flask_socketio import SocketIO
import socket
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)
app.config["DEBUG"] = True

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("192.168.0.172", 5000))
        while True:
            frame_data = sock.recv(4096)
            socketio.emit('video_frame', frame_data, binary=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
