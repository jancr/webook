
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
                    


    
    #  def parse_links(toc):



    def scrape(self, url, workers):
        page = Soup(open_webpage(url), 'lxml')
        toc = find_toc(page)



        # add cover and title
        title_page = page.find('div', {'id': 'profile_top'})
        # TODO: find out how not to be blocked by the CDN :(
        # self.cover_path = 'https:{}'.format(title_page.find('img').attrs['src'])
        # self.cover_path = 'https:{}'.format(page.find('img').attrs['data-original'])
        self.title = title_page.find('b').text
        self.first_name = title_page.find('a').text

        select = page.find('select', {'id': 'chap_select'})
        if select is not None:  # there are more than 1 chapter
            options = select.find_all('option')
            url_chapters = range(1, len(options)+1)
            self.total = len(url_chapters)
            with futures.ThreadPoolExecutor(max_workers=workers) as executor:
                _exe = executor.map(self.parse_chapter, options, repeat(book_id), url_chapters)
                for self.progress, (file_name, chapter_name) in enumerate(_exe, 1):
                    # update the TOC sequencial so the chapters are in order!
                    self.update(file_name, chapter_name)
                    yield self.progress
        else:  # there is only one chapter
            self.total = 1
            story_div = page.find('div', {'id': 'storytext'})
            self.write_html(story_div, 'short_story', self.title)
            self.update('short_story', self.title)
            yield 1


    def parse_chapter(self, *args):
        pass

    def parse_part(self, *args):
        pass

    def scrape(self):
        pass




# inspiration !!!
# inspiration !!!
# inspiration !!!
# inspiration !!!


# core imports
import urllib
import re
from concurrent import futures
from itertools import repeat


# 3rd party imports
import tqdm
from bs4 import BeautifulSoup as Soup

# local imports
from ..webook import EBook

class FanFictionEBook(EBook):

    def scrape(self, url, workers):
        workers = 5
        book_id = re.search('fanfiction\.net\/s\/(\d+)\/', url).groups()[0]
        page = Soup(urllib.request.urlopen(url), 'lxml')

        # add cover and title
        title_page = page.find('div', {'id': 'profile_top'})
        # TODO: find out how not to be blocked by the CDN :(
        # self.cover_path = 'https:{}'.format(title_page.find('img').attrs['src'])
        # self.cover_path = 'https:{}'.format(page.find('img').attrs['data-original'])
        self.title = title_page.find('b').text
        self.first_name = title_page.find('a').text

        select = page.find('select', {'id': 'chap_select'})
        if select is not None:  # there are more than 1 chapter
            options = select.find_all('option')
            url_chapters = range(1, len(options)+1)
            self.total = len(url_chapters)
            with futures.ThreadPoolExecutor(max_workers=workers) as executor:
                _exe = executor.map(self.parse_chapter, options, repeat(book_id), url_chapters)
                for self.progress, (file_name, chapter_name) in enumerate(_exe, 1):
                    # update the TOC sequencial so the chapters are in order!
                    self.update(file_name, chapter_name)
                    yield self.progress
        else:  # there is only one chapter
            self.total = 1
            story_div = page.find('div', {'id': 'storytext'})
            self.write_html(story_div, 'short_story', self.title)
            self.update('short_story', self.title)
            yield 1


    def parse_chapter(self, option, book_id, n_page):
        url = f"https://www.fanfiction.net/s/{book_id}/{n_page}"
        page = Soup(urllib.request.urlopen(url), 'lxml')
        story_div = page.find('div', {'id': 'storytext'})
        n_chapter, chapter_name = option.text.split('. ')
        file_name = f"chapter_{n_chapter}"
        self.write_html(story_div, file_name, chapter_name)
        return (file_name, chapter_name)
