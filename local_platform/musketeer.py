import logging
import json

from flask import Flask, make_response, request, jsonify

from pycloudmessenger.ffl.abstractions import Notification


HOST = '127.0.0.1'
PORT = 5000

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

definition = {}
aggregator_queue = []
participant_queue = {}
participant_list = []
task_name = []


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    """
    Clear in-memory database.
    """
    global definition
    global aggregator_queue
    global participant_queue
    global participant_list
    global task_name

    definition = {}
    aggregator_queue = []
    participant_queue = {}
    participant_list = []
    task_name = []

    return make_response('', 200)


@app.route('/create_task', methods=['POST'])
def create_task():
    from datetime import datetime

    message = request.args['message']
    task_name.append({'task_name': request.args['task_name'], 'status': 'CREATED',
                      'added': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')})
    definition.update({'definition': message})

    return make_response('', 200)


@app.route('/task_info', methods=['GET'])
def task_info():
    return make_response(jsonify({'message': definition}), 200)


@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    return make_response(jsonify({'message': task_name}), 200)


@app.route('/get_joined_tasks', methods=['GET'])
def get_joined_tasks():
    user = request.args['message']
    result = task_name if user in participant_list else []

    return make_response(jsonify({'message': result}), 200)


@app.route('/join_task', methods=['POST'])
def join_task():
    message = request.args['message']
    aggregator_queue.append((message, Notification.participant_joined))

    return make_response('', 200)


@app.route('/get_participants', methods=['GET'])
def get_participants():
    return make_response(jsonify({'message': participant_list}), 200)


@app.route('/aggregator_send', methods=['POST'])
def aggregator_send():
    message = json.loads(request.args['message'])
    for user in participant_queue.keys():
        participant_queue[user].append(message)

    return make_response('', 200)


@app.route('/aggregator_receive', methods=['GET'])
def aggregator_receive():
    while True:
        if len(aggregator_queue) > 0:
            content = aggregator_queue[0]

            if content[1] is Notification.participant_joined:
                participant_list.append(content[0])
                participant_queue.update({content[0]: []})
                result = (Notification.participant_joined, content[0])

            elif content[1] is Notification.participant_updated:
                msg = {'notification': {'type': Notification.participant_updated}}
                result = {'params': content[0]}
                result.update(msg)

            del aggregator_queue[0]
            break

    return make_response(jsonify({'message': result}), 200)


@app.route('/participant_send', methods=['POST'])
def participant_send():
    message = json.loads(request.args['message'])
    aggregator_queue.append((message, Notification.participant_updated))

    return make_response('', 200)


@app.route('/participant_receive', methods=['GET'])
def participant_receive():
    user = request.args['user']

    while True:
        if len(participant_queue[user]) > 0:
            result = {'params': participant_queue[user][0]}
            del participant_queue[user][0]
            break

    return make_response(jsonify({'message': result}), 200)


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
