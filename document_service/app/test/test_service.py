import base64
import functools
import io
from http import HTTPStatus

from flask import url_for
from rq import SimpleWorker

from app.app import q
from app.document import Document, Status
# noinspection PyUnresolvedReferences
from .fixture import *

simple1 = open('app/test/simple1.pdf', 'br').read()
simple2 = open('app/test/simple2.pdf', 'rb').read()


def test_empty_db(client):
    data = {'file': (io.BytesIO(simple1), 'simple1.pdf')}
    with app.app_context():
        response = client.post(
            url_for('document_add'), data=data,
            content_type='multipart/form-data'
        )
    assert response.status_code == HTTPStatus.OK
    assert {'document_id': 1, 'status': 'PROCESSING'} == response.json

    document = Document.get_document(1)
    assert document
    assert simple1 == base64.b64decode(document.body)

    status_res = Document.find_ids_with_status(Status.PROCESSING)
    assert [1] == sorted(status_res)
    list_res = Document.list()
    assert [1] == sorted(list_res)

    jobs = q.get_jobs()
    assert 1 == len(jobs)
    assert jobs[0].func_name == 'app.task.process_document'


def test_document_processing(client):
    with app.app_context():
        load_file = functools.partial(
            client.post, url_for('document_add'), content_type='multipart/form-data'
        )

    data = {'file': (io.BytesIO(simple1), 'simple1.pdf')}
    response = load_file(data=data)
    assert response.status_code == HTTPStatus.OK
    assert {'document_id': 1, 'status': 'PROCESSING'} == response.json

    data = {'file': (io.BytesIO(simple2), 'simple2.pdf')}
    response = load_file(data=data)
    assert response.status_code == HTTPStatus.OK
    assert {'document_id': 2, 'status': 'PROCESSING'} == response.json

    data = {'file': (io.BytesIO(open('app/test/simple3.pdf', 'rb').read()), 'simple3.pdf')}
    response = load_file(data=data)
    assert response.status_code == HTTPStatus.OK
    assert {'document_id': 3, 'status': 'PROCESSING'} == response.json

    data = {'file': (io.BytesIO(simple1), 'simple1.pdf')}
    response = load_file(data=data)
    assert response.status_code == HTTPStatus.OK
    assert {'document_id': 4, 'status': 'PROCESSING'} == response.json

    worker = SimpleWorker([q], connection=q.connection)
    worker.work(burst=True)

    res = Document.documents_with_keyword('Text1')
    assert len(res) == 3
    assert res[0].doc_id == 3
    assert res[0].score == 3.0

    doc = Document.get_document(1)
    assert doc.keywords == {'Text1': 1, 'Text2': 1, 'Text3': 1}
    assert doc.status == Status.PROCESSED.value
