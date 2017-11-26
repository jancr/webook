#!/usr/bin/env python

# core imports
import os
from os.path import join as pjoin
import sys
import hashlib
import time
import tempfile

# Setup for flask
import flask
from flask import render_template, request, send_file, after_this_request

# local imports
from webook.modules.fanfiction import FanFictionEBook
from webook.modules.wordpress import WordPressEBook

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
def get_parser(parser_option):
    if parser_option == 'auto detect':
        raise NotImplemented
    else:
        parser_key = int(parser_option)
        return PARSER_MAPPERS[PARSERS[parser_key]]


################################################################################
# html
################################################################################
@app.route('/')
def index():
    print('test 1')
    return render_template('index.html', parsers=PARSERS)


@app.route('/ebook')
def make_ebook():
    @after_this_request
    def remove_file(response):
        tmp_file.close()
        return response

    book_parser = request.args['parser'] 
    book_url = request.args['url']
    
    tmp_file = tempfile.NamedTemporaryFile(dir=TMP_DIR, suffix='.epub')

    ebook_parser = get_parser(book_parser)
    ebook_parser(book_url, tmp_file.name)

    return send_file(tmp_file.name, mimetype='application/epub+zip')

@app.route('/progress')
def progress():
    raise NotImplemented
    # TODO: 
    #       1. make call back part of the api
    #       2. use the call back here
    #       3. use bootstrap to make it pretty


def runserver(debugging=False, processes=4):
    global DEBUGGING
    DEBUGGING = debugging
    if debugging:
        processes = 1
    app.run(debug=debugging, host='0.0.0.0', port=5555, processes=processes)


if __name__ == '__main__':
    runserver()
