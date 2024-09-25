import logging
import re

from bs4 import BeautifulSoup
import markdown
import yaml

from pelican import readers

logger = logging.getLogger(__name__)
QUARTO_EXTENSION = "qmd"


class QuartoReader(readers.BaseReader):
    """Read QMD Files using a Pelican Reader."""

    enabled = True
    file_extensions = [QUARTO_EXTENSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._source_path = None

    def read(self, filename):
        """Read QMD Files."""
        with open(filename, encoding="utf-8") as file:
            content = file.read()

        # extract yaml header and content body
        _, front_matter, markdown_body = re.split(r"^---\s*$", content, 2, re.MULTILINE)

        metadata = yaml.load(front_matter, Loader=yaml.FullLoader)
        metadata = self._parse_metadata(metadata)

        article_content = markdown.markdown(markdown_body)
        metadata["summary"] = self.generate_article_summary(
            metadata.get("summary"), article_content
        )

        return article_content, metadata

    def _parse_metadata(self, meta):
        """Parse and format the metadata from YAML."""
        output = {}
        for name, value in meta.items():
            key = name.lower()
            output[key] = self.process_metadata(key, value)

        return output

    def generate_article_summary(self, existing_summary, content):
        """Generate a summary if one does not exist."""
        if existing_summary:
            return existing_summary

        # strip code blocks
        content_no_code = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        html_content = markdown.markdown(content_no_code)

        soup = BeautifulSoup(html_content, "html.parser")

        max_paragraphs = self.settings.get("SUMMARY_MAX_PARAGRAPHS", None)
        if max_paragraphs is not None:
            paragraphs = soup.find_all("p")[:max_paragraphs]
            html_content = "".join(str(p) for p in paragraphs)
            soup = BeautifulSoup(html_content, "html.parser")

        max_length = self.settings.get("SUMMARY_MAX_LENGTH", None)
        end_suffix = self.settings.get("SUMMARY_END_SUFFIX", "...")

        text_content = soup.get_text()
        if max_length is not None:
            words = text_content.split()
            if len(words) > max_length:
                text_content = " ".join(words[:max_length]) + end_suffix

        return text_content
