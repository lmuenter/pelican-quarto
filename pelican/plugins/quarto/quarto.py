from datetime import date, datetime
import logging
import re

import markdown
import pytz
import yaml

from pelican import readers, signals
from pelican.contents import Author, Category

logger = logging.getLogger(__name__)


class QuartoReader(readers.BaseReader):
    file_extensions = ["qmd"]

    def read(self, filename):
        """Read QMD Files."""
        with open as file:
            content = file.read()

        # extract yaml header and content body
        _, front_matter, markdown_body = re.split(r"^---\s*$", content, 2, re.MULTILINE)

        metadata = yaml.load(front_matter, Loader=yaml.FullLoader)

        # ensure correct datetime format for date
        metadata["date"] = self.parse_date(metadata["date"])

        if "category" in metadata:
            metadata['category'] = Category(metadata["category"], settings=self.settings)
        if "author" in metadata:
            metadata['author'] = Author(metadata["author"], settings=self.settings)


        html_content = markdown.markdown(markdown_body)
        return html_content, metadata

    def parse_date(self, date_input):
        """Ensure date has timezone information."""
        if isinstance(date_input, datetime):
            return date_input if date_input.tzinfo else date_input.replace(tzinfo=pytz.UTC)
        elif isinstance(date_input, date):
            return datetime(year=date_input.year, month=date_input.month, day=date_input.day, tzinfo=pytz.UTC)
        elif isinstance(date_input, str):
            return datetime.strptime(date_input, "%Y-%m-%d").replace(tzinfo=pytz.UTC)
        else:
            logger.error("Invalid date format or type")
            return None


def add_reader(readers):
    """Add qmd reader to pelican."""
    readers.reader_classes["qmd"] = QuartoReader

def register():
    """Register plugin on readers init."""
    signals.readers_init.connect(add_reader)