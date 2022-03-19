import json

from flask import request

from MediaAgent import app


@app.route("/recv", methods=['POST'])
def recv():
    if request.method == "POST":
        c_da = request.data
        data = json.loads(c_da.decode())

        return json.dumps(
            {
                '经典的错误': '标注的零分'
            },
            ensure_ascii=False
        )


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("20291"),
        debug=True, threaded=True
    )
