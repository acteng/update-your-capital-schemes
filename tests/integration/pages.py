from bs4 import BeautifulSoup


class LandingPage:
    def __init__(self, html: str):
        self._soup = BeautifulSoup(html, "html.parser")
        self.header = self._soup.h1 and self._soup.h1.string
