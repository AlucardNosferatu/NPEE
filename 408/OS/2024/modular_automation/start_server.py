import threading

from core.scheduler_fcfs import process_queued_task
from server.flask_server import flask_app

if __name__ == '__main__':
    pqt_thread = threading.Thread(target=process_queued_task)
    pqt_thread.start()
    flask_app.run(
        host='0.0.0.0',
        port=20291,
        debug=False,
        threaded=True
    )
