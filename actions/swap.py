import os
import uuid
from datetime import datetime
from helpers.s3 import download, upload
from helpers.utils import download_url
from helpers.utils import get_job_data
from SimSwap.swapmulti import process
from SimSwap.options.test_options import TestOptions
from config import load_config

config = load_config()
TASKDIR = config['taskdir']
TASK_BUCKET = config['aws']['task_bucket']
STATUS_INIT = config['app']['statuses']['init']
STATUS_DONE = config['app']['statuses']['done']
crop_size = config['swap']['crop_size']
arc_path = config['swap']['arc_path']

def create_swap_task(payload):
    # FR:
    # * Partitions per user identity
    try:
        dt = datetime.now()
        remaining = 300
        job = {
            'crop_size': crop_size,
            'success': True,
            'id': str(uuid.uuid4()),
            'status': 'INIT',
            'video': payload['video'],
            'targets': payload['targets'],
            'ts': datetime.timestamp(dt),
            'remaining_ts': datetime.timestamp(dt) + remaining
        }
        job_dir = os.path.join(TASKDIR, job["id"])
        os.makedirs(f'{job_dir}/tmp', exist_ok=True)
        job_filename = os.path.join(job_dir, 'job.json')
        job['path'] = job_filename
        # with open(job_filename, 'w') as outfile:
        #     json.dump(job, outfile)

        download_url(job['video'], os.path.join(job_dir, 'source'))
        download_url(job['targets'][0]['face'], os.path.join(job_dir, 'face'))

        opt = TestOptions().parse()
        if payload['fine']:
            opt.crop_size = crop_size
        opt.use_mask = True
        opt.name = 'people'
        opt.Arc_path = arc_path,
        opt.pic_a_path = f'{job_dir}/face'
        opt.video_path = f'{job_dir}/source'
        opt.output_path = f'{job_dir}/final.mp4'
        opt.temp_path = f'{job_dir}/tmp'
        process(job=job, opt=opt)
        upload(TASK_BUCKET, job_filename, job_filename)
        return job
    except Exception as e:
        print(f"Error: {e}")
        return {"success": False, "message": "An error occurred while creating the swap task."}

def get_swap_task(id):
    try:
        job_file = f'{TASKDIR}/{id}/job.json'
        job_data = get_job_data(id)
        if job_data['status'] == 'DONE':
            return job_data
        job_data = download(TASK_BUCKET, job_file, job_file)
        return job_data
    except Exception as e:
        print(f"Error: {e}")
        return {"success": False, "message": "An error occurred while obtaining the swap task data."}
