from flask import Blueprint, jsonify, request
from facades.swap import add_swap_task, fetch_swap_task

swap_routes = Blueprint('swap', __name__)

def init_routes(auth):
    @swap_routes.route('/create', methods=['POST'])
    @auth.required
    def create():
        payload = request.get_json()
        task = add_swap_task(payload)
        return jsonify(task), 200

    @swap_routes.route('/<id>', methods=['GET'])
    def get(id):
        task = fetch_swap_task(id)
        return jsonify(task), 200
