import base64
import io
from http import HTTPStatus

from flask import url_for, current_app
from rq import SimpleWorker

from app import q, Document
# noinspection PyUnresolvedReferences
from .fixture import *


def test_empty_db(client):
    file_body = open('test/simple1.pdf', 'br').read()
    data = {'file': (io.BytesIO(file_body), 'simple1.pdf')}
    with app.app_context():
        response = client.post(
            url_for('document_add'), data=data,
            content_type='multipart/form-data'
        )
    assert response.status_code == HTTPStatus.OK
    assert {'document_id': 1, 'status': 'PROCESSING'} == response.json

    document = Document.get_document(1)
    assert document
    assert file_body == base64.b64decode(document.body)

    jobs = q.get_jobs()
    assert 1 == len(jobs)
    assert jobs[0].func_name == 'task.process_document'

    worker = SimpleWorker([q], connection=q.connection)
    worker.work(burst=True)
