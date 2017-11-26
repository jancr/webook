#!/usr/bin/env python3
# core imports
import sys
import argparse

# local
from webook.modules.fanfiction import FanFictionEBook
from webook.modules.wordpress import WordPressEBook

def scrape_to_book(url, book_file, title):
    if 'fanfiction.net' in url:
        FanFictionEBook(url, book_file, title)
    else:  # assume wordpress
        WordPressEBook(url, book_file, title)


def run():
    example_url = "https://www.fanfiction.net/s/9658524/1/Branches-on-the-Tree-of-Time"
    if '--webserver' in sys.argv:
        from . import runserver
        runserver.runserver('--debug' in sys.argv)
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument('url', help=f'url to where the book is located, fx {example_url}')
        parser.add_argument('book_file', help='the file name of final book', default='book.epub')
        parser.add_argument('--title', default=None, 
                help='The title of the book, default name is scraped from the website')
        parser.set_defaults(func=scrape_to_book)
        args = parser.parse_args()
        args.func(args.url, args.book_file, args.title)


if __name__ == '__main__':
    run()
