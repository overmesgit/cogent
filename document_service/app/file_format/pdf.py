import io
import logging
import re

from pdfminer.high_level import extract_text, extract_pages

from app.file_format.base import BaseFileProcessor

logger = logging.getLogger(__name__)


class PdfProcessor(BaseFileProcessor):
    file_format = 'pdf'

    def get_file_text(self, file_data):
        text = extract_text(io.BytesIO(file_data))
        return re.findall(r'\b\w{3,}\b', text)

    def is_valid_file(self, file_data):
        try:
            return bool(list(extract_pages(io.BytesIO(file_data), maxpages=3)))
        except Exception as ex:
            logger.error('ProcessDocumentError %s', ex)
            return False
