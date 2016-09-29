from . import main
from flask import request

@main.route("/test-operator-ses/post",methods=["POST"])
def root():
    request_data = "*"*50+'\n'
    request_data += request.data
    request_data += '\n'
    print request.is_json
    return request_data

@main.route("/test-operator-ses", methods=["GET"])
def index():
    return "test-operator-ses, just for debug"

@main.route("/test-operator-ses/tasks/<task_id>", methods=["GET"])
def tasks(task_id):
    return "{task-id: %s}" % (task_id)



