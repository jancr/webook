
# core imports
import urllib

# 3rd party imports
from bs4 import BeautifulSoup as Soup

# local imports
from ..webook import EBook


def open_webpage(url):
    """some webpages block the user agent 'python'"""

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
    req = urllib.request.Request(url, headers=hdr)
    return urllib.request.urlopen(req)


class WordPressEBook(EBook):
    """ as there is no standardardized way to parse a wordpress blog into a book
    I will only parse links that are under "Table of contents", if there is no
    table of content, the script will fail
    """

    def find_toc(self, page):
        menu_bar = page.find(id="secondary")

        for header in menu_bar.find_all(['h1', 'h2', 'h3', 'h4']):
            if header.text.lower() == 'table of contents':
                toc_element = header.parent.find('ul')
                break

        #toc = [part, section/arc, chapter]
        toc = []
        for part in toc_element.children:
            part = []
            part_name = ''
            for section in part:
                section = []
                section_name = ''
                part.append(section_name, section)
                for chapter in section:
                    chapter_name = ''
                    link = ''
                    section.append(chapter_name, link)
        return toc
                    
    def scrape(self, url, workers):
        page = Soup(open_webpage(url), 'lxml')
        toc = self.find_toc(page)
        # TODO: make the rest!

    def parse_chapter(self, *args):
        pass

    def parse_part(self, *args):
        pass


