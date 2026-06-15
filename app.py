import uuid

from flask import Flask, request, jsonify


app = Flask(__name__)

todo_lists = []
todos = []

def entry_public(entry):
    return {"id": entry["id"], "name": entry["name"], "description": entry["description"]}

@app.after_request
def apply_cors_header(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,DELETE,PATCH,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.errorhandler(404)
def not_found(_e):
    return jsonify({"message": "Die angeforderte ID wurde nicht gefunden."}), 404

@app.errorhandler(500)
def server_error(_e):
    return jsonify({"message": "Interner Server-Fehler."}), 500

def find_list(list_id):
    for item in todo_lists:
        if item["id"] == list_id:
            return item
    return None

def find_entry(entry_id):
    for item in todos:
        if item["id"] == entry_id:
            return item
    return None

@app.route("/todo-list", methods=["POST", "GET"])
def todo_list_collection():
    if request.method == "POST":
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"id": "", "name": ""}), 406
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            return jsonify({"id": "", "name": ""}), 406
        new_id = str(uuid.uuid4())
        item = {"id": new_id, "name": name.strip()}
        todo_lists.append(item)
        return jsonify(item), 201
    return jsonify(todo_lists), 200

@app.route("/todo-list/<list_id>", methods=["GET", "DELETE", "POST"])
def todo_list_by_id(list_id):
    list_item = find_list(list_id)
    if not list_item:
        return jsonify({"message": "Die angeforderte ID wurde nicht gefunden."}), 404
    if request.method == "GET":
        return jsonify([entry_public(e) for e in todos if e["list"] == list_id]), 200
    if request.method == "DELETE":
        todo_lists.remove(list_item)
        todos[:] = [e for e in todos if e["list"] != list_id]
        return jsonify({"message": "Liste gelöscht."}), 204
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        data = {}
    name = data.get("name", "")
    desc = data.get("description", "")
    if name is None:
        name = ""
    if desc is None:
        desc = ""
    if not isinstance(name, str):
        name = str(name)
    if not isinstance(desc, str):
        desc = str(desc)
    new_id = str(uuid.uuid4())
    entry = {"id": new_id, "name": name, "description": desc, "list": list_id}
    todos.append(entry)
    return jsonify(entry_public(entry)), 201

@app.route("/entry/<entry_id>", methods=["PATCH", "DELETE"])
def entry_by_id(entry_id):
    entry = find_entry(entry_id)
    if not entry:
        return jsonify({"message": "Die angeforderte ID wurde nicht gefunden."}), 404
    if request.method == "DELETE":
        todos.remove(entry)
        return jsonify({"message": "Eintrag gelöscht."}), 204
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return jsonify(entry_public(entry)), 406
    if "name" in data and data["name"] is not None and not isinstance(data["name"], str):
        return jsonify(entry_public(entry)), 406
    if "description" in data and data["description"] is not None and not isinstance(
        data["description"], str
    ):
        return jsonify(entry_public(entry)), 406
    if "name" in data and data["name"] is not None:
        entry["name"] = data["name"]
    if "description" in data and data["description"] is not None:
        entry["description"] = data["description"]
    return jsonify(entry_public(entry)), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
