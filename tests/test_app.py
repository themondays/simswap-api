import unittest
import json
from main import app

from flask_testing import TestCase

class TestApp(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_create_swap_task(self):
        payload = {
            "video": "https://example.com/video.mp4",
            "targets": [
                {
                    "face": "https://example.com/face.jpg"
                }
            ]
        }
        response = self.client.post('/swap/create', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_get_swap_task(self):
        # Replace the 'op_id' value with a valid ID from your application for testing purposes
        op_id = "your_swap_task_id_here"
        response = self.client.get(f'/swap/{op_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_stream_start(self):
        payload = {
            "source": "https://example.com/source_video.mp4",
            "target": "https://example.com/target_face.jpg"
        }
        response = self.client.post('/stream/start', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_stream_stop(self):
        response = self.client.get('/stream/stop')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

if __name__ == '__main__':
    unittest.main()

