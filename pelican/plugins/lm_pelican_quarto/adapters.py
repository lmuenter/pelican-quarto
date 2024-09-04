import logging
from pathlib import Path
import subprocess

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Quarto:
    """Adapter Class for establishing and running Quarto."""

    def __init__(self, path, output_path):
        self.path = Path(path)
        self.wdir = self.path.parent
        self.output_dir = output_path
        self.output_path = self.wdir / self.output_dir
        self._setup_quarto_project()

    def _setup_quarto_project(self):
        quarto_config_path = self.path / "_quarto.yml"
        self.path.mkdir(parents=True, exist_ok=True)

        if not quarto_config_path.exists():
            quarto_config = f"""
project:
  type: website
  output-dir: {self.output_path}

format:
  html:
    theme: none
        """
            quarto_config_path.write_text(quarto_config)

    def run_quarto(self, filename):
        """Run Quarto as a subprocess."""
        try:
            result = subprocess.run(
                ["quarto", "render", filename, "--output", "-", "--no-cache"],
                cwd=str(self.path),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                logger.info("Quarto render completed successfully.")
                return self._update_image_references(filename, result.stdout)
            logger.error(
                f"Error while rendering Quarto Markdown File {filename}: {result.stderr}"
            )
        except subprocess.SubprocessError as e:
            logger.error(f"An exception occurred: {e}")
        return None

    def _update_image_references(self, filename, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        updated = False
        base_name = Path(filename).stem
        figure_path = self._get_figure_html_path(filename)

        for img in soup.find_all("img"):
            original_src = img.get("src", "")
            if original_src.startswith(f"{base_name}_files/"):
                new_src = str(figure_path / original_src[len(f"{base_name}_files/") :])
                img["src"] = new_src
                updated = True

        return str(soup) if updated else html_content

    def _get_figure_html_path(self, filename):
        """Calculate path to figure-html for a given .qmd file."""
        file_path = Path(filename)
        base_name = file_path.stem
        relative_path = file_path.relative_to(self.path)
        return relative_path.parent / f"{base_name}_files"
