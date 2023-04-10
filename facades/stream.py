from actions.stream import start_stream, stop_stream, generate_stream
from config import load_config

config = load_config()
auth_secret_key = config['auth']['secret_key']

def stream():
    try:
        return generate_stream()
    except Exception as e:
        print(f"Error: {e}")
        return {"success": False, "message": "An error occurred during generate operation."}

def start_stream_with_auth(payload, auth):
    return start_stream(payload, auth)

def stop_stream_with_auth():
    return stop_stream()
