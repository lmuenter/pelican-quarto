import logging
from pathlib import Path
import subprocess

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
                return result.stdout
            logger.error(
                f"Error while rendering Quarto Markdown File {filename}: {result.stderr}"
            )
            return result.stderr

        except Exception:
            logger.error("An exception occured while running Quarto: {e}")
