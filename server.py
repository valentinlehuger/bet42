#!python
from gevent import monkey
monkey.patch_all()
from server import create_app, socketio

app = create_app(True)

if __name__ == '__main__':
    socketio.run(app)
