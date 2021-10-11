import io
import logging
from dataclasses import asdict
from http import HTTPStatus

from flask import Flask, request
from rq import Queue

from app.db_connection import redis_con
from app.document import Document, Status
from app.file_format.enabled_formats import FORMAT_TO_PARSER
from app.task import process_document

q = Queue(connection=redis_con)

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route('/document/add', methods=['POST'])
def document_add():
    if 'file' not in request.files or request.files['file'].filename == '':
        logger.info('No file in request.')
        return {'error': 'no file'}, HTTPStatus.BAD_REQUEST

    file = request.files['file']
    file_format = file.filename.split('.')[-1]
    if file_format not in FORMAT_TO_PARSER:
        return {'error': 'wrong file format'}, HTTPStatus.BAD_REQUEST

    buffer = io.BytesIO()
    file.save(buffer)
    parser = FORMAT_TO_PARSER[file_format]()
    if not parser.is_valid_file(buffer.getvalue()):
        return {'error': 'wrong file content'}, HTTPStatus.BAD_REQUEST

    file_base64 = Document.get_encoded_body(buffer.getvalue())
    document = Document(body=file_base64, filename=file.filename)
    document.save()

    logger.info('Send document for processing.')
    q.enqueue(process_document, document)
    return {'document_id': document.id, 'status': Status(document.status).name}


@app.route('/document/')
def document_list():
    documents = Document.list()
    res = []
    for d in documents:
        document_dict = asdict(d)
        document_dict.pop('body')
        document_dict.pop('keywords')
        res.append(document_dict)
    return {'objects': res}


@app.route('/document/find')
def document_find():
    keyword = request.args.get('keyword')
    if not keyword:
        return {'error': "Please enter keyword as url parameter 'keyword'"}
    return {'objects_scores': [r._asdict() for r in Document.get_documents_with_keyword(keyword)]}


if __name__ == '__main__':
    app.run()
