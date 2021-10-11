import base64
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from typing import NamedTuple

from app.db_connection import redis_con

logger = logging.getLogger(__name__)


class Status(Enum):
    PROCESSING = auto()
    PROCESSED = auto()


@dataclass
class Document:
    filename: str
    body: str = ''
    status: Status = Status.PROCESSING.value
    added_time: int = field(default_factory=lambda: datetime.now().timestamp())
    keywords: dict = field(default_factory=dict)
    processing_error: str = ''
    id: str = None

    class Meta:
        KEY_PREFIX = 'DOCUMENT'
        STATUS_INDEX = 'status'
        KEYWORD_INDEX = 'keyword'

    @staticmethod
    def get_key(doc_id):
        return f'{Document.Meta.KEY_PREFIX}_{doc_id}'

    @staticmethod
    def get_keyword_index(keyword):
        return f'{Document.Meta.KEYWORD_INDEX}_{keyword}'

    def save(self):
        logger.info(f'Save document {self.id=}')
        if self.id is None:
            document_id = redis_con.incr('counter')
            self.id = document_id

        redis_con.zadd(self.Meta.STATUS_INDEX, {self.id: self.status})
        if self.keywords:
            logger.info(f'Update document keywords indexes {self.id=}')
            self.status = Status.PROCESSED.value
            for kw, rank in self.keywords.items():
                redis_con.zadd(self.get_keyword_index(kw), {self.id: rank})

        redis_con.set(self.get_key(self.id), json.dumps(asdict(self)))
        return self

    def decode_body(self):
        return base64.b64decode(self.body)

    @staticmethod
    def get_encoded_body(data):
        return base64.b64encode(data).decode()

    @staticmethod
    def get_document(document_id):
        resp = redis_con.get(Document.get_key(document_id))
        if resp:
            return Document(**json.loads(resp))
        else:
            return None

    @staticmethod
    def list_keys():
        prefix = Document.Meta.KEY_PREFIX
        keys = list(redis_con.scan_iter(f'{prefix}_*'))
        return [int(k.decode().removeprefix(prefix + '_')) for k in keys]

    @staticmethod
    def list():
        keys = list(redis_con.scan_iter(f'{Document.Meta.KEY_PREFIX}_*'))
        return [Document(**json.loads(r)) for r in redis_con.mget(keys)]

    @staticmethod
    def find_ids_with_status(status: Status):
        res = []
        for doc_id in redis_con.zrangebyscore(
                Document.Meta.STATUS_INDEX,
                min=status.value, max=status.value
        ):
            res.append(int(doc_id))
        return res

    @staticmethod
    def get_documents_with_keyword(keyword):
        res_tuple = NamedTuple("SearchResult", (('doc_id', int), ('score', float)))
        res = []
        for doc_id, score in redis_con.zrevrangebyscore(
                Document.get_keyword_index(keyword),
                min='-inf', max='+inf',
                start=0, num=3,
                withscores=True
        ):
            res.append(res_tuple(int(doc_id), score))
        return res
