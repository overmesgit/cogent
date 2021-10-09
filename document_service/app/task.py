import io
import re
from collections import Counter

from app.document import Document, Status
from pdfminer.high_level import extract_text
from redis import Redis

redis_con = Redis(host='redis')


def process_document(document: 'Document') -> None:
    try:
        text = extract_text(io.BytesIO(document.decode_body()))
        resp = re.findall(r'\b\w{3,}\b', text)
        document.keywords = dict(Counter(resp))
        document.status = Status.PROCESSED.value
        document.save()
    except Exception as ex:
        print('Exception', ex)
