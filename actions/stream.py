from config import load_config
from SimSwap.options.test_options import TestOptions
from helpers.utils import download_url
from stream import start, stop, generate

config = load_config()
auth_secret_key = config['auth']['secret_key']
crop_size = config['stream']['crop_size']
arc_path = config['swap']['arc_path']
stream_out_path = config['stream']['output_path']
stream_out_dir = config['stream']['output_dir']
temp_face_path = config['stream']['temp_face_path']

def start_stream(payload, auth):
    # FR:
    # * Partitions per user identity
    try:
        target_url=payload['target']
        download_url(target_url, temp_face_path)
        opt = TestOptions().parse()
        if payload['fine']:
            opt.crop_size = crop_size
        opt.use_mask = True
        opt.name = 'people'
        opt.Arc_path = arc_path
        opt.pic_a_path = temp_face_path
        opt.pic_b_path = payload['source']
        opt.video_path = payload['source']
        opt.output_path = stream_out_path
        opt.temp_path = stream_out_dir
        stop()
        return start(opt=opt)
    except Exception as e:
        print(f"Error: {e}")
        return {"success": False, "message": "An error occurred while starting stream."}

def stop_stream():
    try:
        return stop()
    except Exception as e:
        print(f"Error: {e}")
        return {"success": False, "message": "An error occurred while stopping stream."}

def generate_stream():
    try:
        return generate()
    except Exception as e:
        print(f"Error: {e}")
        return {"success": False, "message": "An error occurred during generate operation."}


