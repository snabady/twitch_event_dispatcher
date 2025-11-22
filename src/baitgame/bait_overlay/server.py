from flask import Flask, render_template, request, Response
import json
import queue
import threading

app = Flask(__name__)

# Queue für Events, die an alle verbundenen Clients geschickt werden
event_queue = queue.Queue()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fishing', methods=['POST'])
def fishing_event():
    data = request.get_json(force=True)
    # Event in Queue legen
    event_queue.put(data)
    return {'status': 'ok'}

@app.route('/stream')
def stream():
    def event_stream():
        while True:
            data = event_queue.get()  # blockiert bis neues Event kommt
            yield f"data: {json.dumps(data)}\n\n"
    return Response(event_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8787, debug=True, threaded=True)

