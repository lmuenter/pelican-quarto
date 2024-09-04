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
        self.output_path = output_path
        self._setup_quarto_project()

    def _setup_quarto_project(self):
        content_dir = self.path
        quarto_config_path = content_dir / "_quarto.yml"
        content_dir.mkdir(parents=True, exist_ok=True)

        if quarto_config_path.exists():
            logger.info(
                f"_quarto.yml already exists at {quarto_config_path}, skipping setup."
            )
            return

        output_dir_abs = self.wdir / self.output_path

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
                cwd=str(Path(self.wdir) / "content"),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                logger.info("Quarto render completed successfully.")
                quarto_html = result.stdout
                updated_html = self._update_image_references(filename, quarto_html)
                return updated_html
            logger.error(
                f"Error while rendering Quarto Markdown File {filename}: {result.stderr}"
            )
            return result.stderr

        except Exception:
            logger.error("An exception occured while running Quarto: {e}")

    def _update_image_references(self, filename, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        updated = False
        base_name = Path(filename).stem
        figure_path = self._get_figure_html_path(filename)

        for img in soup.find_all("img"):
            original_src = img.get("src", "")
            if original_src.startswith(f"{base_name}_files/"):
                new_src = str(figure_path / original_src[len(f"{base_name}_files/"):])
                img['src'] = new_src
                updated = True

        if updated:
            return str(soup)
        return html_content

    def _get_figure_html_path(self, filename):
        """ Calculate path to figure-html for a given .qmd file. """
        file_path = Path(filename)
        base_name = file_path.stem
        relative_path = file_path.relative_to(self.path)
        return relative_path.parent / f"{base_name}_files"
