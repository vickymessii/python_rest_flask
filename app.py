from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
import pymysql
import json
from datetime import date, datetime

db = pymysql.connect("localhost", "root", "", "unicef")

app = Flask(__name__)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)


@app.route("/")
def index():
    cursor = db.cursor()
    sql = "SELECT * FROM apps_countries"
    cursor.execute(sql)
    # results = cursor.fetchall()
    # results = list(cursor)
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(["id", "code", "name"], row)))
    return (jsonify({"status": "success", "data": results}), 200)
    # return "Hello, World!"


tasks = [
    {
        "id": 1,
        "title": u"Buy groceries",
        "description": u"Milk, Cheese, Pizza, Fruit, Tylenol",
        "done": False,
    },
    {
        "id": 2,
        "title": u"Learn Python",
        "description": u"Need to find a good Python tutorial on the web",
        "done": False,
    },
]


@app.route("/todo/api/v1.0/tasks", methods=["GET"])
def get_tasks():
    return jsonify({"status": "success", "tasks": tasks}), 200


@app.route("/todo/api/v1.0/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = [task for task in tasks if task["id"] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({"status": "success", "task": task[0]}), 200


@app.route("/todo/api/v1.0/tasks", methods=["POST"])
def create_task():
    if not request.json or not "title" in request.json:
        abort(400)
    task = {
        "id": tasks[-1]["id"] + 1,
        "title": request.json["title"],
        "description": request.json.get("description", ""),
        "done": False,
    }
    tasks.append(task)
    return jsonify({"status": "success", "task": task}), 200


@app.route("/todo/api/v1.0/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = [task for task in tasks if task["id"] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if "title" in request.json and type(request.json["title"]) != unicode:
        abort(400)
    if (
        "description" in request.json
        and type(request.json["description"]) is not unicode
    ):
        abort(400)
    if "done" in request.json and type(request.json["done"]) is not bool:
        abort(400)
    task[0]["title"] = request.json.get("title", task[0]["title"])
    task[0]["description"] = request.json.get("description", task[0]["description"])
    task[0]["done"] = request.json.get("done", task[0]["done"])
    return jsonify({"task": task[0]})


@app.route("/todo/api/v1.0/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = [task for task in tasks if task["id"] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({"result": True})


if __name__ == "__main__":
    app.run(debug=True)
