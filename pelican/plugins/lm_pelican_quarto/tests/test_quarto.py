import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from bs4 import BeautifulSoup
import pytest

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
date: "2024-06-02"
category: "test"
tags: ["arts", "b"]
---
Hi

``` {r}
library(ggplot2)
data = data.frame(
    X=c(1),
    Y=c(2)
)

ggplot(data=data, aes(x=X,y=Y)) +
    geom_point()
```

"""
    article_path = content_dir / f"{TESTFILE_NAME}.qmd"
    article_path.write_text(article_content)
    return article_path


@pytest.fixture
def create_nested_article(temp_path):
    """Create dummy qmd report in content dir."""
    content_dir = Path(temp_path) / "content" / "test"
    content_dir.mkdir(parents=True, exist_ok=True)

    article_content = """
---
title: "testqmd"
date: "2024-06-02"
category: "test"
tags: ["a", "b"]
---
Hi

``` {r}
library(ggplot2)
data = data.frame(
    X=c(1),
    Y=c(2)
)

ggplot(data=data, aes(x=X,y=Y)) +
    geom_point()
```

"""
    article_path = content_dir / f"{TESTFILE_NAME}.qmd"
    article_path.write_text(article_content)
    return article_path


@pytest.fixture
def quarto_run_mock():
    with patch("subprocess.run") as mock_run:
        script_dir = Path(__file__).parent

        with open(
            script_dir / "test_data" / "quarto_test_output.html", encoding="utf-8"
        ) as f:
            mock_html_content = f.read()
        mock_run.return_value.stdout = mock_html_content
        mock_run.return_value.returncode = 0
        yield mock_run


def test_plugin_functionality(create_article, temp_path, quarto_run_mock):
    """Test basic plugin functionality: Header extraction."""
    path = Path(temp_path)
    output_path = path / "output"
    content_path = path / "content"
    settings = read_settings(
        override={
            "PATH": content_path,
            "OUTPUT_PATH": output_path,
            "PLUGIN_PATHS": ["../"],
            "PLUGINS": ["lm_pelican_quarto"],
        }
    )
    pelican = Pelican(settings=settings)
    pelican.run()

    articles = os.listdir(output_path)
    assert f"{TESTFILE_NAME}.html" in articles, "An article should have been written"

    filepath = output_path / f"{TESTFILE_NAME}.html"
    with open(filepath, encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    assert soup.find("body") is not None, "The body of the HTML should exist"
    quarto_script = soup.find("script", id="quarto-html-after-body")
    assert quarto_script is not None, "Quarto-specific script not found in body"


def test_figure_html_path_correction(create_nested_article, temp_path, quarto_run_mock):
    """Test image path correction when nested dirs are present."""
    path = Path(temp_path)
    output_path = path / "output"
    content_path = path / "content"
    settings = read_settings(
        override={
            "PATH": content_path,
            "OUTPUT_PATH": output_path,
            "PLUGIN_PATHS": ["../"],
            "PLUGINS": ["lm_pelican_quarto"],
        }
    )
    pelican = Pelican(settings=settings)
    pelican.run()

    articles = os.listdir(output_path)
    assert f"{TESTFILE_NAME}.html" in articles, "An article should have been written"

    filepath = output_path / f"{TESTFILE_NAME}.html"
    with open(filepath, encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    for img in soup.find_all("img"):
        src = img.get("src", "")
        assert src.startswith(f"test/{TESTFILE_NAME}_files/")
