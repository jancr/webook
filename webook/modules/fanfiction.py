
# core imports
import urllib
import re
from concurrent import futures
from itertools import repeat
import time


# 3rd party imports
import tqdm
from bs4 import BeautifulSoup as Soup

# local imports
from ..webook import EBook


class FanFictionEBook(EBook):
    def scrape(self, url, workers):
        _re = 'fanfiction\.net\/s\/(\d+)\/\d+/(.+)'
        self.book_id, self.slug = re.search(_re, url).groups()
        page = Soup(urllib.request.urlopen(url), 'lxml')

        # CDN blocks referes != fanfiction.net :(
        cover_path = 'https:{}'.format(page.find('img').attrs['data-original'])
        self.cover = urllib.request.Request(cover_path, headers={'referer': url})

        title_page = page.find('div', {'id': 'profile_top'})
        self.title = title_page.find('b').text
        self.first_name = title_page.find('a').text

        select = page.find('select', {'id': 'chap_select'})
        if select is not None:  # there are more than 1 chapter
            options = select.find_all('option')
            url_chapters = range(1, len(options)+1)
            self.total = len(url_chapters)
            #  with futures.ThreadPoolExecutor(max_workers=workers) as executor:
            #      _exe = executor.map(self.parse_chapter, options, url_chapters)
            #      for self.progress, (file_name, chapter_name) in enumerate(_exe, 1):
            #          # update the TOC sequencial so the chapters are in order!
            #          self.update(file_name, chapter_name)
            #          yield self.progress
            _iter = enumerate(zip(options, url_chapters), 1)
            for self.progress, (option, url_chapter) in _iter:
                time.sleep(5)
                file_name, chapter_name = self.parse_chapter(option, url_chapter)
                # update the TOC sequencial so the chapters are in order!
                self.update(file_name, chapter_name)
                yield self.progress
        else:  # there is only one chapter
            self.total = 1
            story_div = page.find('div', {'id': 'storytext'})
            self.write_html(story_div, 'short_story', self.title)
            self.update('short_story', self.title)
            yield 1


    def parse_chapter(self, option, n_page):
        url = f"https://www.fanfiction.net/s/{self.book_id}/{n_page}/{self.slug}"
        page = Soup(urllib.request.urlopen(url), 'lxml')
        story_div = page.find('div', {'id': 'storytext'})
        if story_div is None:
            import ipdb; ipdb.set_trace()  # noqa
            raise IOError("Bad Page")
        n_chapter, chapter_name = option.text.split('. ')
        file_name = f"chapter_{n_chapter}"
        self.write_html(story_div, file_name, chapter_name)
        return (file_name, chapter_name)
