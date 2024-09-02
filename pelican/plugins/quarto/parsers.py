from bs4 import BeautifulSoup


class QuartoHTML:
    """Facade to Quarto HTML Documents."""

    def __init__(self, html_string):
        self.soup = BeautifulSoup(html_string, "html.parser")
        self.header = self._extract_header()
        self.body = self._extract_body()
        self.header_scripts_links = self._extract_header_scripts_links()
        self.header_styles = self._extract_header_styles()

    def _extract_header(self):
        header = self.soup.find("head")
        return str(header) if header else ""

    def _extract_header_scripts_links(self):
        """Extract <script> and <link> tags from the <head>."""
        header_soup = BeautifulSoup(self.header, "html.parser")
        scripts_and_links = header_soup.find_all(["script", "link"])
        return [str(element) for element in scripts_and_links]

    def _extract_header_styles(self):
        """Extract <script> and <link> tags from the <head>."""
        header_soup = BeautifulSoup(self.header, "html.parser")
        styles = header_soup.find_all(["style"])
        return [str(element) for element in styles]

    def _extract_body(self):
        body = self.soup.find("body")
        return str(body) if body else ""
