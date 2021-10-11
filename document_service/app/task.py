import logging
from collections import Counter

from app.document import Document
from app.file_format.enabled_formats import FORMAT_TO_PARSER

logger = logging.getLogger(__name__)


def process_document(document: 'Document') -> None:
    try:
        file_format = document.filename.split('.')[-1]
        parser = FORMAT_TO_PARSER[file_format]()

        file_body = document.decode_body()
        document.keywords = dict(Counter(parser.get_file_text(file_body)))
        document.save()
    except Exception as ex:
        logger.error('ProcessDocumentError %s', ex)
        document.error = str(ex)
        document.save()
