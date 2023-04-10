from flask import Blueprint, jsonify, request, Response
from facades.stream import start_stream_with_auth, stop_stream_with_auth, stream

stream_routes = Blueprint('stream', __name__)

def init_routes(auth):
    @stream_routes.route('/start', methods=['POST'])
    @auth.required
    def start():
        payload = request.get_json()
        response = start_stream_with_auth(payload, auth)
        return jsonify(response), 200

    @stream_routes.route('/stop', methods=['GET'])
    def stop():
        response = stop_stream_with_auth()
        return jsonify(response), 200

    @stream_routes.route('/stream', methods=['GET'])
    def generate():
        return Response(stream(), mimetype="multipart/x-mixed-replace; boundary=frame")
