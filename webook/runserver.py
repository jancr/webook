#!/usr/bin/env python

# core imports
import os
from os.path import join as pjoin
import sys
import hashlib
import time
import tempfile
import base64

# Setup for flask
import flask
from flask import render_template, request, send_file, after_this_request, Response
# local imports
from webook.modules import FanFictionEBook, WordPressEBook

app = flask.Flask(__name__, 
        template_folder='static/templates')

################################################################################
# Globals
################################################################################
DEBUGGING = False

# paths
WEBOOK_DIR = os.path.dirname(__file__)
TMP_DIR = pjoin(WEBOOK_DIR, 'tmp')
#  TEMPLATE_DIR = pjoin(WEBOOK_DIR, 'static/templates')

# variables
PARSERS = ('fanfiction.net', 'Wordpress sites')
PARSER_MAPPERS = {'fanfiction.net': FanFictionEBook,
                  'Wordpress sites':WordPressEBook
                 }

################################################################################
# helpers
################################################################################
def get_parser(parser_option, url):
    if parser_option == 'auto detect':
        if 'fanfiction.net' in url:
            return FanFictionEBook
        raise NotImplemented
    else:
        parser_key = int(parser_option)
        return PARSER_MAPPERS[PARSERS[parser_key]]


def cleanup():
    keep = PROCESSES * 2 + 5
    tmp_files = [pjoin(TMP_DIR, f) for f in os.listdir(TMP_DIR) if f.endswith('epub')]
    tmp_files.sort(key=os.path.getctime, reverse=True)
    for old_tmp_file in tmp_files[keep:]:
        try:
            os.unlink(old_tmp_file)
        except:  # if another process deleted it
            pass


################################################################################
# html
################################################################################
@app.route('/')
def index():
    return render_template('index.html', parsers=PARSERS)


@app.route('/download_ebook/<file_name>')
def download_ebook(file_name):
    """This function is called after progress, it simply returns 
    the ebook and deletes it subsequently
    """

    @after_this_request
    def remove_file(response):
        cleanup()
        return response

    tmp_file_name = pjoin(TMP_DIR, file_name)

    return send_file(tmp_file_name, mimetype='application/epub+zip',
                     attachment_filename="book.epub", as_attachment=True)


@app.route('/create_ebook/<parser>/<url>')
def create_ebook(parser, url):
    """this function returns a progress bar while the book is
    being made
    """
    
    def generate(ebook_parser, tmp_file):
        ebook_generator = ebook_parser.run()
        progress = next(ebook_generator)
        total = ebook_parser.total
        yield f"data: {round(100 * progress / total)}\n\n"
        for progress in ebook_generator:
            yield f"data: {round(100 * progress / total)}\n\n"
        # hack: return file name for the next request
        tmp_file = os.path.basename(tmp_file)
        yield f"data: file-name: {tmp_file}\n\n"

    book_parser = base64.b64decode(parser).decode('utf-8')
    book_url = base64.b64decode(url).decode('utf-8')

    tmp_file = tempfile.mkstemp(dir=TMP_DIR, suffix='.epub')[1]
    ebook_parser = get_parser(book_parser, url)
    ebook_parser = ebook_parser(book_url, tmp_file, run=False)
    return Response(generate(ebook_parser, tmp_file), mimetype='text/event-stream')


def runserver(debugging=False, processes=4):
    global DEBUGGING
    global PROCESSES
    if debugging:
        processes=1
    PROCESSES=processes
    DEBUGGING = debugging
    app.run(debug=debugging, host='0.0.0.0', port=5555, processes=processes)


if __name__ == '__main__':
    runserver()

