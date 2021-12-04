import json
import unittest
import requests
from db import connect, delete_job

LOCAL = False

if LOCAL:
    print("Be sure to have the app running!!")


class TestAppApi(unittest.TestCase):
    def setUp(self):
        self.conn = connect()
        if LOCAL:
            self.base_url = 'http://127.0.0.1:5000/'
        else:
            self.base_url = 'https://musical-notes-converter.herokuapp.com/'

    def post_request(self, payload, append_url=''):
        url = self.base_url + append_url
        headers = {'content-type': 'application/json'}
        resp = requests.post(url, data=json.dumps(payload), headers=headers)
        return resp.status_code, resp.json()

    def test_success_hit(self):
        payload = {
            "title": "Score1",
            "mainSheet": "asd"
        }
        status_code, message = self.post_request(payload)

        self.assertEqual([status_code, message['message'],
                         message['numInstruments']], [200, 'Started', 2])
        job_id = message['jobId']

        payload = {
            "jobId": job_id
        }
        status_code, message = self.post_request(payload, append_url='status')
        self.assertEqual([status_code, message['message'],
                         message['doneInstrumentsArr']], [200, 'Running', []])

        # Clean up
        delete_job(self.conn, job_id)

    def test_double_hits(self):
        payload = {
            "title": "Score1",
            "mainSheet": "asd"
        }
        self.post_request(payload)
        status_code, message = self.post_request(payload)

        self.assertEqual([status_code, message['message'], message['numInstruments']], [
                         200, 'Currently Running', 2])
        job_id = message['jobId']

        # Clean up
        delete_job(self.conn, job_id)

    def test_entire_conversion(self):
        payload = {
            "title": "Score1",
            "mainSheet": "asd"
        }
        _, message = self.post_request(payload)

        job_id = message['jobId']
        payload = {
            "jobId": job_id
        }
        _, message = self.post_request(payload, append_url='status')
        status = message['message']
        while status == 'Running':
            _, message = self.post_request(
                payload, append_url='status')
            status = message['message']
            try:
                instruments = message['doneInstrumentsArr']
            except BaseException:
                pass
        self.assertEqual(status, 'Done')
        self.assertEqual(instruments, ['F. VOICE 2', 'VIOLIN 1'])
        # Clean up
        delete_job(self.conn, job_id)
