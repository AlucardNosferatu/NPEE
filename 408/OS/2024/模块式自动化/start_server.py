from server.flask_server import flask_app

if __name__ == '__main__':
    flask_app.run(
        host='0.0.0.0',
        port=20291,
        debug=False,
        threaded=True
    )
