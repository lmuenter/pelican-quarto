import os
from pathlib import Path
from tempfile import TemporaryDirectory
from bs4 import BeautifulSoup
import pytest
from unittest.mock import patch, MagicMock

from pelican import Pelican
from pelican.settings import read_settings

TESTFILE_NAME = "testqmd"


@pytest.fixture
def temp_path():
    """Create temp path for tests."""
    with TemporaryDirectory() as tempdir:
        yield os.path.abspath(tempdir)


@pytest.fixture
def create_article(temp_path):
    """Create dummy qmd report in content dir."""
    content_dir = Path(temp_path) / "content"
    content_dir.mkdir(parents=True, exist_ok=True)

    article_content = """
---
title: testqmd
date: 2024-06-02
category: test
---
Hi

"""
    article_path = content_dir / f"{TESTFILE_NAME}.qmd"
    article_path.write_text(article_content)
    return article_path

def test_plugin_functionality(create_article, temp_path):
    """Test basic plugin functionality: Header extraction."""

    script_dir = Path(__file__).parent

    # Load the mock HTML content from quarto_test_output.html
    with open(script_dir / "test_data" / "quarto_test_output.html", "r", encoding="utf-8") as f:
        mock_html_content = f.read()

    print(mock_html_content)

    # Mock the QuartoHTML class to return a mock object with the desired HTML output
    with patch("quarto.quarto.QuartoHTML", autospec=True) as MockQuartoHTML:
        mock_instance = MockQuartoHTML.return_value
        mock_instance.body = mock_html_content
        mock_instance.header_scripts_links = []
        mock_instance.header_styles = []

        with patch.dict('os.environ', {'PATH': ''}):
            path = Path(temp_path)
            output_path = path / "output"
            content_path = path / "content"
            settings = read_settings(
                override={
                    "PATH": content_path,
                    "OUTPUT_PATH": output_path,
                    "PLUGIN_PATHS": ["../"],
                    "PLUGINS": ["quarto"],
                }
            )
            pelican = Pelican(settings=settings)
            pelican.run()

            articles=os.listdir(output_path)
            assert f"{TESTFILE_NAME}.html" in articles, "An article should have been written"

            filepath = output_path / f"{TESTFILE_NAME}.html"
            with open(filepath, "r", encoding="utf-8") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")

            contents=os.listdir(content_path)
            assert "_quarto.yml" in contents, "A quarto config file should have been prepared"

            script_tags = soup.find_all("script")
            link_tags = soup.find_all("link")

            # check if body contains Quarto content
            body = soup.find("body")
            assert body is not None, "The body of the HTML should exist"
            quarto_script = body.find("script", id="quarto-html-after-body")
            assert quarto_script is not None, "Quarto-specific script not found in body"

            assert any("site_lib" in script.get("src", "") for script in script_tags), "No script link to site_lib found in header"
            assert any("site_lib" in link.get("href", "") for link in link_tags), "No link to site_lib found in header"
