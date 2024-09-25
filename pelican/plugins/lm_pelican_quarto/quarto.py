import logging
from pathlib import Path

from bs4 import BeautifulSoup

from pelican import signals
from pelican.generators import ArticlesGenerator

from .adapters import Quarto
from .parsers import QuartoHTML
from .readers import QuartoReader

logger = logging.getLogger(__name__)
QUARTO_EXTENSION = "qmd"


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
