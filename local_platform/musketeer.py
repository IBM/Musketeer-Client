import logging

from flask import Flask, make_response, request, jsonify

from pycloudmessenger.ffl.abstractions import Notification


HOST = '127.0.0.1'
PORT = 5000
NOT_FOUND = 404
OK = 200
CONFLICT = 409

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

    return make_response('', OK)


@app.route('/create_task', methods=['POST'])
def create_task():
    from datetime import datetime

    global task_name
    global definition

    message = request.args['message']
    task_name.append({'task_name': request.args['task_name'], 'status': 'CREATED',
                      'added': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')})
    definition.update({'definition': message})

    return make_response('', OK)


@app.route('/task_info', methods=['GET'])
def task_info():
    global definition
    return make_response(jsonify({'message': definition}), OK)


@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    global task_name
    return make_response(jsonify({'message': task_name}), OK)


@app.route('/get_joined_tasks', methods=['GET'])
def get_joined_tasks():
    global participant_list

    user = request.args['message']
    result = task_name if user in participant_list else []

    return make_response(jsonify({'message': result}), OK)


@app.route('/join_task', methods=['POST'])
def join_task():
    global aggregator_queue
    global participant_list

    message = request.args['message']

    if not ((message in participant_list) or ((message, Notification.participant_joined) in aggregator_queue)):
        aggregator_queue.append((message, Notification.participant_joined))
        return make_response('', OK)
    else:
        return make_response('', CONFLICT)


@app.route('/get_participants', methods=['GET'])
def get_participants():
    global participant_list
    return make_response(jsonify({'message': participant_list}), OK)


@app.route('/aggregator_send', methods=['POST'])
def aggregator_send():
    global participant_queue

    message = request.json['message']

    for user in participant_queue.keys():
        participant_queue[user].append(message)

    return make_response('', OK)


@app.route('/aggregator_receive', methods=['GET'])
def aggregator_receive():
    global aggregator_queue
    global participant_list
    global participant_queue

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

        final_msg = make_response(jsonify({'message': result}), OK)

        del aggregator_queue[0]

    else:
        final_msg = make_response('', NOT_FOUND)

    return final_msg


@app.route('/participant_send', methods=['POST'])
def participant_send():
    global aggregator_queue

    message = request.json['message']
    aggregator_queue.append((message, Notification.participant_updated))

    return make_response('', OK)


@app.route('/participant_receive', methods=['GET'])
def participant_receive():
    global participant_queue

    user = request.args['user']

    if len(participant_queue[user]) > 0:
        result = participant_queue[user][0]
        final_msg = make_response(jsonify({'message': result}), OK)

        del participant_queue[user][0]

    else:
        final_msg = make_response('', NOT_FOUND)

    return final_msg


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
