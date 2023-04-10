import requests
import shutil
from config import load_config

config = load_config()

TASKDIR = config['taskdir']

def download_url(src, dst):
    res = requests.get(src, stream=True)
    if res.status_code == 200:
        with open(dst, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        print('Image successfully Downloaded:', dst)
    else:
        print("Image Couldn't be retrieved")

def get_job_data(id):
    with open(f'{TASKDIR}/{id}/job.json') as data:
        job_data = json.load(data)
        return job_data
    return None


