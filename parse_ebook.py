
# core imports
import argparse

# local
from webook.modules.fanfiction import FanFictionEBook
from webook.modules.wordpress import WordPressEBook

def parse(args):
    if 'fanfiction.net' in args.url:
        ebook = FanFictionEBook(args.url, args.book_file, args.title)
    else:  # assume wordpress
        ebook = WordPressEBook(args.url, args.book_file, args.title)

if __name__ == '__main__':
    example_url = "https://www.fanfiction.net/s/9658524/1/Branches-on-the-Tree-of-Time"

    parser = argparse.ArgumentParser()
    parser.add_argument('url', help=f'url to where the book is located, fx {example_url}')
    parser.add_argument('book_file', help='the file name of final book', default='book.epub')
    parser.add_argument('--title', help='The title of the book, default name is scraped from the website',
                        default=None)
    parser.set_defaults(func=parse)
    args = parser.parse_args()
    parse(args)

