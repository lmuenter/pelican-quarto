import os
from pathlib import Path
from tempfile import TemporaryDirectory

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
    output_path = Path(temp_path) / "output"
    settings = read_settings(
        override={
            "PATH": temp_path,
            "OUTPUT_PATH": output_path,
            "PLUGIN_PATHS": ["../"],
            "PLUGINS": ["quarto"],
        }
    )
    pelican = Pelican(settings=settings)
    pelican.run()

    articles=os.listdir(output_path)

    assert f"{TESTFILE_NAME}.html" in articles
