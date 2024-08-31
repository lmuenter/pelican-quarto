from datetime import date, datetime
import logging
import re
from pathlib import Path
import os
import subprocess

import markdown
import pytz
import yaml

from pelican import readers, signals
from pelican.contents import Author, Category

logger = logging.getLogger(__name__)


class Quarto:
    def __init__(self, path, output_path):
        self.path = Path(path)
        self.output_path = output_path
        self._setup_quarto_project()

    def _setup_quarto_project(self):
        content_dir = self.path / "content"
        quarto_config_path = content_dir / "_quarto.yml"
        content_dir.mkdir(parents=True, exist_ok=True)

        output_dir_abs = self.path / self.output_path

        quarto_config = f"""
project:
  type: website
  output-dir: {output_dir_abs}

format:
  html:
    theme: none
        """
        with open(quarto_config_path, "w") as config_file:
            config_file.write(quarto_config)
        logger.info(f"_quarto.yml created at {quarto_config_path}")


    def run_quarto(self, filename):
        try:
            result = subprocess.run(
                ["quarto", "render", filename, "--output", "-"],
                cwd=str(Path(self.path) / 'content'),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("Quarto render completed successfully.")
                return result.stdout
            else:
                return result

        except Exception as e:
            logger.error("An exception occured while running Quarto: {e}")


class QuartoReader(readers.BaseReader):
    file_extensions = ["qmd"]

    def read(self, filename):
        """Read QMD Files."""

        with open(filename, "r", encoding="utf-8") as file:
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

        quarto = Quarto(self.settings["PATH"], self.settings["OUTPUT_PATH"])
        output = quarto.run_quarto(filename)
        logger.error(f"fffffffffffffffffffffff {output}")

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