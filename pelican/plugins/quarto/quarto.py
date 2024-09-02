from datetime import date, datetime
import logging
from pathlib import Path
import re

from bs4 import BeautifulSoup
import markdown
import pytz
import yaml

from pelican import readers, signals
from pelican.contents import Author, Category
from pelican.generators import ArticlesGenerator

from .adapters import Quarto
from .parsers import QuartoHTML

logger = logging.getLogger(__name__)
QUARTO_EXTENSION = "qmd"


class QuartoReader(readers.BaseReader):
    """Read QMD Files using a Pelican Reader."""

    file_extensions = [QUARTO_EXTENSION]

    def read(self, filename):
        """Read QMD Files."""
        with open(filename, encoding="utf-8") as file:
            content = file.read()

        # extract yaml header and content body
        _, front_matter, markdown_body = re.split(r"^---\s*$", content, 2, re.MULTILINE)

        metadata = yaml.load(front_matter, Loader=yaml.FullLoader)

        # ensure correct datetime format for date
        metadata["date"] = self.parse_date(metadata["date"])

        if "category" in metadata:
            metadata["category"] = Category(
                metadata["category"], settings=self.settings
            )
        if "author" in metadata:
            metadata["author"] = Author(metadata["author"], settings=self.settings)

        article_content = markdown.markdown(markdown_body)
        metadata["summary"] = self.generate_article_summary(
            metadata.get("summary"), article_content
        )
        return article_content, metadata

    def parse_date(self, date_input):
        """Ensure date has timezone information."""
        if isinstance(date_input, datetime):
            return (
                date_input if date_input.tzinfo else date_input.replace(tzinfo=pytz.UTC)
            )
        if isinstance(date_input, date):
            return datetime(
                year=date_input.year,
                month=date_input.month,
                day=date_input.day,
                tzinfo=pytz.UTC,
            )
        if isinstance(date_input, str):
            return datetime.strptime(date_input, "%Y-%m-%d").replace(tzinfo=pytz.UTC)
        logger.error("Invalid date format or type")
        return None

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


def setup_quarto_project(pelican_instance):
    """Set up the Quarto project if a .qmd file is found."""
    content_path = Path(pelican_instance.settings["PATH"])
    output_path = pelican_instance.settings["OUTPUT_PATH"]

    # check for .qmd files in the content directory
    qmd_files_present = any(content_path.glob(f"**/*.{QUARTO_EXTENSION}"))

    if qmd_files_present:
        quarto = Quarto(content_path, output_path)
        quarto._setup_quarto_project()


def inject_quarto_content(generators):
    """Inject quarto content into the generated article."""
    for generator in generators:
        if isinstance(generator, ArticlesGenerator):
            process_articles(generator)


def process_articles(generator):
    """Process articles within a given ArticlesGenerator."""
    for article in generator.articles:
        if article.source_path.endswith(".qmd"):
            try:
                quarto = Quarto(
                    article.settings["PATH"], article.settings["OUTPUT_PATH"]
                )
                quarto_html_string = quarto.run_quarto(article.source_path)
                quarto_html = QuartoHTML(quarto_html_string)
                soup = BeautifulSoup(quarto_html.body, "html.parser")

                # remove Quarto block header
                title_block_header = soup.find("header", id="title-block-header")
                if title_block_header:
                    title_block_header.decompose()

                body_contents = soup.body
                if body_contents:
                    combined_content = "".join(
                        str(element) for element in body_contents.contents
                    )
                    combined_content += "".join(quarto_html.header_scripts_links)
                    combined_content += "".join(quarto_html.header_styles)
                    article._content = combined_content
                else:
                    article._content = str(soup)

            except Exception as e:
                logger.error(
                    f"Error processing Quarto content for {article.source_path}: {e}"
                )


def add_reader(readers):
    """Add qmd reader to pelican."""
    readers.reader_classes["qmd"] = QuartoReader


def register():
    """Register plugin."""
    signals.initialized.connect(setup_quarto_project)
    signals.readers_init.connect(add_reader)
    signals.all_generators_finalized.connect(inject_quarto_content)
