
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
