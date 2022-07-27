from flask import Flask, session, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
from flaskext.mysql import MySQL

import datetime

app: Flask = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'

socketio = SocketIO(app, cors_allowed_origins='*')
# MYSQL Config

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1235789'
app.config['MYSQL_DATABASE_DB'] = 'newdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

conn = mysql.connect()

cursor = conn.cursor()
# create a new db if you have not created yet or remove comment from next line
# cursor.execute("create database newdb;")
cursor.execute("use newdb;")


@app.route('/', methods=['GET', 'POST'])
def index():
    return jsonify({'error': "Method not allowed"})


@socketio.on('join', namespace='/chat')
def join(message):
    room = message['roomId']
    username = message['username']
    join_room(room)
    query = "Select username,roomId from user where username='%s'" % username + ' ; '

    cursor.execute(query)
    user = cursor.fetchall()

    # if user not exist then create new user
    if len(user) == 0:
        try:
            query = "Insert into user values (0,'%s','%s')" % (username, room)
            cursor.execute(query)
            conn.commit()
            addNewMsg(msg=username + ' has entered the room.', username=username, room=room)

        except Exception as e:
            print(e)
    else:
        if user[0][1] != room:
            query = "UPDATE user SET roomId = '%s' WHERE username = '%s';" % (room, username)
            cursor.execute(query)
            conn.commit()
            addNewMsg(msg=username + ' has entered the room.', username=username, room=room)
    emit('message', {'msg': getChats(room)}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = message['room']
    username = message['username']
    addNewMsg(msg=username + " : " + message['msg'], username=username, room=room)
    emit('message', {'msg': getChats(room)}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = message['room']
    username = message['username']
    addNewMsg(msg=username + ' has left the room.', username=username, room=room)
    leave_room(room)
    session.clear()
    lst = getChats(room)
    if len(lst) == 0:
        emit('message', {'msg': [{'msg': "No messages has been sent"}]})
    else:
        emit('message', {'msg': lst}, room=room)


def addNewMsg(msg, room, username):
    x = datetime.datetime.now()
    try:
        query = "insert into chats(msg, room, username,ts) values('%s','%s','%s','%s');" % (msg, room, username, x)
        print(query)
        cursor.execute(query)
        conn.commit()
    except Exception as e:
        print(e)


def getChats(room):
    query = "select msg,ts from chats where room='%s' order by ts ; " % room
    print(query)
    cursor.execute(query)
    msgLst = cursor.fetchall()
    lst = []
    for msg in msgLst:
        lst.append({'msg': msg[0], 'ts': str(msg[1])})
    return lst


if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app, debug=True)
