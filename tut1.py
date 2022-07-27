from flask import Flask, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit

# Flask App Config
app: Flask = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'

# CORS_ALLOWED_ORIGINS is the list of origins authorized to make requests.
socketio = SocketIO(app, cors_allowed_origins='*')


# Home Page
@app.route('/', methods=['GET', 'POST'])
def index():
    return jsonify({'data': "Web Socket Example"})


@socketio.on('join', namespace='/chat')
def join(message):
    # we need roomId and Username for joining the room
    room = message['roomId']
    username = message['username']
    # join room
    join_room(room)
    print("joined")
    # Emit message or notifier to other user of same room
    emit('message', {"msg": str(username) + 'has joined the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = message['room']
    username = message['username']
    msg = message['msg']
    print("texted")
    emit('message', {"msg": str(username) + ' : ' + str(msg)}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = message['room']
    username = message['username']
    # leaving the room
    leave_room(room=room)
    emit('message', {"msg": str(username) + 'has left the room.'}, room=room)


if __name__ == '__main__':
    # Run Flask-SocketIO App
    socketio.run(app, debug=True)
