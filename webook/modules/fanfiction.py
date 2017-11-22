
# core imports
import urllib

# 3rd party imports
from bs4 import BeautifulSoup as Soup

# local imports
from ..webook import EBook

class FanFictionEBook(EBook):
    def scrape(self, url):
        self._u = urllib.parse.urlparse(url)
        print(f"Downloading: {url}")
        page = Soup(urllib.request.urlopen(url), 'lxml')

        # add cover and title
        title_page = page.find('div', {'id': 'profile_top'})
        # TODO: find out how not to be blocked by the CDN :(
        # self.cover_path = 'https:{}'.format(title_page.find('img').attrs['src'])
        # self.cover_path = 'https:{}'.format(page.find('img').attrs['data-original'])
        self.title = title_page.find('b').text
        self.first_name = title_page.find('a').text
        options = page.find('select', {'id': 'chap_select'}).find_all('option')

        self.parse_chapter(page, options[0])
        for option in options[1:]:
            page = self.next_page(page)
            self.parse_chapter(page, option)

    def parse_chapter(self, page, option):
        story_div = page.find('div', {'id': 'storytext'})
        n_chapter, chapter_name = option.text.split('. ')
        self.write_chapter(story_div, n_chapter, chapter_name)
        self.update(f'chapter_{n_chapter}', chapter_name)

    def next_page(self, page):
        next_chapter = page.find_all('button', {'class': 'btn', 'type': 'BUTTON'})[1]
        url = next_chapter.attrs['onclick'].split("'")[1]
        url = f'{self._u.scheme}://{self._u.netloc}{url}'
        print(f"Downloading: {url}")
        return Soup(urllib.request.urlopen(url), 'lxml')


