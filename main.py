from flask import Flask
from flask_cors import CORS
from middleware.auth import Auth
from config import load_config
from routes.stream import stream_routes, init_routes as init_stream_routes
from routes.swap import swap_routes, init_routes as init_swap_routes

app = Flask(__name__)


config = load_config()

API_HOST = config['app']['expose']
API_PORT = config['app']['port']
ALLOWED_DOMAINS = config['app']['allowed_domains']
TASKDIR = config['taskdir']
AWS_ACCESS_KEY = config['aws']['access_key']
AWS_SECRET_ACCESS_KEY = config['aws']['secret_access_key']
TASK_BUCKET = config['aws']['task_bucket']
auth_secret_key = config['auth']['secret_key']

CORS(app, resources={r"/api/*": {"origins": ','.join(ALLOWED_DOMAINS)}})

auth = Auth(auth_secret_key)

# Register blueprints
init_swap_routes(auth)
app.register_blueprint(swap_routes, url_prefix='/api/swap')

init_stream_routes(auth)
app.register_blueprint(stream_routes, url_prefix='/api/stream')

if __name__ == '__main__':
    app.run(host=API_HOST, port=API_PORT, debug=True, threaded=True, use_reloader=False)
