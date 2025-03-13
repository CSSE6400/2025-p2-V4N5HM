from flask import Blueprint, jsonify, request
from todo.models import db 
from todo.models.todo import Todo
from datetime import datetime, timedelta

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/health')
def health():
    return jsonify({"status": "ok"})

@api.route('/todos', methods=['GET'])
def get_todos():
    query = Todo.query

    if request.args.get('completed') == "true":
        query = query.filter_by(completed=True)

    if request.args.get("window"):
        try:
            days = int(request.args.get("window"))
            window_end = datetime.now() + timedelta(days=days)
            query = query.filter(Todo.deadline_at <= window_end)
        except ValueError:
            return jsonify({'error': 'Invalid window parameter'}), 400

    return jsonify([todo.to_dict() for todo in query.all()])

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = db.session.get(Todo, todo_id)  
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():
    allowed_fields = {"title", "description", "completed", "deadline_at"}
    extra_fields = set(request.json.keys()) - allowed_fields

    if extra_fields:
        return jsonify({'error': f'Unexpected fields: {extra_fields}'}), 400

    if 'title' not in request.json or not request.json.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )

    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))

    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201



@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404

    allowed_fields = {"title", "description", "completed", "deadline_at"}
    extra_fields = set(request.json.keys()) - allowed_fields

    if extra_fields:
        return jsonify({'error': f'Unexpected fields: {extra_fields}'}), 400

    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)

    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))

    db.session.commit()
    return jsonify(todo.to_dict())


@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = db.session.get(Todo, todo_id) 
    if todo is None:
        return jsonify({}), 200

    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200