# A Quarto Reader for Pelican

[![Build Status](https://img.shields.io/github/actions/workflow/status/lmuenter/pelican-quarto/main.yml?branch=main)](https://github.com/lmuenter/pelican-quarto/actions)
[![PyPI Version](https://img.shields.io/pypi/v/lm-pelican-quarto)](https://pypi.org/project/lm-pelican-quarto/)
[![Downloads](https://img.shields.io/pypi/dm/lm-pelican-quarto)](https://pypi.org/project/lm-pelican-quarto/)
![License](https://img.shields.io/pypi/l/lm-pelican-quarto?color=blue)

This plugin integrates Quarto with Pelican, allowing you to render interactive reports and high-quality documents directly within your Pelican-generated static website.

## Features

- **Seamless Integration**: Automatically read and render Quarto Markdown (`.qmd`) files found in Pelican's content directory, making it easy to use Quarto with your existing Pelican setup.

- **Interactive Content**: Easily present dynamic and interactive elements like charts, tables, and other visualizations within Pelican pages, enhancing the interactivity and engagement of your content.

- **Quarto Asset Management**: Utilizes Quarto’s asset management system, consolidating JavaScript, stylesheets, and other assets into a single `<output>/site_libs/` directory for efficient loading and maintenance.

## Installation

You can install the Pelican-Quarto plugin using pip:

```bash
pip install lm-pelican-quarto
```

After installation, add `lm_pelican_quarto` to your `PLUGINS` list in your Pelican settings file. For more detailed instructions, refer to the [How to Use Plugins](https://docs.getpelican.com/en/latest/plugins.html#how-to-use-plugins) section in the Pelican documentation.

## Usage

Once integrated, Pelican-Quarto will automatically process Quarto Markdown (`.qmd`) files present in your content directory. During the build process, Pelican will:

1. Use the Quarto CLI to render `.qmd` files into HTML.
2. Generate necessary assets and place them in the `<output>/site_libs/` directory.
3. Merge Quarto-generated HTML into Pelican's HTML structure, ensuring that your site maintains a consistent look and feel.

This seamless process allows you to leverage Quarto's advanced content capabilities with minimal configuration or manual intervention.

## Customization

Pelican-Quarto will generate a `_quarto.yml` configuration file at the root of your content directory. You can customize this file to suit your specific needs. For more details on customization options, please refer to the [Quarto Documentation](https://quarto.org/docs/projects/quarto-projects.html).

### Quarto Pre-configuration

Pelican-Quarto employs a minimalist Quarto setup to simplify integration with Pelican. By default, it uses Quarto’s `Website` project type to minimize additional asset files in your output directory. You are free to experiment with different themes, enable or disable specific Quarto features, and further customize your Quarto environment.

## Dependencies

This plugin requires Quarto to be installed and accessible in your system's PATH. Ensure that you have [downloaded and installed Quarto](https://quarto.org/docs/download/) before using this plugin.

## Current Limitations

Pelican-Quarto is currently under active development. Some planned features include:

- Enhanced customization options via Pelican settings, allowing users to specify more detailed Quarto configurations directly from their Pelican setup.

## Contributing

Contributions to Pelican-Quarto are welcome and greatly appreciated. Whether it’s improving documentation, adding new features, or fixing bugs, every contribution helps. You can also contribute by reviewing and providing feedback on [existing issues][existing issues].

To get started with contributing, please refer to the [Contributing to Pelican][Contributing to Pelican] guide, particularly the **Contributing Code** section.

[existing issues]: https://github.com/lmuenter/pelican-quarto/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html

## License

This project is licensed under the MIT License.
