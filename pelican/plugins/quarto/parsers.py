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


class PelicanHTML:
    """Facade to Pelican HTML Documents."""

    def __init__(self, html_string):
        self.soup = BeautifulSoup(html_string, 'html.parser')
        self.header = self._extract_header()
        self.body = self._extract_body()
        self.footer = self._extract_footer()

    def _extract_header(self):
        header = self.soup.find('head')
        return str(header) if header else ""

    def _extract_body(self):
        body = self.soup.find('body')
        # Optionally remove the footer for isolated body manipulation
        if body:
            footer = body.find('footer')
            if footer:
                footer.extract()
        return str(body) if body else ""

    def _extract_footer(self):
        footer = self.soup.find('footer')
        return str(footer) if footer else ""

    def inject_content(self, html_content, position='end'):
        body = self.soup.find('body')
        if body:
            new_content = BeautifulSoup(html_content, 'html.parser')
            if position == 'end':
                body.append(new_content)
            elif position == 'start':
                body.insert(0, new_content)
            else:
                body.append(new_content)  # Default to end if position is unclear

    def serialize(self):
        """Returns the entire modified HTML as a string."""
        return str(self.soup)